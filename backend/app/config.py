"""
配置管理 — 所有配置项集中管理，通过环境变量覆盖默认值
运维友好：生产环境通过 .env 或系统环境变量注入敏感配置
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 应用基础
    APP_NAME: str = "费控系统"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # 数据库 — 默认 SQLite，生产改为 PostgreSQL 连接串
    DATABASE_URL: str = "sqlite:///./cost_control.db"

    # JWT 认证 — 生产环境务必更换为强随机字符串
    SECRET_KEY: str = "change-me-to-a-random-secret-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8  # 8 小时

    # 文件上传
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    # CORS — 前端开发服务器地址
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
