from sqlalchemy import Column, Integer, String, Boolean, CheckConstraint, DateTime, func
from sqlalchemy.orm import relationship

from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True) 
    email = Column(String(100), unique=True, nullable=False, index=True) 
    password = Column(String(255), nullable=False) 
    
    # Phân quyền với giá trị mặc định là 'user'
    roles = Column(String(20), nullable=False, default="user") 
    
    is_active = Column(Boolean, default=True) 
    created_at = Column(DateTime, server_default=func.now())

    # Ràng buộc CHECK để đảm bảo roles chỉ nhận 'user' hoặc 'admin' 
    __table_args__ = (
        CheckConstraint("roles IN ('user', 'admin')", name="check_user_roles"),
    )

    # Quan hệ 1-N: Một người dùng có thể có nhiều lịch sử truy vấn
    histories = relationship("History", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.roles}')>"