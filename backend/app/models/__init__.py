# 数据模型包 — 在此处 import 所有 model，确保 Alembic 和 SQLAlchemy 能发现它们
from .department import Department
from .user import User

__all__ = ["Department", "User"]
