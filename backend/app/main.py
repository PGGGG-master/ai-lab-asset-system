from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.init_db import init_database
from app.routers import auth, users, roles, assets, logs

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(
    title="AI实验室资产管理系统",
    description="基于 RBAC 的 AI 实验室资产管理系统",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(assets.router)
app.include_router(logs.router)


@app.on_event("startup")
def on_startup():
    init_database()


@app.get("/api/health")
def health():
    return {"status": "ok"}


if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/")
    def spa_index():
        return FileResponse(
            STATIC_DIR / "index.html",
            media_type="text/html; charset=utf-8",
        )
