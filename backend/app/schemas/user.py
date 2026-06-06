"""
用户相关 Pydantic Schema — 请求/响应数据模型
FastAPI 用这些做自动校验、序列化和文档生成
"""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# ========== 请求模型 ==========

class UserRegisterRequest(BaseModel):
    """注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="登录用户名")
    email: str = Field(..., max_length=100, description="邮箱")
    password: str = Field(..., min_length=6, max_length=50, description="密码（至少6位）")
    full_name: str = Field(..., min_length=1, max_length=50, description="真实姓名")


class UserLoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


# ========== 响应模型 ==========

class TokenResponse(BaseModel):
    """登录成功返回的 Token"""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """用户信息（不含密码）"""
    id: int
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool
    department_id: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}  # 允许从 SQLAlchemy Model 直接转换
