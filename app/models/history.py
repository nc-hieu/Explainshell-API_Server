from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base

# BẢNG TRUNG GIAN (Junction Table)
history_programs = Table(
    "history_programs",
    Base.metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("history_id", Integer, ForeignKey("histories.id", ondelete="CASCADE"), nullable=False),
    Column("program_id", Integer, ForeignKey("programs.id", ondelete="CASCADE"), nullable=False),
    Column("created_at", DateTime(timezone=True), server_default=func.now())
)

class History(Base):
    __tablename__ = "histories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True)
    command_text = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="FOUND")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Quan hệ
    user = relationship("User", back_populates="histories")
    
    # Liên kết Nhiều-Nhiều với bảng Program thông qua history_programs
    programs = relationship("Program", secondary=history_programs, back_populates="histories")