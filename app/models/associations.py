from sqlalchemy import Table, Column, Integer, ForeignKey, DateTime, func
from app.db.session import Base

program_categories = Table(
    "program_categories",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("program_id", Integer, ForeignKey("programs.id", ondelete="CASCADE"), nullable=False), 
    Column("category_id", Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False), 
    Column("created_at", DateTime, server_default=func.now()) 
)