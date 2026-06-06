import pytest
from fastapi import HTTPException

from app.models import User
from app.services.rbac import (
    ASSET_TYPE_DATASET,
    ASSET_TYPE_MODEL,
    check_asset_type_access,
    get_user_permissions,
    require_permission,
)


def _get_user(db_session, username: str) -> User:
    return db_session.query(User).filter(User.username == username).first()


def test_get_user_permissions(db_session):
    admin = _get_user(db_session, "admin")
    perms = get_user_permissions(db_session, admin.id)
    assert "asset:read" in perms
    assert "user:manage" in perms

    guest = _get_user(db_session, "guest")
    guest_perms = get_user_permissions(db_session, guest.id)
    assert guest_perms == {"asset:read"}


def test_require_permission_success(db_session):
    admin = _get_user(db_session, "admin")
    require_permission(db_session, admin, "asset:upload")


def test_require_permission_denied(db_session):
    guest = _get_user(db_session, "guest")
    with pytest.raises(HTTPException) as exc:
        require_permission(db_session, guest, "asset:upload", ip="127.0.0.1")
    assert exc.value.status_code == 403


def test_check_asset_type_access_modeler_on_model(db_session):
    modeler = _get_user(db_session, "modeler")
    check_asset_type_access(db_session, modeler, ASSET_TYPE_MODEL, "UPDATE_ASSET")


def test_check_asset_type_access_modeler_on_dataset(db_session):
    modeler = _get_user(db_session, "modeler")
    with pytest.raises(HTTPException) as exc:
        check_asset_type_access(db_session, modeler, ASSET_TYPE_DATASET, "DELETE_ASSET", ip="127.0.0.1")
    assert exc.value.status_code == 403
