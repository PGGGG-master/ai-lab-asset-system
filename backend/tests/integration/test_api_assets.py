from pathlib import Path

from tests.conftest import auth_headers, create_test_asset, login


def test_list_assets_requires_login(client):
    response = client.get("/api/assets")
    assert response.status_code == 401


def test_upload_and_list_asset(client, db_session, upload_dir):
    token = login(client, "admin", "admin123")
    files = {"file": ("demo.txt", b"model params", "text/plain")}
    data = {"name": "演示模型", "asset_type": "模型资产", "description": "测试"}
    response = client.post(
        "/api/assets/upload",
        headers=auth_headers(token),
        data=data,
        files=files,
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["name"] == "演示模型"
    assert body["asset_type"] == "模型资产"
    assert body["file_ext"] == ".txt"

    list_resp = client.get("/api/assets", headers=auth_headers(token))
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1


def test_preview_asset(client, db_session, upload_dir):
    admin_token = login(client, "admin", "admin123")
    asset = create_test_asset(db_session, upload_dir, owner_id=1)

    response = client.get(f"/api/assets/{asset.id}/preview", headers=auth_headers(admin_token))
    assert response.status_code == 200
    assert response.json()["content"] == "test model content"


def test_download_asset(client, db_session, upload_dir):
    admin_token = login(client, "admin", "admin123")
    asset = create_test_asset(db_session, upload_dir, owner_id=1)

    response = client.get(f"/api/assets/{asset.id}/download", headers=auth_headers(admin_token))
    assert response.status_code == 200
    assert response.content == b"test model content"


def test_delete_asset(client, db_session, upload_dir):
    admin_token = login(client, "admin", "admin123")
    asset = create_test_asset(db_session, upload_dir, owner_id=1, name="待删除资产")
    file_path = Path(asset.file_path)
    assert file_path.exists()

    response = client.delete(f"/api/assets/{asset.id}", headers=auth_headers(admin_token))
    assert response.status_code == 200
    assert not file_path.exists()
