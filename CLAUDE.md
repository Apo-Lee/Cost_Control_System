# CLAUDE.md — 费控系统 (Cost Control System)

## 项目概述

全栈费控系统，用于学习全栈开发。包含：用户管理、预算管理、费用报销、审批流程、报表查询。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.12 + FastAPI + SQLAlchemy 2.0 |
| 前端 | Vue 3 + Element Plus + Vite |
| 数据库 | SQLite（开发）/ PostgreSQL（生产） |
| 包管理 | uv（后端）+ npm（前端） |
| 认证 | JWT (OAuth2 Password Flow) |

## 启动命令

```bash
# 后端 — 从 backend/ 目录执行
cd backend
../.venv/Scripts/activate        # Windows 激活虚拟环境
uvicorn app.main:app --reload     # 启动，访问 http://localhost:8000/docs

# 前端 — 从 frontend/ 目录执行
cd frontend
npm install
npm run dev                       # 启动，访问 http://localhost:5173
```

## 数据库迁移

```bash
cd backend
# 激活虚拟环境后：
alembic revision --autogenerate -m "描述"   # 生成迁移文件
alembic upgrade head                        # 执行迁移
alembic downgrade -1                        # 回滚上一步
```

## 项目结构

```
backend/app/
├── main.py          # FastAPI 入口
├── config.py        # 配置管理 (pydantic-settings)
├── database.py      # SQLAlchemy 引擎 + Session
├── models/          # 数据模型 (User, Department, Budget, ExpenseReport, ApprovalRecord)
├── schemas/         # Pydantic 请求/响应模型
├── api/             # API 路由
├── services/        # 业务逻辑层
├── middleware/       # JWT 认证、日志中间件
└── utils/           # 工具函数
frontend/src/
├── main.js          # Vue 入口
├── App.vue          # 根组件
├── router/          # 路由配置
├── stores/          # Pinia 状态管理
├── api/             # Axios 封装
├── views/           # 页面组件
└── components/      # 复用组件
```
