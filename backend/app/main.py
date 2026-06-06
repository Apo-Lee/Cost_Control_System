"""
FastAPI 应用入口
"""
import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import engine, Base
from .api import approvals, auth, budgets, departments, expenses, reports, users

# 配置日志
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s %(message)s")
logger = logging.getLogger("expense_control")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS — 必须最先处理 OPTIONS 预检，所以最后 add（逆序执行）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 先用 * 排查是不是 origin 匹配问题
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(departments.router)
app.include_router(budgets.router)
app.include_router(expenses.router)
app.include_router(approvals.router)
app.include_router(reports.router)


@app.get("/api/v1/health", tags=["系统"])
def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
