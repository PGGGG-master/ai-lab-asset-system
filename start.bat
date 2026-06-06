@echo off
chcp 65001 >nul
cd /d "%~dp0backend"
echo 正在启动 AI 实验室资产管理系统...
echo 启动后请在浏览器打开: http://127.0.0.1:8000/
echo 按 Ctrl+C 可停止服务
echo.
call venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload
pause
