"""
全局异常处理 — 统一错误响应格式
"""
from fastapi import Request
from fastapi.responses import JSONResponse


async def global_exception_handler(request: Request, exc: Exception):
    """捕获所有未处理异常，返回统一格式"""
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "detail": str(exc) if request.app.debug else "请联系管理员",
        },
    )
