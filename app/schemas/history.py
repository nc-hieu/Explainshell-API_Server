from enum import Enum
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.schemas.program import ProgramShort

# ==========================================
# 0. ENUM VÀ SCHEMA HỖ TRỢ
# ==========================================
class HistoryStatus(str, Enum):
    FOUND = "FOUND"
    PARTIAL = "PARTIAL"
    NOT_FOUND = "NOT_FOUND"

class HistoryStatusSummary(BaseModel):
    FOUND: int = 0
    PARTIAL: int = 0
    NOT_FOUND: int = 0
    TOTAL: int = 0

# ==========================================
# 1. SCHEMA CƠ BẢN (Dùng chung)
# ==========================================
class HistoryBase(BaseModel):
    command_text: str
    status: Optional[str] = "FOUND"

# ==========================================
# 2. SCHEMA GHI DỮ LIỆU (Request)
# ==========================================
class HistoryCreate(HistoryBase):
    """
    Schema dùng khi tạo lịch sử mới (Mỗi khi user search trên web).
    (user_id sẽ được lấy tự động từ hệ thống Auth, không bắt user truyền lên)
    """
    program_ids: List[int] = []
# LƯU Ý: Không có HistoryUpdate vì lịch sử đã tạo ra thì không nên sửa chữa

# ==========================================
# 3. SCHEMA ĐỌC DỮ LIỆU (Response)
# ==========================================
class History(HistoryBase):
    """Schema trả về cho Frontend hiển thị"""
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    # Trả về danh sách các lệnh liên quan (VD: [{name: "tar", ...}, {name: "ssh", ...}])
    programs: List[ProgramShort] = []

    class Config:
        from_attributes = True # Dùng cho Pydantic V2


