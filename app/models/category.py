from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Table, DateTime, func
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship, backref
from app.db.session import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(150), unique=True, nullable=False, index=True)
    description = Column(Text)
    icon_url = Column(String(255))
    is_featured = Column(Boolean, default=False)
    
    # Quan hệ cha-con (Self-referencing)
    parent_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    
    # Vector tìm kiếm
    fts_category_vector = Column(TSVECTOR)
    
    updated_at = Column(DateTime, server_default=func.now())

    # Định nghĩa quan hệ phân cấp
    subcategories = relationship(
        "Category", 
        backref=backref('parent', remote_side=[id]),
        cascade="all, delete"
    )

    # Quan hệ nhiều-nhiều với Program
    programs = relationship("Program", secondary="program_categories", back_populates="categories")

    def __repr__(self):
        return f"<Category(name='{self.name}', slug='{self.slug}')>"