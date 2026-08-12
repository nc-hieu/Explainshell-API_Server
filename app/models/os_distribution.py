from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base

class OSDistribution(Base):
    __tablename__ = "os_distributions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    icon_url = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Quan hệ 1-N: 1 Hệ điều hành có nhiều Man Pages
    man_pages = relationship("ManPage", back_populates="os")