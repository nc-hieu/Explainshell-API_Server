from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TSVECTOR
from app.db.session import Base

class Example(Base):
    __tablename__ = "examples"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id", ondelete="CASCADE"), nullable=False)
    group_id = Column(Integer, ForeignKey("option_groups.id", ondelete="SET NULL"))
    option_id = Column(Integer, ForeignKey("options.id", ondelete="SET NULL"))
    
    command_line = Column(Text, nullable=False)
    explanation = Column(Text)
    is_common = Column(Boolean, default=True)
    
    fts_example_vector = Column(TSVECTOR)

    # Các relationships
    program = relationship("Program", back_populates="examples")
    group = relationship("OptionGroup", back_populates="examples")
    option = relationship("Option") # Trỏ đến Option cụ thể nếu ví dụ này là của riêng 1 cờ lệnh