"""
部门模型 — 支持树形层级（自引用 parent_id）
例如：总公司 → 技术部 → 后端组
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="部门名称")

    # 树形结构：parent_id 指向同一表的 id，NULL 表示顶级部门
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("departments.id"), nullable=True, comment="上级部门ID"
    )
    # 部门负责人（暂时允许为空，等 User 模型创建后补充 FK）
    manager_id: Mapped[Optional[int]] = mapped_column(nullable=True, comment="部门负责人ID")

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )

    # 自引用关系
    parent: Mapped[Optional["Department"]] = relationship(
        "Department", remote_side=[id], back_populates="children"
    )
    children: Mapped[list["Department"]] = relationship(
        "Department", back_populates="parent"
    )

    def __repr__(self) -> str:
        return f"<Department(id={self.id}, name='{self.name}')>"
