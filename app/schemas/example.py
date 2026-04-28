from typing import Optional
from pydantic import BaseModel

# ==========================================
# 1. SCHEMA CƠ BẢN (Dùng chung)
# ==========================================
class ExampleBase(BaseModel):
    """Các trường thông tin cơ bản của một Ví dụ"""
    command_line: str                     # Câu lệnh ví dụ (VD: "ls -la /var/log")
    explanation: Optional[str] = None     # Giải thích câu lệnh này làm gì
    is_common: bool = True                # Đánh dấu đây là ví dụ phổ biến (hiện lên đầu)
    
    # Các khóa ngoại tùy chọn (để liên kết ví dụ này với 1 nhóm hoặc 1 cờ lệnh cụ thể)
    group_id: Optional[int] = None        
    option_id: Optional[int] = None       


# ==========================================
# 2. SCHEMA GHI DỮ LIỆU (Request)
# ==========================================
class ExampleCreate(ExampleBase):
    """
    Schema dùng khi Admin tạo Ví dụ mới.
    (program_id sẽ được lấy từ URL API)
    """
    pass

class ExampleUpdate(BaseModel):
    """Schema dùng khi Admin cập nhật Ví dụ (Tất cả đều Optional)"""
    command_line: Optional[str] = None
    explanation: Optional[str] = None
    is_common: Optional[bool] = None
    group_id: Optional[int] = None
    option_id: Optional[int] = None


# ==========================================
# 3. SCHEMA ĐỌC DỮ LIỆU (Response)
# ==========================================
class Example(ExampleBase):
    """Schema chuẩn trả về cho Frontend"""
    id: int
    program_id: int

    class Config:
        from_attributes = True # Dùng cho Pydantic V2