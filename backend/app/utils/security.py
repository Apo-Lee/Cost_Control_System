"""
安全工具 — 密码哈希 + JWT 生成与验证

为什么用 bcrypt？
- 自带盐值（salt），相同密码每次哈希结果不同 → 防彩虹表
- 计算成本可调（rounds 参数），硬件升级后能提高破解难度
- 比 SHA256/MD5 安全得多，后者可以 GPU 暴力破解

JWT 结构（三段 Base64，用 . 分隔）：
  header.payload.signature
  例如：eyJhbGciOi... .eyJzdWIiOi... .SflKxwRJS...
"""
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from ..config import settings

# ========== 密码哈希上下文 ==========
# bcrypt 算法，自动处理 salt 生成和验证
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """将明文密码哈希后存储 — 永远不存明文！"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码是否匹配 — 用户登录时调用"""
    return pwd_context.verify(plain_password, hashed_password)


# ========== JWT Token 操作 ==========

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    生成 JWT Access Token
    data 示例: {"sub": "admin"}  — sub 是 JWT 标准字段，存用户标识
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """
    验证并解码 JWT Token
    成功返回 payload 字典，失败返回 None（不抛异常，由调用方处理）
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
