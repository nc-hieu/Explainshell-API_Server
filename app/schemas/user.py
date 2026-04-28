from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr

# ==========================================
# 1. SCHEMA CƠ BẢN (Dùng chung)
# ==========================================
class UserBase(BaseModel):
    """Các thông tin công khai cơ bản của User"""
    username: str
    email: EmailStr # EmailStr tự động kiểm tra định dạng email hợp lệ (cần cài thư viện email-validator)
    is_active: Optional[bool] = True
    roles: Optional[str] = "user" # Mặc định khi tạo mới luôn là 'user'


# ==========================================
# 2. SCHEMA GHI DỮ LIỆU (Request)
# ==========================================
class UserCreate(UserBase):
    """Schema dùng khi Đăng ký / Tạo tài khoản mới (Bắt buộc có password)"""
    password: str

class UserUpdate(BaseModel):
    """Schema dùng khi cập nhật thông tin (Admin hoặc chính User tự sửa)"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None # Nếu truyền lên password mới thì sẽ được hash lại
    is_active: Optional[bool] = None
    roles: Optional[str] = None


# ==========================================
# 3. SCHEMA ĐỌC DỮ LIỆU (Response)
# ==========================================
class UserResponse(UserBase):
    """
    Schema dùng để trả dữ liệu về qua API. 
    LƯU Ý: KHÔNG CÓ trường `password` ở đây để bảo mật.
    """
    id: int
    created_at: datetime

    class Config:
        from_attributes = True # Giúp Pydantic đọc được object từ Database