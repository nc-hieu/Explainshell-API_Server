from typing import Optional
from datetime import datetime
from pydantic import BaseModel

# ==========================================
# 1. SCHEMA CƠ BẢN (Dùng chung)
# ==========================================
class ManPageBase(BaseModel):
    """Các trường thông tin cơ bản của một tài liệu Man Page"""
    section: Optional[int] = None         # Phần của tài liệu (VD: "1", "8", "3")
    content: str                          # Toàn văn nội dung tài liệu (Rất dài)
    source_url: Optional[str] = None      # Đường dẫn URL nguồn (Nếu crawl từ nơi khác về)


# ==========================================
# 2. SCHEMA GHI DỮ LIỆU (Request)
# ==========================================
class ManPageCreate(ManPageBase):
    """Schema dùng khi Admin tạo tài liệu mới cho 1 lệnh"""
    pass

class ManPageUpdate(BaseModel):
    """Schema dùng khi Admin cập nhật tài liệu (Các trường đều Optional)"""
    section: Optional[int] = None
    content: Optional[str] = None
    source_url: Optional[str] = None


# ==========================================
# 3. SCHEMA ĐỌC DỮ LIỆU (Response)
# ==========================================
class ManPage(ManPageBase):
    """Schema chuẩn trả về cho Frontend"""
    id: int
    program_id: int
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True # Giúp Pydantic V2 hiểu object SQLAlchemy