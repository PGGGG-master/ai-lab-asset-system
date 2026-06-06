from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile

from app.services.asset_files import (
    build_stored_filename,
    download_filename,
    file_rules_payload,
    is_previewable,
    read_preview_content,
    validate_file_for_type,
)


def _upload_file(filename: str, content: bytes = b"data") -> UploadFile:
    return UploadFile(filename=filename, file=BytesIO(content))


def test_validate_file_for_type_success():
    ext = validate_file_for_type(_upload_file("model.txt"), "模型资产")
    assert ext == ".txt"


def test_validate_file_for_type_wrong_extension():
    with pytest.raises(HTTPException) as exc:
        validate_file_for_type(_upload_file("model.pdf"), "模型资产")
    assert exc.value.status_code == 400
    assert "仅允许" in exc.value.detail


def test_is_previewable():
    assert is_previewable("模型资产")
    assert not is_previewable("实验报告")


def test_build_stored_filename_unique():
    a = build_stored_filename(".txt")
    b = build_stored_filename(".txt")
    assert a != b
    assert a.endswith(".txt")


def test_download_filename():
    assert download_filename("报告", "/uploads/a.pdf") == "报告.pdf"
    assert download_filename("报告.pdf", "/uploads/a.pdf") == "报告.pdf"


def test_read_preview_content(tmp_path):
    path = tmp_path / "demo.txt"
    path.write_text("hello", encoding="utf-8")
    assert read_preview_content(path) == "hello"


def test_file_rules_payload_structure():
    rules = file_rules_payload()
    assert "模型资产" in rules
    assert ".txt" in rules["模型资产"]["extensions"]
    assert rules["实验报告"]["preview"] is False
