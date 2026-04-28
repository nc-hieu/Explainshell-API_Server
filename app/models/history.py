from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.session import Base

class History(Base):
    __tablename__ = "histories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    command_text = Column(Text, nullable=False)
    explanation = Column(Text)

    created_at = Column(DateTime, server_default=func.now())

    # Quan hệ N-1: Nhiều lịch sử thuộc về 1 người dùng
    user = relationship("User", back_populates="histories")

    def __repr__(self):
        return f"<History(user_id={self.user_id}, query='{self.command_text[:20]}...')>"