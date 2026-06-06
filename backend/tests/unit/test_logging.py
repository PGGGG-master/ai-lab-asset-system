from app.models import OperationLog
from app.services.logging import write_log


def test_write_log_persists_record(db_session):
    log = write_log(
        db_session,
        user_id=1,
        action="UPLOAD",
        target_type="asset",
        target_id="1",
        result="成功",
        detail="测试上传",
        ip="127.0.0.1",
    )
    assert log.id is not None

    saved = db_session.query(OperationLog).filter(OperationLog.id == log.id).first()
    assert saved.action == "UPLOAD"
    assert saved.result == "成功"
    assert saved.detail == "测试上传"
    assert saved.ip == "127.0.0.1"
