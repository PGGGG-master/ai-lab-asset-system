from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.auth import hash_password
from app.database import get_db
from app.deps import get_current_user, get_client_ip
from app.models import User, Role, UserRole
from app.schemas import UserCreate, UserOut, UserUpdate, RoleAssign
from app.services.logging import write_log
from app.services.rbac import require_permission

router = APIRouter(prefix="/api/users", tags=["用户管理"])


def _user_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        username=user.username,
        status=user.status,
        created_at=user.created_at,
        roles=[r.role_name for r in user.roles],
    )


@router.get("", response_model=list[UserOut])
def list_users(
    request: Request,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    ip = get_client_ip(request)
    require_permission(db, current, "user:manage", ip=ip)
    users = db.query(User).all()
    return [_user_out(u) for u in users]


@router.post("", response_model=UserOut)
def create_user(
    body: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    ip = get_client_ip(request)
    require_permission(db, current, "user:manage", ip=ip)
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(username=body.username, password_hash=hash_password(body.password), status=body.status)
    db.add(user)
    db.flush()
    for rid in body.role_ids:
        role = db.query(Role).filter(Role.id == rid).first()
        if role:
            db.add(UserRole(user_id=user.id, role_id=rid))
    db.commit()
    db.refresh(user)
    write_log(db, user_id=current.id, action="CREATE_USER", target_type="user", target_id=str(user.id), result="成功", detail=f"创建用户 {user.username}", ip=ip)
    return _user_out(user)


@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    body: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    ip = get_client_ip(request)
    require_permission(db, current, "user:manage", ip=ip)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if body.status is not None:
        user.status = body.status
    if body.password:
        user.password_hash = hash_password(body.password)
    db.commit()
    db.refresh(user)
    write_log(db, user_id=current.id, action="UPDATE_USER", target_type="user", target_id=str(user_id), result="成功", ip=ip)
    return _user_out(user)


@router.put("/{user_id}/roles", response_model=UserOut)
def assign_roles(
    user_id: int,
    body: RoleAssign,
    request: Request,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    ip = get_client_ip(request)
    require_permission(db, current, "user:manage", ip=ip)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    db.query(UserRole).filter(UserRole.user_id == user_id).delete()
    for rid in body.role_ids:
        if db.query(Role).filter(Role.id == rid).first():
            db.add(UserRole(user_id=user_id, role_id=rid))
    db.commit()
    db.refresh(user)
    write_log(db, user_id=current.id, action="ASSIGN_ROLES", target_type="user", target_id=str(user_id), result="成功", detail=str(body.role_ids), ip=ip)
    return _user_out(user)
