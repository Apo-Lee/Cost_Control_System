"""
用户模型 — 支持多种角色：employee(员工)、manager(部门经理)、finance(财务)、admin(管理员)
"""
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True, comment="登录用户名"
    )
    email: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, comment="邮箱"
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="bcrypt 哈希密码"
    )
    full_name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="真实姓名"
    )
    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id"), nullable=True, comment="所属部门"
    )
    # 角色: employee(普通员工), manager(部门经理), finance(财务), admin(管理员)
    role: Mapped[str] = mapped_column(
        String(20), default="employee", nullable=False, comment="用户角色"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="是否启用"
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )

    # 关联部门
    department: Mapped["Department"] = relationship("Department")  # noqa: F821

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"
