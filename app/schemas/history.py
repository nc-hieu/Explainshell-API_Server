from typing import Optional
from datetime import datetime
from pydantic import BaseModel

# ==========================================
# 1. SCHEMA CƠ BẢN (Dùng chung)
# ==========================================
class HistoryBase(BaseModel):
    command_text: str
    status: Optional[str] = "FOUND"
    program_id: Optional[int] = None

# ==========================================
# 2. SCHEMA GHI DỮ LIỆU (Request)
# ==========================================
class HistoryCreate(HistoryBase):
    """
    Schema dùng khi tạo lịch sử mới (Mỗi khi user search trên web).
    (user_id sẽ được lấy tự động từ hệ thống Auth, không bắt user truyền lên)
    """
    pass
# LƯU Ý: Không có HistoryUpdate vì lịch sử đã tạo ra thì không nên sửa chữa

# ==========================================
# 3. SCHEMA ĐỌC DỮ LIỆU (Response)
# ==========================================
class History(HistoryBase):
    """Schema trả về cho Frontend hiển thị"""
    id: int
    user_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True # Dùng cho Pydantic V2


