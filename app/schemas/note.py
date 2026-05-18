from typing import Optional
from datetime import datetime
from pydantic import BaseModel

# ==========================================
# 1. SCHEMA CƠ BẢN
# ==========================================
class NoteBase(BaseModel):
    title: str
    content: str

# ==========================================
# 2. SCHEMA GHI DỮ LIỆU
# ==========================================
class NoteCreate(NoteBase):
    """Admin tạo Note mới (Cần truyền program_id)"""
    program_id: int

class NoteUpdate(BaseModel):
    """Admin cập nhật Note"""
    title: Optional[str] = None
    content: Optional[str] = None
    program_id: Optional[int] = None

# ==========================================
# 3. SCHEMA ĐỌC DỮ LIỆU
# ==========================================
class Note(NoteBase):
    """Schema trả về cho Frontend"""
    id: int
    program_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True