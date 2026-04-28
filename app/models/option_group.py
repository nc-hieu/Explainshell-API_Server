from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class OptionGroup(Base):
    __tablename__ = "option_groups"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    sort_order = Column(Integer, default=0)

    # Quan hệ ngược lại với Program
    program = relationship("Program", back_populates="option_groups")
    
    # 1 Nhóm có thể chứa nhiều Option và nhiều Example
    options = relationship("Option", back_populates="group", cascade="all, delete-orphan")
    examples = relationship("Example", back_populates="group", cascade="all, delete-orphan")