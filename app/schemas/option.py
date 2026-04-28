from typing import Optional
from pydantic import BaseModel

# ==========================================
# 1. SCHEMA CƠ BẢN (Dùng chung)
# ==========================================
class OptionBase(BaseModel):
    """Các trường thông tin cơ bản của một cờ lệnh"""
    short_name: Optional[str] = None      # Tên ngắn (VD: "-l")
    long_name: Optional[str] = None       # Tên dài (VD: "--all")
    description: str                      # Mô tả chi tiết chức năng của cờ lệnh
    is_deprecated: bool = False           # Đánh dấu cờ lệnh này đã lỗi thời hay chưa
    is_featured: bool = False             # Đánh dấu cờ lệnh nổi bật
    group_id: Optional[int] = None        # ID của nhóm cờ lệnh (Có thể null)


# ==========================================
# 2. SCHEMA GHI DỮ LIỆU (Request)
# ==========================================
class OptionCreate(OptionBase):
    """
    Schema dùng khi Admin tạo cờ lệnh mới.
    (Không cần program_id ở đây vì sẽ được lấy từ URL /programs/{id}/options)
    """
    pass

class OptionUpdate(BaseModel):
    """Schema dùng khi Admin cập nhật cờ lệnh (Mọi trường đều Optional)"""
    short_name: Optional[str] = None
    long_name: Optional[str] = None
    description: Optional[str] = None
    is_deprecated: Optional[bool] = None
    is_featured: Optional[bool] = None
    group_id: Optional[int] = None


# ==========================================
# 3. SCHEMA ĐỌC DỮ LIỆU (Response)
# ==========================================
class Option(OptionBase):
    """Schema chuẩn trả về cho Frontend"""
    id: int
    program_id: int

    class Config:
        from_attributes = True # Dùng cho Pydantic V2