from sqlalchemy import Column, Integer, Text, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TSVECTOR
from app.db.session import Base

class ManPage(Base):
    __tablename__ = "man_pages"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id", ondelete="CASCADE"), nullable=False, index=True)
    os_id = Column(Integer, ForeignKey("os_distributions.id", ondelete="SET NULL"), index=True)
    
    section = Column(Integer)
    content = Column(Text)
    source_url = Column(String(255))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    fts_doc_vector = Column(TSVECTOR)

    # Quan hệ
    program = relationship("Program", back_populates="man_pages")
    os = relationship("OSDistribution", back_populates="man_pages")