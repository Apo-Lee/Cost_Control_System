"""
审批业务逻辑 — 审批状态机

报销单状态流转：
  draft → submitted → approved → paid
                    ↘ rejected → draft (可重新提交)

预算状态流转：
  draft → submitted → approved
                    ↘ rejected → draft
"""
from sqlalchemy.orm import Session

from ..models.approval import ApprovalRecord
from ..models.expense import ExpenseReport
from ..models.budget import Budget
from ..models.user import User


class ApprovalService:

    @staticmethod
    def approve(db: Session, target_type: str, target_id: int, approver_id: int, comment: str | None = None) -> dict:
        """通过审批"""
        if target_type == "expense_report":
            target = db.query(ExpenseReport).filter(ExpenseReport.id == target_id).first()
        elif target_type == "budget":
            target = db.query(Budget).filter(Budget.id == target_id).first()
        else:
            raise ValueError(f"不支持的审批类型: {target_type}")

        if not target:
            raise ValueError(f"{target_type} ID={target_id} 不存在")
        if target.status != "submitted":
            raise ValueError(f"当前状态 '{target.status}' 不可审批")

        # 记录审批
        record = ApprovalRecord(
            target_type=target_type,
            target_id=target_id,
            approver_id=approver_id,
            action="approved",
            comment=comment,
        )
        db.add(record)

        # 更新状态
        target.status = "approved"
        target.current_approver_id = None
        db.commit()

        return {"message": "审批通过", "status": "approved"}

    @staticmethod
    def reject(db: Session, target_type: str, target_id: int, approver_id: int, comment: str | None = None) -> dict:
        """驳回审批 — 重置回草稿状态，允许修改后重新提交"""
        if target_type == "expense_report":
            target = db.query(ExpenseReport).filter(ExpenseReport.id == target_id).first()
        elif target_type == "budget":
            target = db.query(Budget).filter(Budget.id == target_id).first()
        else:
            raise ValueError(f"不支持的审批类型: {target_type}")

        if not target:
            raise ValueError(f"{target_type} ID={target_id} 不存在")
        if target.status != "submitted":
            raise ValueError(f"当前状态 '{target.status}' 不可驳回")

        # 记录审批
        record = ApprovalRecord(
            target_type=target_type,
            target_id=target_id,
            approver_id=approver_id,
            action="rejected",
            comment=comment,
        )
        db.add(record)

        # 驳回后回到草稿
        target.status = "draft"
        target.current_approver_id = None
        db.commit()

        return {"message": "已驳回", "status": "draft"}

    @staticmethod
    def get_pending(db: Session, approver_id: int, target_type: str | None = None) -> list[dict]:
        """获取待审批列表"""
        pending = []

        # 报销单审批
        if target_type is None or target_type == "expense_report":
            reports = (
                db.query(ExpenseReport)
                .filter(ExpenseReport.status == "submitted")
                .all()
            )
            for r in reports:
                user = db.query(User).filter(User.id == r.submitter_id).first()
                pending.append({
                    "id": r.id,
                    "target_type": "expense_report",
                    "target_id": r.id,
                    "title": r.title,
                    "amount": r.amount,
                    "submitter_name": user.full_name if user else f"用户#{r.submitter_id}",
                    "submitted_at": r.submitted_at,
                })

        # 预算审批
        if target_type is None or target_type == "budget":
            budgets = (
                db.query(Budget)
                .filter(Budget.status == "submitted")
                .all()
            )
            for b in budgets:
                user = db.query(User).filter(User.id == b.created_by).first()
                pending.append({
                    "id": b.id,
                    "target_type": "budget",
                    "target_id": b.id,
                    "title": f"预算 #{b.id}",
                    "amount": b.amount,
                    "submitter_name": user.full_name if user else f"用户#{b.created_by}",
                    "submitted_at": b.created_at,
                })

        return pending

    @staticmethod
    def get_history(db: Session, target_type: str, target_id: int) -> list[ApprovalRecord]:
        """获取审批历史"""
        return (
            db.query(ApprovalRecord)
            .filter(
                ApprovalRecord.target_type == target_type,
                ApprovalRecord.target_id == target_id,
            )
            .order_by(ApprovalRecord.created_at.asc())
            .all()
        )
