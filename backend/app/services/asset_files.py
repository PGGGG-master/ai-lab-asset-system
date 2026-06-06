import mimetypes
from pathlib import Path

from fastapi import HTTPException, UploadFile

# 各资产类型允许的上传扩展名
ASSET_TYPE_EXTENSIONS: dict[str, set[str]] = {
    "模型资产": {".txt"},
    "数据集": {".csv", ".json"},
    "Prompt模板": {".json", ".txt"},
    "实验报告": {".pdf"},
    "配置文件": {".json", ".txt"},
    "论文资料": {".pdf"},
}

# 不支持在线预览的类型
NO_PREVIEW_TYPES = {"实验报告", "论文资料"}


def get_allowed_extensions(asset_type: str) -> set[str]:
    return ASSET_TYPE_EXTENSIONS.get(asset_type, set())


def is_previewable(asset_type: str) -> bool:
    return asset_type not in NO_PREVIEW_TYPES


def validate_file_for_type(file: UploadFile, asset_type: str) -> str:
    ext = Path(file.filename or "").suffix.lower()
    allowed = get_allowed_extensions(asset_type)
    if not allowed:
        raise HTTPException(status_code=400, detail=f"未知资产类型: {asset_type}")
    if ext not in allowed:
        exts = ", ".join(sorted(allowed))
        raise HTTPException(status_code=400, detail=f"「{asset_type}」仅允许: {exts}")
    return ext


def build_stored_filename(ext: str) -> str:
    import uuid

    return f"{uuid.uuid4().hex}{ext}"


def download_filename(asset_name: str, file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    if asset_name.lower().endswith(ext):
        return asset_name
    return f"{asset_name}{ext}"


def guess_media_type(filename: str) -> str:
    media_type, _ = mimetypes.guess_type(filename)
    return media_type or "application/octet-stream"


def read_preview_content(path: Path, max_chars: int = 50000) -> str:
    return path.read_text(encoding="utf-8", errors="replace")[:max_chars]


def file_rules_payload() -> dict:
    return {
        asset_type: {
            "extensions": sorted(exts),
            "preview": is_previewable(asset_type),
        }
        for asset_type, exts in ASSET_TYPE_EXTENSIONS.items()
    }
