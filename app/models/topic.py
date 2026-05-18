from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

# Import class Base của hệ thống
from app.db.session import Base

class Topic(Base):
    __tablename__ = "topics" # Tên bảng chuẩn theo script của bạn

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text)
    icon_url = Column(String(255))
    is_featured = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # ==========================================
    # QUAN HỆ (RELATIONSHIPS)
    # ==========================================
    # Một Topic có thể chứa nhiều Categories. Khi Topic bị xóa, tùy thuộc vào setup nhưng thường các Category sẽ bị xóa theo (CASCADE)
    categories = relationship("Category", back_populates="topic", cascade="all, delete-orphan")