"""
报销单 Schema
"""
from datetime import datetime

from pydantic import BaseModel, Field


class ExpenseCreate(BaseModel):
    """创建报销单"""
    department_id: int
    expense_type_id: int
    title: str = Field(..., min_length=1, max_length=200, description="报销事由")
    amount: float = Field(..., gt=0, description="报销金额")
    description: str | None = Field(None, max_length=500, description="详细说明")


class ExpenseResponse(BaseModel):
    """报销单响应"""
    id: int
    report_no: str
    submitter_id: int
    department_id: int
    expense_type_id: int
    title: str
    amount: float
    description: str | None = None
    attachment_path: str | None = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
