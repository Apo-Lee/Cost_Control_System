"""
费用报销 API — CRUD + 文件上传
"""
import os

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..middleware.auth import get_current_user
from ..models.expense import ExpenseReport
from ..models.user import User
from ..schemas.expense import ExpenseCreate, ExpenseResponse
from ..services.expense_service import ExpenseService

router = APIRouter(prefix="/api/v1/expenses", tags=["费用报销"])


@router.get("", response_model=list[ExpenseResponse])
def list_expenses(
    status: str | None = Query(None, description="状态筛选"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """我的报销单列表"""
    query = db.query(ExpenseReport).filter(
        ExpenseReport.submitter_id == current_user.id
    )
    if status:
        query = query.filter(ExpenseReport.status == status)
    return query.order_by(ExpenseReport.created_at.desc()).offset(skip).limit(limit).all()


@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    body: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建报销单（草稿）"""
    return ExpenseService.create_expense(
        db=db,
        submitter_id=current_user.id,
        department_id=body.department_id,
        expense_type_id=body.expense_type_id,
        title=body.title,
        amount=body.amount,
        description=body.description,
    )


@router.get("/{report_id}", response_model=ExpenseResponse)
def get_expense(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = db.query(ExpenseReport).filter(ExpenseReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="报销单不存在")
    return report


@router.post("/{report_id}/submit", response_model=ExpenseResponse)
def submit_expense(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """提交报销单"""
    try:
        return ExpenseService.submit_expense(db, report_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{report_id}/upload")
def upload_attachment(
    report_id: int,
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """上传发票附件"""
    try:
        file_data = file.file.read()
        ExpenseService.upload_attachment(db, report_id, file.filename, file_data)
        return {"message": "上传成功", "filename": file.filename}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{report_id}/download")
def download_attachment(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """下载发票附件"""
    report = db.query(ExpenseReport).filter(ExpenseReport.id == report_id).first()
    if not report or not report.attachment_path:
        raise HTTPException(status_code=404, detail="附件不存在")
    if not os.path.exists(report.attachment_path):
        raise HTTPException(status_code=404, detail="文件已丢失")
    return FileResponse(report.attachment_path)
