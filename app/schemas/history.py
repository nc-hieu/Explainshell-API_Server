from typing import Optional
from datetime import datetime
from pydantic import BaseModel

# ==========================================
# 1. SCHEMA CƠ BẢN (Dùng chung)
# ==========================================
class HistoryBase(BaseModel):
    """Các trường dữ liệu cơ bản của một bản ghi lịch sử"""
    command_text: str                     # Câu lệnh người dùng đã tra cứu (VD: "ls -la")
    explanation: Optional[str] = None     # Kết quả giải thích ngắn gọn (nếu có lưu lại)


# ==========================================
# 2. SCHEMA GHI DỮ LIỆU (Request)
# ==========================================
class HistoryCreate(HistoryBase):
    """
    Schema dùng khi tạo lịch sử mới (Mỗi khi user search trên web).
    (user_id sẽ được lấy tự động từ hệ thống Auth, không bắt user truyền lên)
    """
    pass

# LƯU Ý: Không có HistoryUpdate vì lịch sử đã tạo ra thì không nên sửa chữa.


# ==========================================
# 3. SCHEMA ĐỌC DỮ LIỆU (Response)
# ==========================================
class History(HistoryBase):
    """Schema chuẩn trả về cho Frontend"""
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True # Dùng cho Pydantic V2