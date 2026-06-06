"""
数据库引擎与 Session 管理
SQLAlchemy 2.0 风格：使用 Engine + sessionmaker
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings

# 创建引擎
# SQLite 需要 check_same_thread=False，否则 FastAPI 异步下会报错
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # DEBUG 模式下打印 SQL 语句，方便学习
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)

# Session 工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 所有 Model 继承自此 Base
class Base(DeclarativeBase):
    pass


# FastAPI 依赖：每个请求获取独立 Session，请求结束自动关闭
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
