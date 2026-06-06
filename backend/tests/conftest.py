import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import hash_password
from app.database import Base, get_db
from app.main import app
from app.models import Asset, Permission, Role, RolePermission, User, UserRole

# 精简版角色权限，覆盖主要测试场景
TEST_PERMISSIONS = [
    ("asset:read", "查看资产"),
    ("asset:download", "下载资产"),
    ("asset:upload", "上传资产"),
    ("asset:update", "修改资产"),
    ("asset:delete", "删除资产"),
    ("model:manage", "管理模型资产"),
    ("dataset:manage", "管理数据集资产"),
    ("user:manage", "用户管理"),
    ("log:view", "查看日志"),
]

TEST_ROLE_PERMS = {
    "系统管理员": [code for code, _ in TEST_PERMISSIONS],
    "模型管理员": [
        "asset:read", "asset:download", "asset:upload", "asset:update", "asset:delete",
        "model:manage",
    ],
    "访客": ["asset:read"],
}

TEST_USERS = [
    ("admin", "系统管理员", "admin123"),
    ("modeler", "模型管理员", "modeler123"),
    ("guest", "访客", "guest123"),
]


def seed_test_data(db):
    perm_map = {}
    for code, name in TEST_PERMISSIONS:
        perm = Permission(permission_code=code, permission_name=name)
        db.add(perm)
        db.flush()
        perm_map[code] = perm

    role_map = {}
    for role_name, codes in TEST_ROLE_PERMS.items():
        role = Role(role_name=role_name, description=f"{role_name}角色")
        db.add(role)
        db.flush()
        role_map[role_name] = role
        for code in codes:
            db.add(RolePermission(role_id=role.id, permission_id=perm_map[code].id))

    user_map = {}
    for username, role_name, password in TEST_USERS:
        user = User(username=username, password_hash=hash_password(password), status="active")
        db.add(user)
        db.flush()
        db.add(UserRole(user_id=user.id, role_id=role_map[role_name].id))
        user_map[username] = user

    db.commit()
    return user_map


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    seed_test_data(session)
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def upload_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("app.config.UPLOAD_DIR", tmp_path)
    monkeypatch.setattr("app.routers.assets.UPLOAD_DIR", tmp_path)
    return tmp_path


@pytest.fixture
def client(db_session, upload_dir, monkeypatch):
    monkeypatch.setattr("app.main.init_database", lambda: None)

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def login(client: TestClient, username: str, password: str) -> str:
    response = client.post("/api/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def create_test_asset(db_session, upload_dir, owner_id: int, asset_type: str = "模型资产", name: str = "测试模型"):
    file_path = upload_dir / "test-model.txt"
    file_path.write_text("test model content", encoding="utf-8")
    asset = Asset(
        name=name,
        asset_type=asset_type,
        file_path=str(file_path),
        owner_id=owner_id,
        description="单元测试资产",
    )
    db_session.add(asset)
    db_session.commit()
    db_session.refresh(asset)
    return asset
