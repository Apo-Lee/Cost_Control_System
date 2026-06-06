"""
认证业务逻辑 — 注册、登录
处于 api 路由和 database 之间，处理业务规则
"""
from sqlalchemy.orm import Session

from ..models.user import User
from ..utils.security import create_access_token, hash_password, verify_password


class AuthService:
    """认证服务 — 无状态，所有方法为静态方法"""

    @staticmethod
    def register(db: Session, username: str, email: str, password: str, full_name: str) -> User:
        """注册新用户 — 校验唯一性后创建"""
        # 检查用户名是否已存在
        if db.query(User).filter(User.username == username).first():
            raise ValueError(f"用户名 '{username}' 已被占用")
        if db.query(User).filter(User.email == email).first():
            raise ValueError(f"邮箱 '{email}' 已被注册")

        user = User(
            username=username,
            email=email,
            hashed_password=hash_password(password),  # 存哈希，不存明文
            full_name=full_name,
            role="employee",  # 默认注册为普通员工
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def login(db: Session, username: str, password: str) -> dict:
        """
        登录验证
        成功返回 {"access_token": "...", "token_type": "bearer"}
        失败抛出 ValueError
        """
        # 查找用户
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise ValueError("用户名或密码错误")
        if not user.is_active:
            raise ValueError("账号已被禁用，请联系管理员")

        # 验证密码
        if not verify_password(password, user.hashed_password):
            raise ValueError("用户名或密码错误")

        # 生成 JWT
        access_token = create_access_token(data={"sub": user.username})
        return {"access_token": access_token, "token_type": "bearer"}
