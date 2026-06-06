# 基于 RBAC 的 AI 实验室资产管理系统

面向软件安全实验课程的小型 Web 系统，使用 **FastAPI + SQLite + Vue 3 + Element Plus** 实现基于角色的访问控制（RBAC），并以 `.txt` 文件模拟模型参数、数据集、Prompt 模板等实验室资产。

## 功能特性

- 7 种角色：系统管理员、项目负责人、模型管理员、数据管理员、实验成员、安全审计员、访客
- 完整 RBAC：用户 → 角色 → 权限，前后端双重校验
- 资产 CRUD：上传 / 预览 / 下载 / 修改 / 删除（仅 `.txt`）
- 按资产类型限制：模型管理员只能管理「模型资产」，数据管理员只能管理「数据集」
- 操作日志：记录登录、文件操作及越权（403）尝试

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

### 1. 后端

```bash
cd ai-lab-asset-system/backend
python -m venv venv
# Windows:
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

首次启动会自动创建 SQLite 数据库、初始化角色权限和演示数据。

API 文档：http://127.0.0.1:8000/docs

### 2. 前端（两种方式任选）

**方式 A：内置 Web 界面（无需 Node.js）**

后端启动后直接访问：**http://127.0.0.1:8000/**

**方式 B：Vue 开发版（需安装 Node.js）**

```bash
cd ai-lab-asset-system/frontend
npm install
npm run dev
```

浏览器访问：http://127.0.0.1:5173

### 3. HTTPS（可选）

```bash
openssl req -x509 -newkey rsa:2048 -keyout server.key -out server.crt -days 365 -nodes
uvicorn app.main:app --host 0.0.0.0 --port 8443 --ssl-keyfile server.key --ssl-certfile server.crt
```

## 答辩演示建议

1. **admin** 登录 → 展示用户/角色/权限/资产管理全菜单
2. **member** 登录 → 无删除按钮；用 API 或开发者工具尝试删除 → 403 + 日志
3. **modeler** 修改模型资产成功；修改数据集资产失败
4. **auditor** 仅可查看操作日志
5. **guest** 仅可预览列表，下载返回 403

## 项目结构

```
ai-lab-asset-system/
├── backend/          # FastAPI 后端
│   ├── app/
│   │   ├── routers/  # API 路由
│   │   ├── services/ # RBAC、日志
│   │   └── init_db.py
│   └── uploads/      # .txt 资产文件
└── frontend/         # Vue 3 前端
    └── src/views/
```

## 技术栈

- 后端：FastAPI、SQLAlchemy、SQLite、JWT、bcrypt
- 前端：Vue 3、Vue Router、Element Plus、Axios
