from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

# Import class Base của hệ thống
from app.db.session import Base

class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    
    # Khóa ngoại liên kết tới User và Program. 
    # ondelete="CASCADE": Nếu User bị xóa hoặc Lệnh bị xóa, dòng Yêu thích này tự động biến mất!
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    program_id = Column(Integer, ForeignKey("programs.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Thời gian thả tim
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # ==========================================
    # RÀNG BUỘC (CONSTRAINTS)
    # ==========================================
    # Đảm bảo 1 người dùng (user_id) chỉ có thể yêu thích 1 lệnh (program_id) ĐÚNG 1 LẦN.
    # Nếu vi phạm, PostgreSQL sẽ ném ra lỗi IntegrityError ngay lập tức.
    __table_args__ = (
        UniqueConstraint('user_id', 'program_id', name='uix_user_program_favorite'),
    )

    # ==========================================
    # QUAN HỆ (RELATIONSHIPS)
    # ==========================================
    # Giúp SQLAlchemy biết đường "kéo" dữ liệu của Program lên khi gọi hàm selectinload()
    program = relationship("Program")
    
    # (Tùy chọn) Kéo thông tin User nếu cần
    user = relationship("User")