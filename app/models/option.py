from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship
from app.db.session import Base

class Option(Base):
    __tablename__ = "options"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id", ondelete="CASCADE"), nullable=False) 
    
    # Khóa ngoại trỏ đến nhóm cờ lệnh (Có thể null nếu cờ lệnh không thuộc nhóm nào)
    group_id = Column(Integer, ForeignKey("option_groups.id", ondelete="SET NULL"))
    
    short_name = Column(String(10))
    long_name = Column(String(50)) 
    description = Column(Text, nullable=False) 
    
    is_deprecated = Column(Boolean, default=False) 
    is_featured = Column(Boolean, default=False)
    
    # Cột vector tìm kiếm nâng cao 
    fts_option_vector = Column(TSVECTOR) 

    # Đảm bảo tính duy nhất: Một lệnh không thể có 2 option trùng cả tên ngắn và dài 
    __table_args__ = (
        UniqueConstraint('program_id', 'short_name', 'long_name', name='uix_program_option_names'),
    )

    # Quan hệ N-1: Nhiều options thuộc về một Program
    program = relationship("Program", back_populates="options")

    # Quan hệ N-1: Nhiều options có thể thuộc về một OptionGroup
    group = relationship("OptionGroup", back_populates="options")

    def __repr__(self):
        return f"<Option(name='{self.short_name or self.long_name}', program_id={self.program_id})>"