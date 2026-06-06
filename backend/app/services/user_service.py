"""
用户管理业务逻辑 — CRUD + 分页 + 角色管理
"""
from sqlalchemy.orm import Session

from ..models.user import User
from ..utils.security import hash_password


class UserService:

    @staticmethod
    def list_users(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        role: str | None = None,
    ) -> list[User]:
        """用户列表 — 支持按角色筛选 + 分页"""
        query = db.query(User)
        if role:
            query = query.filter(User.role == role)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_user(db: Session, user_id: int) -> User | None:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def update_user(
        db: Session,
        user_id: int,
        full_name: str | None = None,
        email: str | None = None,
        role: str | None = None,
        department_id: int | None = None,
        is_active: bool | None = None,
        password: str | None = None,
    ) -> User:
        """更新用户信息 — 只更新传入的字段"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"用户 ID={user_id} 不存在")

        if full_name is not None:
            user.full_name = full_name
        if email is not None:
            # 检查邮箱唯一性（排除自己）
            existing = db.query(User).filter(User.email == email, User.id != user_id).first()
            if existing:
                raise ValueError(f"邮箱 '{email}' 已被其他用户使用")
            user.email = email
        if role is not None:
            user.role = role
        if department_id is not None:
            user.department_id = department_id
        if is_active is not None:
            user.is_active = is_active
        if password is not None:
            user.hashed_password = hash_password(password)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> None:
        """软删除 — 将用户设置为禁用状态"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"用户 ID={user_id} 不存在")
        user.is_active = False
        db.commit()
