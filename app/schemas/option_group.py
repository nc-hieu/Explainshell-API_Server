from typing import Optional
from pydantic import BaseModel

# ==========================================
# 1. SCHEMA CƠ BẢN (Dùng chung)
# ==========================================
class OptionGroupBase(BaseModel):
    """Các trường thông tin cơ bản của một nhóm cờ lệnh"""
    title: str # Tiêu đề nhóm (VD: "Formatting Options")
    description: Optional[str] = None # Mô tả thêm về nhóm này
    sort_order: int = 0 # Thứ tự hiển thị (Số nhỏ hơn hiện trước)


# ==========================================
# 2. SCHEMA GHI DỮ LIỆU (Request)
# ==========================================
class OptionGroupCreate(OptionGroupBase):
    """
    Schema dùng khi Admin tạo một nhóm mới.
    (Không cần program_id ở đây vì nó sẽ được truyền trên URL API)
    """
    pass

class OptionGroupUpdate(BaseModel):
    """Schema dùng khi Admin cập nhật nhóm (Các trường đều Optional)"""
    title: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None


# ==========================================
# 3. SCHEMA ĐỌC DỮ LIỆU (Response)
# ==========================================
class OptionGroup(OptionGroupBase):
    """Schema chuẩn dùng để trả dữ liệu về cho Frontend"""
    id: int
    program_id: int

    class Config:
        from_attributes = True # Dùng cho Pydantic V2 để chuyển đổi object từ Database