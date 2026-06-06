from tests.conftest import auth_headers, create_test_asset, login


def test_guest_cannot_upload(client):
    token = login(client, "guest", "guest123")
    files = {"file": ("demo.txt", b"content", "text/plain")}
    data = {"name": "非法上传", "asset_type": "模型资产"}
    response = client.post(
        "/api/assets/upload",
        headers=auth_headers(token),
        data=data,
        files=files,
    )
    assert response.status_code == 403


def test_guest_can_read_assets(client, db_session, upload_dir):
    create_test_asset(db_session, upload_dir, owner_id=1)
    token = login(client, "guest", "guest123")

    response = client.get("/api/assets", headers=auth_headers(token))
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_modeler_cannot_delete_dataset(client, db_session, upload_dir):
    asset = create_test_asset(
        db_session,
        upload_dir,
        owner_id=1,
        asset_type="数据集",
        name="测试数据集",
    )
    token = login(client, "modeler", "modeler123")

    response = client.delete(f"/api/assets/{asset.id}", headers=auth_headers(token))
    assert response.status_code == 403


def test_modeler_can_delete_model_asset(client, db_session, upload_dir):
    asset = create_test_asset(db_session, upload_dir, owner_id=1, asset_type="模型资产")
    token = login(client, "modeler", "modeler123")

    response = client.delete(f"/api/assets/{asset.id}", headers=auth_headers(token))
    assert response.status_code == 200


def test_guest_cannot_view_logs(client):
    token = login(client, "guest", "guest123")
    response = client.get("/api/logs", headers=auth_headers(token))
    assert response.status_code == 403


def test_admin_can_view_logs(client, db_session, upload_dir):
    login(client, "guest", "guest123")  # 产生一条登录日志
    token = login(client, "admin", "admin123")

    response = client.get("/api/logs", headers=auth_headers(token))
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) >= 1
    assert any(log["action"] == "LOGIN" for log in logs)
