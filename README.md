# 费控系统 (Cost Control System)

全栈费控管理系统 — 从零搭建的学习项目。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.12 + FastAPI + SQLAlchemy 2.0 |
| 前端 | Vue 3 + Element Plus + Vite |
| 数据库 | SQLite（开发）/ PostgreSQL（生产） |
| 包管理 | uv（后端）+ npm（前端） |
| 认证 | JWT (OAuth2 Password Flow) |

## 功能模块

- **用户管理** — 注册/登录、角色权限（admin/manager/finance/employee）
- **预算管理** — 预算编制、审批、调整、执行跟踪、超标预警
- **费用报销** — 报销单 CRUD、发票上传/下载、报编号自动生成
- **审批流程** — 多级审批、状态流转、审批历史时间线
- **报表查询** — 个人/部门费用统计、预算执行报表、CSV 导出

## 快速启动

### 后端

```bash
cd backend
# 激活虚拟环境（Windows）
..\.venv\Scripts\activate
# 或 Linux/Mac
source ../.venv/bin/activate

# 安装依赖
uv pip install -r requirements.txt

# 数据库迁移
alembic upgrade head

# 启动服务
uvicorn app.main:app --reload

# 访问 API 文档: http://localhost:8000/docs
```

### 前端

```bash
cd frontend
npm install
npm run dev

# 访问: http://localhost:5173
```

### 默认账号

首次启动后，通过 API 注册账号：
```
POST /api/v1/auth/register
{"username":"admin", "email":"admin@test.com", "password":"123456", "full_name":"管理员"}
```

然后手动在数据库中提权：
```sql
UPDATE users SET role = 'admin' WHERE username = 'admin';
```

## 项目结构

```
├── backend/               # 后端
│   ├── app/
│   │   ├── main.py        # FastAPI 入口
│   │   ├── config.py      # 配置管理
│   │   ├── database.py    # SQLAlchemy 引擎
│   │   ├── models/        # 数据模型
│   │   ├── schemas/       # Pydantic 请求/响应
│   │   ├── api/           # API 路由
│   │   ├── services/      # 业务逻辑
│   │   ├── middleware/     # 中间件
│   │   └── utils/         # 工具函数
│   └── alembic/           # 数据库迁移
├── frontend/              # 前端
│   └── src/
│       ├── views/         # 页面组件
│       ├── components/    # 复用组件
│       ├── api/           # Axios 封装
│       ├── stores/        # Pinia 状态管理
│       └── router/        # 路由配置
└── CLAUDE.md              # AI 助手指南
```

## 运维说明

- 日志：请求日志输出到控制台，格式 `[时间] LEVEL 消息`
- 健康检查：`GET /api/v1/health`
- 配置：通过 `.env` 文件或环境变量管理
- 生产部署建议：将 SQLite 替换为 PostgreSQL，SECRET_KEY 更换为强随机值
