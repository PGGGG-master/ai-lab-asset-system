# 基于 RBAC 的 AI 实验室资产管理系统

面向软件安全实验课程的小型 Web 系统，使用 **FastAPI + SQLite + Vue 3 + Element Plus** 实现基于角色的访问控制（RBAC），并以本地文件模拟模型参数、数据集、Prompt 模板等实验室资产。

## 功能特性

- 7 种角色：系统管理员、项目负责人、模型管理员、数据管理员、实验成员、安全审计员、访客
- 完整 RBAC：用户 → 角色 → 权限，前后端双重校验
- 资产 CRUD：上传 / 预览 / 下载 / 修改 / 删除（按资产类型限制扩展名，如 `.txt`、`.csv`、`.json`、`.pdf`）
- 按资产类型限制：模型管理员只能管理「模型资产」，数据管理员只能管理「数据集」
- 操作日志：记录登录、文件操作及越权（403）尝试

## 环境要求

- **Python 3.10+**（后端必需）
- **Node.js 18+**（仅 Vue 开发版需要；使用内置 Web 界面则不需要）

## 演示账号

| 账号 | 密码 | 角色 |
|------|------|------|
| admin | admin123 | 系统管理员 |
| leader | leader123 | 项目负责人 |
| modeler | modeler123 | 模型管理员 |
| dataer | dataer123 | 数据管理员 |
| member | member123 | 实验成员 |
| auditor | auditor123 | 安全审计员 |
| guest | guest123 | 访客 |

## 快速启动

### 方式一：一键启动（Windows）

完成首次后端依赖安装后，双击项目根目录 **`start.bat`**，浏览器访问：**http://127.0.0.1:8000/**

### 方式二：手动启动

#### 1. 后端

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
# source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

首次启动会自动创建 SQLite 数据库（`backend/ai_lab_assets.db`）、初始化角色权限和演示数据。

- API 文档：http://127.0.0.1:8000/docs
- 内置 Web 界面：http://127.0.0.1:8000/

#### 2. 前端（Vue 开发版，可选）

```bash
cd frontend
npm install
npm run dev
```

浏览器访问：http://127.0.0.1:5173（`/api` 代理至后端 8000 端口）

### 3. HTTPS（可选）

```bash
openssl req -x509 -newkey rsa:2048 -keyout server.key -out server.crt -days 365 -nodes
uvicorn app.main:app --host 0.0.0.0 --port 8443 --ssl-keyfile server.key --ssl-certfile server.crt
```

## 运行测试

后端提供单元测试与 API 集成测试，使用内存数据库，不会污染正式 `ai_lab_assets.db`。

```bash
cd backend
venv\Scripts\activate          # Windows
pip install -r requirements-dev.txt
pytest -v                      # 全部测试
pytest tests/unit -v           # 仅单元测试
pytest tests/integration -v    # 仅集成测试
```

## 项目结构

```
ai-lab-asset-system/
├── README.md
├── start.bat                 # Windows 一键启动后端
├── 使用说明.txt
├── backend/
│   ├── app/
│   │   ├── routers/          # API 路由（auth、users、roles、assets、logs）
│   │   ├── services/         # RBAC、日志、文件规则
│   │   ├── init_db.py        # 角色权限与演示数据初始化
│   │   ├── auth.py           # JWT、密码哈希
│   │   └── main.py
│   ├── tests/                # pytest 单元测试与集成测试
│   ├── static/               # 内置 Web 页面
│   ├── uploads/              # 资产文件存储目录
│   ├── requirements.txt
│   └── requirements-dev.txt  # 测试依赖（pytest、httpx）
└── frontend/
    └── src/
        ├── views/              # 页面组件
        ├── router/             # 路由与权限守卫
        └── utils/permission.js # 前端权限校验
```

## 打包说明

分发源码时通常**不包含**以下目录/文件（需在新环境重新生成）：

- `backend/venv/` — Python 虚拟环境
- `frontend/node_modules/` — Node 依赖
- `backend/ai_lab_assets.db` — 本地数据库（首次启动自动创建）
- `__pycache__/`、`.pytest_cache/` — 缓存

## 技术栈

- 后端：FastAPI、SQLAlchemy、SQLite、JWT、bcrypt、pytest
- 前端：Vue 3、Vue Router、Element Plus、Axios
