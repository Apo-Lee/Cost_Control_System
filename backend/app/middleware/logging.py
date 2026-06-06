"""
请求日志中间件 — 记录每个请求的方法、路径、耗时、状态码
运维友好：方便排查问题和性能分析
"""
import time
import logging

from fastapi import Request

# 配置日志格式：时间 + 级别 + 消息
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("expense_control")


async def log_requests(request: Request, call_next):
    """记录请求日志中间件"""
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    logger.info(
        f"{request.method} {request.url.path} → {response.status_code} ({duration:.3f}s)"
    )
    return response
