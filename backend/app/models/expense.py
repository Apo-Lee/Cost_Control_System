"""
费用类型模型 — 差旅费、办公费、招待费等
报销单模型 — 报销申请主表
"""
from datetime import datetime

from sqlalchemy import DECIMAL, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class ExpenseType(Base):
    """费用类型"""
    __tablename__ = "expense_types"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="费用类型名称")
    code: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, comment="编码（如 TRAVEL）"
    )
    description: Mapped[str | None] = mapped_column(String(200), nullable=True, comment="说明")


class ExpenseReport(Base):
    """报销单"""
    __tablename__ = "expense_reports"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    report_no: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False, comment="报销单号"
    )
    submitter_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, comment="提交人"
    )
    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id"), nullable=False, comment="所属部门"
    )
    expense_type_id: Mapped[int] = mapped_column(
        ForeignKey("expense_types.id"), nullable=False, comment="费用类型"
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="报销事由")
    amount: Mapped[float] = mapped_column(
        DECIMAL(12, 2), nullable=False, comment="报销金额"
    )
    description: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="详细说明")
    attachment_path: Mapped[str | None] = mapped_column(
        String(500), nullable=True, comment="附件路径"
    )
    # draft/submitted/approved/rejected/paid
    status: Mapped[str] = mapped_column(
        String(20), default="draft", nullable=False, comment="报销单状态"
    )
    current_approver_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, comment="当前审批人"
    )
    submitted_at: Mapped[datetime | None] = mapped_column(nullable=True, comment="提交时间")
    settled_at: Mapped[datetime | None] = mapped_column(nullable=True, comment="完成时间")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
