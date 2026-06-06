from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
DATABASE_URL = f"sqlite:///{BASE_DIR / 'ai_lab_assets.db'}"

SECRET_KEY = "ai-lab-rbac-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB（含 PDF 等）
