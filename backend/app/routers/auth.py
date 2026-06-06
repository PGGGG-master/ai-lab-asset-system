from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.auth import create_access_token, verify_password
from app.database import get_db
from app.deps import build_user_info, get_client_ip
from app.models import User
from app.schemas import LoginRequest, TokenResponse, UserInfo, DashboardStats, LogOut
from app.services.logging import write_log
from app.services.rbac import get_user_permissions
from app.deps import get_current_user
from app.models import Asset, Role, Permission, OperationLog

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, request: Request, db: Session = Depends(get_db)):
    ip = get_client_ip(request)
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.password_hash):
        write_log(
            db,
            user_id=user.id if user else None,
            action="LOGIN",
            target_type="user",
            target_id=body.username,
            result="失败",
            detail="用户名或密码错误",
            ip=ip,
        )
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if user.status != "active":
        write_log(db, user_id=user.id, action="LOGIN", target_type="user", target_id=str(user.id), result="失败", detail="账号已禁用", ip=ip)
        raise HTTPException(status_code=403, detail="账号已禁用")

    token = create_access_token(user.id, user.username)
    info = build_user_info(user, db)
    write_log(db, user_id=user.id, action="LOGIN", target_type="user", target_id=str(user.id), result="成功", detail="登录成功", ip=ip)
    return TokenResponse(access_token=token, user=UserInfo(**info))


@router.get("/me", response_model=UserInfo)
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return UserInfo(**build_user_info(user, db))


@router.get("/dashboard", response_model=DashboardStats)
def dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    recent = (
        db.query(OperationLog)
        .order_by(OperationLog.created_at.desc())
        .limit(10)
        .all()
    )
    logs_out = []
    for log in recent:
        username = log.user.username if log.user else None
        logs_out.append(
            LogOut(
                id=log.id,
                user_id=log.user_id,
                username=username,
                action=log.action,
                target_type=log.target_type,
                target_id=log.target_id,
                result=log.result,
                detail=log.detail,
                ip=log.ip,
                created_at=log.created_at,
            )
        )
    return DashboardStats(
        user_count=db.query(User).count(),
        asset_count=db.query(Asset).count(),
        role_count=db.query(Role).count(),
        permission_count=db.query(Permission).count(),
        log_count=db.query(OperationLog).count(),
        recent_logs=logs_out,
    )
