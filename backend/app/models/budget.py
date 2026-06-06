"""
预算模型 — 按部门 + 费用类型 + 年度/季度编制
"""
from datetime import datetime

from sqlalchemy import DECIMAL, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Budget(Base):
    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id"), nullable=False, comment="预算归属部门"
    )
    expense_type_id: Mapped[int] = mapped_column(
        ForeignKey("expense_types.id"), nullable=False, comment="费用类型"
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False, comment="预算年度")
    quarter: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="预算季度(1-4, NULL=年度)"
    )
    amount: Mapped[float] = mapped_column(
        DECIMAL(12, 2), nullable=False, comment="预算金额"
    )
    used_amount: Mapped[float] = mapped_column(
        DECIMAL(12, 2), default=0.0, nullable=False, comment="已使用金额（冗余字段加速查询）"
    )
    # draft=草稿, submitted=已提交, approved=已审批, rejected=已驳回
    status: Mapped[str] = mapped_column(
        String(20), default="draft", nullable=False, comment="预算状态"
    )
    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, comment="创建人"
    )
    approved_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, comment="审批人"
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    # 关联
    department: Mapped["Department"] = relationship("Department")  # noqa: F821
    expense_type: Mapped["ExpenseType"] = relationship("ExpenseType")  # noqa: F821
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])  # noqa: F821

    def __repr__(self) -> str:
        return f"<Budget(id={self.id}, dept={self.department_id}, amount={self.amount})>"


class BudgetAdjustment(Base):
    __tablename__ = "budget_adjustments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    budget_id: Mapped[int] = mapped_column(
        ForeignKey("budgets.id"), nullable=False, comment="关联预算"
    )
    adjustment_amount: Mapped[float] = mapped_column(
        DECIMAL(12, 2), nullable=False, comment="调整金额（正=追加，负=调减）"
    )
    reason: Mapped[str] = mapped_column(String(500), nullable=False, comment="调整原因")
    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, comment="操作人"
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
