"""
报表 API — 费用统计 + CSV 导出
"""
import csv
import io

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..middleware.auth import get_current_user
from ..models.expense import ExpenseReport
from ..models.budget import Budget
from ..models.user import User

router = APIRouter(prefix="/api/v1/reports", tags=["报表"])


@router.get("/my-expenses")
def my_expenses(
    year: int | None = Query(None, description="年度"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """个人费用统计 — 按费用类型汇总"""
    query = db.query(
        ExpenseReport.expense_type_id,
        func.count(ExpenseReport.id).label("count"),
        func.sum(ExpenseReport.amount).label("total_amount"),
    ).filter(ExpenseReport.submitter_id == current_user.id)

    if year:
        query = query.filter(func.strftime("%Y", ExpenseReport.created_at) == str(year))

    rows = query.group_by(ExpenseReport.expense_type_id).all()
    return [
        {"expense_type_id": r.expense_type_id, "count": r.count, "total_amount": float(r.total_amount or 0)}
        for r in rows
    ]


@router.get("/budget-execution")
def budget_execution(
    year: int | None = Query(None),
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """预算执行报表"""
    query = db.query(Budget)
    if year:
        query = query.filter(Budget.year == year)
    budgets = query.all()

    return [
        {
            "id": b.id,
            "department_id": b.department_id,
            "year": b.year,
            "amount": b.amount,
            "used_amount": b.used_amount,
            "execution_rate": round(b.used_amount / b.amount * 100, 1) if b.amount > 0 else 0,
        }
        for b in budgets
    ]


@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """仪表盘汇总数据"""
    # 本月报销总额
    import datetime
    now = datetime.datetime.now()
    month_start = now.replace(day=1).strftime("%Y-%m-%d")
    month_total = (
        db.query(func.sum(ExpenseReport.amount))
        .filter(ExpenseReport.created_at >= month_start)
        .scalar()
    ) or 0

    # 待审批数量
    pending_count = (
        db.query(func.count(ExpenseReport.id))
        .filter(ExpenseReport.status == "submitted")
        .scalar()
    ) or 0

    # 预算总数
    budget_count = db.query(func.count(Budget.id)).scalar() or 0

    return {
        "month_total": float(month_total),
        "pending_count": pending_count,
        "budget_count": budget_count,
    }


@router.get("/export")
def export_csv(
    year: int | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """导出报销单为 CSV"""
    query = db.query(ExpenseReport).filter(ExpenseReport.submitter_id == current_user.id)
    if year:
        query = query.filter(func.strftime("%Y", ExpenseReport.created_at) == str(year))

    reports = query.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["报销单号", "事由", "金额", "状态", "费用类型", "创建时间"])
    for r in reports:
        writer.writerow([r.report_no, r.title, r.amount, r.status, r.expense_type_id, r.created_at])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=expenses.csv"},
    )
