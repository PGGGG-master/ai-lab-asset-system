from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config import MAX_UPLOAD_SIZE, UPLOAD_DIR
from app.database import get_db
from app.deps import get_current_user, get_client_ip
from app.models import Asset, User
from app.schemas import AssetOut, AssetUpdate
from app.services.asset_files import (
    ASSET_TYPE_EXTENSIONS,
    build_stored_filename,
    download_filename,
    file_rules_payload,
    guess_media_type,
    is_previewable,
    read_preview_content,
    validate_file_for_type,
)
from app.services.logging import write_log
from app.services.rbac import check_asset_type_access, require_permission

router = APIRouter(prefix="/api/assets", tags=["资产管理"])

ASSET_TYPES = list(ASSET_TYPE_EXTENSIONS.keys())


def _asset_out(asset: Asset) -> AssetOut:
    ext = Path(asset.file_path).suffix.lower()
    return AssetOut(
        id=asset.id,
        name=asset.name,
        asset_type=asset.asset_type,
        description=asset.description,
        owner_id=asset.owner_id,
        owner_name=asset.owner.username if asset.owner else None,
        created_at=asset.created_at,
        updated_at=asset.updated_at,
        file_ext=ext,
        previewable=is_previewable(asset.asset_type),
    )


@router.get("", response_model=list[AssetOut])
def list_assets(
    request: Request,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    ip = get_client_ip(request)
    require_permission(db, current, "asset:read", ip=ip)
    assets = db.query(Asset).order_by(Asset.updated_at.desc()).all()
    return [_asset_out(a) for a in assets]


@router.get("/meta/types")
def asset_types_list(current: User = Depends(get_current_user)):
    return ASSET_TYPES


@router.get("/meta/file-rules")
def asset_file_rules(current: User = Depends(get_current_user)):
    return file_rules_payload()


@router.get("/{asset_id}/preview")
def preview_asset(
    asset_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    ip = get_client_ip(request)
    require_permission(db, current, "asset:read", ip=ip)
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在")
    if not is_previewable(asset.asset_type):
        raise HTTPException(status_code=400, detail="该类型资产不支持预览，请下载查看")
    path = Path(asset.file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    content = read_preview_content(path)
    return {"id": asset.id, "name": asset.name, "content": content}


@router.get("/{asset_id}/download")
def download_asset(
    asset_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    ip = get_client_ip(request)
    require_permission(db, current, "asset:download", ip=ip, target_type="asset", target_id=str(asset_id))
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在")
    path = Path(asset.file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    filename = download_filename(asset.name, asset.file_path)
    write_log(db, user_id=current.id, action="DOWNLOAD", target_type="asset", target_id=str(asset_id), result="成功", detail=asset.name, ip=ip)
    return FileResponse(path, filename=filename, media_type=guess_media_type(filename))


@router.post("/upload", response_model=AssetOut)
async def upload_asset(
    request: Request,
    name: str = Form(...),
    asset_type: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    ip = get_client_ip(request)
    require_permission(db, current, "asset:upload", ip=ip)
    if asset_type not in ASSET_TYPES:
        raise HTTPException(status_code=400, detail=f"资产类型无效，可选: {', '.join(ASSET_TYPES)}")
    ext = validate_file_for_type(file, asset_type)
    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail=f"文件大小超过限制 ({MAX_UPLOAD_SIZE // 1024 // 1024}MB)")
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_path = UPLOAD_DIR / build_stored_filename(ext)
    file_path.write_bytes(content)
    asset = Asset(
        name=name,
        asset_type=asset_type,
        file_path=str(file_path),
        owner_id=current.id,
        description=description or None,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    write_log(db, user_id=current.id, action="UPLOAD", target_type="asset", target_id=str(asset.id), result="成功", detail=name, ip=ip)
    return _asset_out(asset)


@router.put("/{asset_id}", response_model=AssetOut)
def update_asset_meta(
    asset_id: int,
    body: AssetUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    ip = get_client_ip(request)
    require_permission(db, current, "asset:update", ip=ip, target_type="asset", target_id=str(asset_id))
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在")
    check_asset_type_access(db, current, asset.asset_type, "UPDATE_ASSET", ip=ip, asset_id=asset_id)
    if body.asset_type is not None:
        if body.asset_type not in ASSET_TYPES:
            raise HTTPException(status_code=400, detail="资产类型无效")
        check_asset_type_access(db, current, body.asset_type, "UPDATE_ASSET", ip=ip, asset_id=asset_id)
        asset.asset_type = body.asset_type
    if body.name is not None:
        asset.name = body.name
    if body.description is not None:
        asset.description = body.description
    db.commit()
    db.refresh(asset)
    write_log(db, user_id=current.id, action="UPDATE", target_type="asset", target_id=str(asset_id), result="成功", detail=asset.name, ip=ip)
    return _asset_out(asset)


@router.put("/{asset_id}/file", response_model=AssetOut)
async def update_asset_file(
    asset_id: int,
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    ip = get_client_ip(request)
    require_permission(db, current, "asset:update", ip=ip, target_type="asset", target_id=str(asset_id))
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在")
    check_asset_type_access(db, current, asset.asset_type, "UPDATE_ASSET", ip=ip, asset_id=asset_id)
    ext = validate_file_for_type(file, asset.asset_type)
    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="文件大小超过限制")
    old_path = Path(asset.file_path)
    new_path = UPLOAD_DIR / build_stored_filename(ext)
    new_path.write_bytes(content)
    if old_path.exists() and old_path != new_path:
        old_path.unlink()
    asset.file_path = str(new_path)
    db.commit()
    db.refresh(asset)
    write_log(db, user_id=current.id, action="UPDATE_FILE", target_type="asset", target_id=str(asset_id), result="成功", ip=ip)
    return _asset_out(asset)


@router.delete("/{asset_id}")
def delete_asset(
    asset_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    ip = get_client_ip(request)
    require_permission(db, current, "asset:delete", ip=ip, target_type="asset", target_id=str(asset_id))
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在")
    check_asset_type_access(db, current, asset.asset_type, "DELETE_ASSET", ip=ip, asset_id=asset_id)
    path = Path(asset.file_path)
    if path.exists():
        path.unlink()
    name = asset.name
    db.delete(asset)
    db.commit()
    write_log(db, user_id=current.id, action="DELETE", target_type="asset", target_id=str(asset_id), result="成功", detail=name, ip=ip)
    return {"message": "删除成功"}
