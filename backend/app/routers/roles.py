from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, get_client_ip
from app.models import Role, Permission, RolePermission, User
from app.schemas import RoleCreate, RoleOut, RolePermissionAssign, PermissionOut
from app.services.logging import write_log
from app.services.rbac import require_permission

router = APIRouter(prefix="/api", tags=["角色权限"])


def _role_out(role: Role) -> RoleOut:
    return RoleOut(
        id=role.id,
        role_name=role.role_name,
        description=role.description,
        permissions=[p.permission_code for p in role.permissions],
    )


@router.get("/roles", response_model=list[RoleOut])
def list_roles(
    request: Request,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    ip = get_client_ip(request)
    require_permission(db, current, "role:manage", ip=ip)
    return [_role_out(r) for r in db.query(Role).all()]


@router.post("/roles", response_model=RoleOut)
def create_role(
    body: RoleCreate,
    request: Request,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    ip = get_client_ip(request)
    require_permission(db, current, "role:manage", ip=ip)
    if db.query(Role).filter(Role.role_name == body.role_name).first():
        raise HTTPException(status_code=400, detail="角色名已存在")
    role = Role(role_name=body.role_name, description=body.description)
    db.add(role)
    db.commit()
    db.refresh(role)
    write_log(db, user_id=current.id, action="CREATE_ROLE", target_type="role", target_id=str(role.id), result="成功", ip=ip)
    return _role_out(role)


@router.delete("/roles/{role_id}")
def delete_role(
    role_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    ip = get_client_ip(request)
    require_permission(db, current, "role:manage", ip=ip)
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    db.delete(role)
    db.commit()
    write_log(db, user_id=current.id, action="DELETE_ROLE", target_type="role", target_id=str(role_id), result="成功", ip=ip)
    return {"message": "删除成功"}


@router.put("/roles/{role_id}/permissions", response_model=RoleOut)
def assign_permissions(
    role_id: int,
    body: RolePermissionAssign,
    request: Request,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    ip = get_client_ip(request)
    require_permission(db, current, "permission:manage", ip=ip)
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    db.query(RolePermission).filter(RolePermission.role_id == role_id).delete()
    for pid in body.permission_ids:
        if db.query(Permission).filter(Permission.id == pid).first():
            db.add(RolePermission(role_id=role_id, permission_id=pid))
    db.commit()
    db.refresh(role)
    write_log(db, user_id=current.id, action="ASSIGN_PERMISSIONS", target_type="role", target_id=str(role_id), result="成功", ip=ip)
    return _role_out(role)


@router.get("/permissions", response_model=list[PermissionOut])
def list_permissions(
    request: Request,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    ip = get_client_ip(request)
    require_permission(db, current, "permission:manage", ip=ip)
    return db.query(Permission).all()
