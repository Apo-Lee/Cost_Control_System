"""
FastAPI 应用入口
注册路由、中间件、CORS 配置
"""
import time
import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings
from .database import engine, Base
from .api import approvals, auth, budgets, departments, expenses, reports, users

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("expense_control")


# ========== 应用生命周期 ==========
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时：自动创建所有表（仅开发阶段，生产用 Alembic 迁移）
    Base.metadata.create_all(bind=engine)
    yield


# ========== 创建 App ==========
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# ========== 中间件 ==========
# 注意：Starlette 中间件执行顺序 = 添加顺序的逆序
# 所以 CORS 必须最后添加 → 最先执行 → 拦截 OPTIONS 预检请求

# 请求日志中间件
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration:.3f}s)")
        return response

app.add_middleware(LoggingMiddleware)

# CORS 中间件 — 必须最后添加（最先执行），处理浏览器 OPTIONS 预检
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
app.include_router(budgets.router)
app.include_router(expenses.router)
app.include_router(approvals.router)
app.include_router(reports.router)


# ========== 健康检查 ==========
@app.get("/api/v1/health", tags=["系统"])
def health_check():
    """健康检查接口 — 运维监控用"""
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
