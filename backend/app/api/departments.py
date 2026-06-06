"""
部门管理 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..middleware.auth import get_current_user
from ..models.department import Department
from ..models.user import User
from ..schemas.department import DepartmentCreate, DepartmentResponse

router = APIRouter(prefix="/api/v1/departments", tags=["部门管理"])


@router.get("", response_model=list[DepartmentResponse])
def list_departments(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """获取所有部门"""
    return db.query(Department).all()


@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(
    body: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建部门 — 需要登录"""
    dept = Department(name=body.name, parent_id=body.parent_id)
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


@router.get("/{dept_id}", response_model=DepartmentResponse)
def get_department(
    dept_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="部门不存在")
    return dept
