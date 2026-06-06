from sqlalchemy.orm import Session

from app.models import OperationLog


def write_log(
    db: Session,
    *,
    user_id: int | None,
    action: str,
    target_type: str | None = None,
    target_id: str | None = None,
    result: str,
    detail: str | None = None,
    ip: str | None = None,
) -> OperationLog:
    log = OperationLog(
        user_id=user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        result=result,
        detail=detail,
        ip=ip,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
