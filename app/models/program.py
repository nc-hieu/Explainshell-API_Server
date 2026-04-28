from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship

from app.db.session import Base

class Program(Base):
    """
    Ánh xạ bảng 'programs' từ PostgreSQL sang SQLAlchemy Model.
    """
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True) 
    name = Column(String(100), unique=True, nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_featured = Column(Boolean, default=False) 
    
    # created_at dùng server_default để PostgreSQL tự điền thời gian hiện tại
    created_at = Column(DateTime, server_default=func.now())
    
    # updated_at sẽ được cập nhật bởi Trigger 'trg_programs_updated_at' đã tạo trong DB
    updated_at = Column(DateTime, server_default=func.now())

    # Cột dùng cho Full-text Search (PostgreSQL specific)
    fts_program_vector = Column(TSVECTOR) 

    # Thiết lập mối quan hệ (Relationships)
    
    # 1. Quan hệ với Category (Nhiều - Nhiều)
    categories = relationship("Category", secondary="program_categories", back_populates="programs")
    
    # 2. Quan hệ với Option Group (1 Program có nhiều Option Groups)
    option_groups = relationship("OptionGroup", back_populates="program", cascade="all, delete-orphan")
    
    # 3. Quan hệ với Option (1 Program có nhiều Options)
    options = relationship("Option", back_populates="program", cascade="all, delete-orphan")
    
    # 4. Quan hệ với Example (1 Program có nhiều Examples)
    examples = relationship("Example", back_populates="program", cascade="all, delete-orphan")
    
    # 5. Quan hệ với Man Page (1 Program có nhiều Sections trong Man Page)
    man_pages = relationship("ManPage", back_populates="program", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Program(name='{self.name}')>"