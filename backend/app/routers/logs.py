from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, get_client_ip
from app.models import OperationLog, User
from app.schemas import LogOut
from app.services.rbac import require_permission

router = APIRouter(prefix="/api/logs", tags=["操作日志"])


@router.get("", response_model=list[LogOut])
def list_logs(
    request: Request,
    limit: int = 200,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    ip = get_client_ip(request)
    require_permission(db, current, "log:view", ip=ip)
    logs = db.query(OperationLog).order_by(OperationLog.created_at.desc()).limit(min(limit, 500)).all()
    result = []
    for log in logs:
        result.append(
            LogOut(
                id=log.id,
                user_id=log.user_id,
                username=log.user.username if log.user else None,
                action=log.action,
                target_type=log.target_type,
                target_id=log.target_id,
                result=log.result,
                detail=log.detail,
                ip=log.ip,
                created_at=log.created_at,
            )
        )
    return result
