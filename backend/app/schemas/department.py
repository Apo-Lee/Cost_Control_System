"""
部门 Schema
"""
from datetime import datetime

from pydantic import BaseModel, Field


class DepartmentCreate(BaseModel):
    """创建部门请求"""
    name: str = Field(..., min_length=1, max_length=100)
    parent_id: int | None = Field(None, description="上级部门ID")


class DepartmentResponse(BaseModel):
    """部门响应"""
    id: int
    name: str
    parent_id: int | None = None
    manager_id: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
