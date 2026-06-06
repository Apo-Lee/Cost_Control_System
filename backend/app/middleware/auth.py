"""
JWT 认证中间件 — FastAPI 依赖注入
每个需要登录的接口只需添加 Depends(get_current_user) 即可
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..utils.security import decode_access_token

# OAuth2 密码流 — 前端在 Authorization 头传 Bearer <token>
# tokenUrl 指向登录接口，Swagger 文档中的 "Authorize" 按钮会用到
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    从请求的 Authorization 头中解析 JWT，返回当前登录用户
    如果 token 无效或用户不存在 → 自动返回 401
    """
    # 1. 解析 Token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. 从 payload 取用户名（sub 字段）
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 格式错误",
        )

    # 3. 查到用户
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被删除",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用",
        )

    return user
