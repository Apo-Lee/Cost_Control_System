"""
预算 Schema
"""
from datetime import datetime

from pydantic import BaseModel, Field


class BudgetCreate(BaseModel):
    """创建预算"""
    department_id: int
    expense_type_id: int
    year: int = Field(..., ge=2024, le=2099)
    quarter: int | None = Field(None, ge=1, le=4)
    amount: float = Field(..., gt=0, description="预算金额")


class BudgetAdjustRequest(BaseModel):
    """预算调整"""
    adjustment_amount: float = Field(..., description="调整金额（正=追加，负=调减）")
    reason: str = Field(..., min_length=1, max_length=500)


class BudgetResponse(BaseModel):
    """预算响应"""
    id: int
    department_id: int
    expense_type_id: int
    year: int
    quarter: int | None = None
    amount: float
    used_amount: float
    status: str
    created_by: int
    created_at: datetime

    model_config = {"from_attributes": True}
