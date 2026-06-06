"""
用户管理 API — 仅管理员可操作
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..database import get_db
from ..middleware.auth import get_current_user
from ..models.user import User
from ..schemas.user import UserResponse
from ..services.user_service import UserService
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/users", tags=["用户管理"])


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """权限校验：仅 admin 角色可操作"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅管理员可执行此操作",
        )
    return current_user


@router.get("", response_model=list[UserResponse])
def list_users(
    skip: int = Query(0, ge=0, description="跳过条数"),
    limit: int = Query(20, ge=1, le=100, description="每页条数"),
    role: str | None = Query(None, description="按角色筛选"),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """用户列表 — 分页 + 按角色筛选"""
    return UserService.list_users(db, skip=skip, limit=limit, role=role)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    user = UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    full_name: str | None = None,
    email: str | None = None,
    role: str | None = None,
    department_id: int | None = None,
    is_active: bool | None = None,
    password: str | None = None,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """更新用户 — 仅管理员"""
    try:
        return UserService.update_user(
            db, user_id,
            full_name=full_name, email=email, role=role,
            department_id=department_id, is_active=is_active, password=password,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """禁用用户（软删除）"""
    try:
        UserService.delete_user(db, user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
