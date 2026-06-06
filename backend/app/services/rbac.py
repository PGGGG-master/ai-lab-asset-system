from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import User
from app.services.logging import write_log

ASSET_TYPE_MODEL = "模型资产"
ASSET_TYPE_DATASET = "数据集"


def get_user_permissions(db: Session, user_id: int) -> set[str]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return set()
    perms: set[str] = set()
    for role in user.roles:
        for perm in role.permissions:
            perms.add(perm.permission_code)
    return perms


def get_user_roles(db: Session, user_id: int) -> list[str]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []
    return [r.role_name for r in user.roles]


def require_permission(
    db: Session,
    user: User,
    permission_code: str,
    ip: str | None = None,
    target_type: str | None = None,
    target_id: str | None = None,
) -> None:
    perms = get_user_permissions(db, user.id)
    if permission_code not in perms:
        write_log(
            db,
            user_id=user.id,
            action="DENY",
            target_type=target_type or "permission",
            target_id=target_id or permission_code,
            result="失败",
            detail=f"权限不足: 需要 {permission_code}",
            ip=ip,
        )
        raise HTTPException(status_code=403, detail=f"权限不足: 需要 {permission_code}")


def check_asset_type_access(
    db: Session,
    user: User,
    asset_type: str,
    action: str,
    ip: str | None = None,
    asset_id: int | None = None,
) -> None:
    perms = get_user_permissions(db, user.id)

    if "user:manage" in perms:
        return

    if "model:manage" in perms and "dataset:manage" in perms:
        return

    if "model:manage" in perms and "dataset:manage" not in perms:
        if asset_type != ASSET_TYPE_MODEL:
            write_log(
                db,
                user_id=user.id,
                action=action,
                target_type="asset",
                target_id=str(asset_id) if asset_id else asset_type,
                result="失败",
                detail="模型管理员只能操作模型资产",
                ip=ip,
            )
            raise HTTPException(status_code=403, detail="模型管理员只能管理模型资产")

    if "dataset:manage" in perms and "model:manage" not in perms:
        if asset_type != ASSET_TYPE_DATASET:
            write_log(
                db,
                user_id=user.id,
                action=action,
                target_type="asset",
                target_id=str(asset_id) if asset_id else asset_type,
                result="失败",
                detail="数据管理员只能操作数据集",
                ip=ip,
            )
            raise HTTPException(status_code=403, detail="数据管理员只能管理数据集资产")
