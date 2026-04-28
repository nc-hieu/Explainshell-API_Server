from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, func, String
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship
from app.db.session import Base

class ManPage(Base):
    __tablename__ = "man_pages"

    id = Column(Integer, primary_key=True, index=True)
    # Quan hệ 1 - N: Mỗi chương trình nhiều trang man
    program_id = Column(Integer, ForeignKey("programs.id", ondelete="CASCADE"), nullable=False)
    section = Column(Integer)
    content = Column(Text, nullable=False)
    source_url = Column(String(255))

    # Vector tìm kiếm cho toàn bộ nội dung man page
    fts_doc_vector = Column(TSVECTOR)
    
    updated_at = Column(DateTime, server_default=func.now())

    # Quan hệ ngược lại với Program
    program = relationship("Program", back_populates="man_pages")

    def __repr__(self):
        return f"<ManPage(program_id={self.program_id})>"