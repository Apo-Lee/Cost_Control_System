"""
审批 API — 待审批列表、通过/驳回、审批历史
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..middleware.auth import get_current_user
from ..models.user import User
from ..schemas.approval import ApprovalActionRequest, ApprovalRecordResponse, PendingItem
from ..services.approval_service import ApprovalService

router = APIRouter(prefix="/api/v1/approvals", tags=["审批"])


@router.get("/pending", response_model=list[PendingItem])
def pending_list(
    target_type: str | None = Query(None, description="审批类型: expense_report / budget"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """我的待审批列表"""
    return ApprovalService.get_pending(db, current_user.id, target_type)


@router.post("/{target_type}/{target_id}/approve")
def approve(
    target_type: str,
    target_id: int,
    body: ApprovalActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """审批操作 — 通过或驳回"""
    try:
        if body.action == "approved":
            return ApprovalService.approve(
                db, target_type, target_id, current_user.id, body.comment
            )
        else:
            return ApprovalService.reject(
                db, target_type, target_id, current_user.id, body.comment
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history/{target_type}/{target_id}", response_model=list[ApprovalRecordResponse])
def approval_history(
    target_type: str,
    target_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """审批历史"""
    return ApprovalService.get_history(db, target_type, target_id)
