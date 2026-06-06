"""
审批 Schema
"""
from datetime import datetime

from pydantic import BaseModel, Field


class ApprovalActionRequest(BaseModel):
    """审批操作请求"""
    action: str = Field(..., pattern="^(approved|rejected)$", description="approved=通过, rejected=驳回")
    comment: str | None = Field(None, max_length=500, description="审批意见")


class ApprovalRecordResponse(BaseModel):
    """审批记录响应"""
    id: int
    target_type: str
    target_id: int
    approver_id: int
    level: int
    action: str
    comment: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PendingItem(BaseModel):
    """待审批项"""
    id: int
    target_type: str
    target_id: int
    title: str
    amount: float
    submitter_name: str
    submitted_at: datetime | None = None
