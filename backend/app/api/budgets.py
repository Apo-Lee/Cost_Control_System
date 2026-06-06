"""
预算管理 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..middleware.auth import get_current_user
from ..models.user import User
from ..models.budget import Budget
from ..schemas.budget import BudgetCreate, BudgetAdjustRequest, BudgetResponse

router = APIRouter(prefix="/api/v1/budgets", tags=["预算管理"])


@router.get("", response_model=list[BudgetResponse])
def list_budgets(
    year: int | None = Query(None, description="年度"),
    department_id: int | None = Query(None, description="部门ID"),
    status: str | None = Query(None, description="状态"),
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """预算列表 — 支持按年度、部门、状态筛选"""
    query = db.query(Budget)
    if year:
        query = query.filter(Budget.year == year)
    if department_id:
        query = query.filter(Budget.department_id == department_id)
    if status:
        query = query.filter(Budget.status == status)
    return query.all()


@router.post("", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budget(
    body: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建预算（草稿状态）"""
    budget = Budget(
        department_id=body.department_id,
        expense_type_id=body.expense_type_id,
        year=body.year,
        quarter=body.quarter,
        amount=body.amount,
        created_by=current_user.id,
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


@router.get("/{budget_id}", response_model=BudgetResponse)
def get_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="预算不存在")
    return budget


@router.post("/{budget_id}/submit", response_model=BudgetResponse)
def submit_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """提交预算审批"""
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="预算不存在")
    if budget.status != "draft":
        raise HTTPException(status_code=400, detail="仅草稿状态的预算可提交")
    budget.status = "submitted"
    db.commit()
    db.refresh(budget)
    return budget


@router.post("/{budget_id}/adjust", response_model=BudgetResponse)
def adjust_budget(
    budget_id: int,
    body: BudgetAdjustRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """预算调整 — 记录调整历史 + 更新金额"""
    from ..models.budget import BudgetAdjustment

    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="预算不存在")

    # 记录调整历史
    adj = BudgetAdjustment(
        budget_id=budget_id,
        adjustment_amount=body.adjustment_amount,
        reason=body.reason,
        created_by=current_user.id,
    )
    db.add(adj)

    # 更新预算金额
    budget.amount += body.adjustment_amount
    db.commit()
    db.refresh(budget)
    return budget


@router.get("/alerts/list", response_model=list[BudgetResponse])
def budget_alerts(
    threshold: float = Query(0.8, description="预警阈值（执行率）"),
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """预算预警 — 执行率超过阈值的预算"""
    budgets = db.query(Budget).filter(
        Budget.status == "approved",
        Budget.amount > 0,
        Budget.used_amount / Budget.amount >= threshold,
    ).all()
    return budgets
