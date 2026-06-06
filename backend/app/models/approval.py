"""
审批记录模型 — 支持报销单和预算的审批
"""
from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class ApprovalRecord(Base):
    __tablename__ = "approval_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # 多态关联：target_type = expense_report / budget
    target_type: Mapped[str] = mapped_column(
        String(30), nullable=False, comment="审批目标类型"
    )
    target_id: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="审批目标ID"
    )
    approver_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, comment="审批人"
    )
    level: Mapped[int] = mapped_column(
        Integer, default=1, nullable=False, comment="审批级别"
    )
    action: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="操作: approved/rejected"
    )
    comment: Mapped[str | None] = mapped_column(
        String(500), nullable=True, comment="审批意见"
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
