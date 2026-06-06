"""
报销单业务逻辑 — 报编号自动生成 + 文件上传
"""
import os
from datetime import datetime

from sqlalchemy.orm import Session

from ..config import settings
from ..models.expense import ExpenseReport


def generate_report_no(db: Session) -> str:
    """
    生成报销单号: EX + 年月日 + 4位流水号
    例如: EX202606060001
    注意：高并发下可能重复，生产环境应用数据库序列或分布式ID
    """
    date_prefix = datetime.now().strftime("%Y%m%d")
    # 查询今日已有多少报销单（简单实现，非线程安全）
    count = (
        db.query(ExpenseReport)
        .filter(ExpenseReport.report_no.like(f"EX{date_prefix}%"))
        .count()
    )
    return f"EX{date_prefix}{count + 1:04d}"


class ExpenseService:

    @staticmethod
    def create_expense(
        db: Session,
        submitter_id: int,
        department_id: int,
        expense_type_id: int,
        title: str,
        amount: float,
        description: str | None = None,
    ) -> ExpenseReport:
        """创建报销单（草稿）"""
        report = ExpenseReport(
            report_no=generate_report_no(db),
            submitter_id=submitter_id,
            department_id=department_id,
            expense_type_id=expense_type_id,
            title=title,
            amount=amount,
            description=description,
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report

    @staticmethod
    def submit_expense(db: Session, report_id: int, user_id: int) -> ExpenseReport:
        """提交报销单审批 — 简化版，直接设为 submitted 状态"""
        report = db.query(ExpenseReport).filter(ExpenseReport.id == report_id).first()
        if not report:
            raise ValueError("报销单不存在")
        if report.status != "draft":
            raise ValueError("仅草稿状态可提交")
        if report.submitter_id != user_id:
            raise ValueError("只能提交自己的报销单")

        report.status = "submitted"
        report.submitted_at = datetime.now()
        db.commit()
        db.refresh(report)
        return report

    @staticmethod
    def upload_attachment(
        db: Session, report_id: int, filename: str, file_data: bytes
    ) -> ExpenseReport:
        """上传附件"""
        report = db.query(ExpenseReport).filter(ExpenseReport.id == report_id).first()
        if not report:
            raise ValueError("报销单不存在")

        # 保存到 uploads/ 目录
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(settings.UPLOAD_DIR, f"{report_id}_{filename}")
        with open(file_path, "wb") as f:
            f.write(file_data)

        report.attachment_path = file_path
        db.commit()
        db.refresh(report)
        return report
