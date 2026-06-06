"""
FastAPI 应用入口
注册路由、中间件、CORS 配置
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import engine, Base
from .api import auth, departments, users


# ========== 应用生命周期 ==========
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时：自动创建所有表（仅开发阶段，生产用 Alembic 迁移）
    # SQLite 下如果表不存在则创建，已有表不会重复创建
    Base.metadata.create_all(bind=engine)
    yield
    # 关闭时：清理资源（当前无需特殊处理）


# ========== 创建 App ==========
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# ========== CORS 中间件 ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== 注册路由 ==========
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(departments.router)

# ========== 健康检查 ==========
@app.get("/api/v1/health", tags=["系统"])
def health_check():
    """健康检查接口 — 运维监控用"""
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
