from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

# Import class Base của hệ thống
from app.db.session import Base

class History(Base):
    __tablename__ = "histories"

    id = Column(Integer, primary_key=True, index=True)
    
    # Khóa ngoại
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True)
    program_id = Column(Integer, ForeignKey("programs.id", ondelete="SET NULL"), index=True, nullable=True)
    
    command_text = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="FOUND")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Quan hệ
    user = relationship("User", back_populates="histories")
    program = relationship("Program", back_populates="histories")

    def __repr__(self):
        return f"<History(user_id={self.user_id}, query='{self.command_text[:20]}...')>"
