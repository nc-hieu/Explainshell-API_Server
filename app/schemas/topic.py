from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

# ==========================================
# 1. SCHEMA CƠ BẢN (Dùng chung)
# ==========================================
class TopicBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    is_featured: Optional[bool] = False

# ==========================================
# 2. SCHEMA GHI DỮ LIỆU (Request)
# ==========================================
class TopicCreate(TopicBase):
    """Schema dùng khi Admin tạo mới Topic"""
    pass

class TopicUpdate(BaseModel):
    """Schema dùng khi Admin cập nhật Topic (cho phép sửa từng trường riêng lẻ)"""
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    icon_url: Optional[str] = None
    is_featured: Optional[bool] = None

# ==========================================
# THÊM SCHEMA RÚT GỌN CỦA CATEGORY
# (Dùng để hiển thị các danh mục con trực thuộc khi truy vấn Topic)
# ==========================================
class CategoryInfoForTopic(BaseModel):
    id: int
    name: str
    slug: str
    icon_url: Optional[str] = None
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

# ==========================================
# 3. SCHEMA ĐỌC DỮ LIỆU (Response)
# ==========================================
class Topic(TopicBase):
    """Schema chuẩn trả về cho Frontend"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TopicWithCategories(Topic):
    """
    Schema mở rộng: Lấy thông tin Topic kèm theo danh sách các Category nằm trong đó.
    Rất hữu ích để vẽ màn hình Trang chủ (Hiển thị Topic -> Các danh mục con).
    """
    categories: List[CategoryInfoForTopic] = []

    class Config:
        from_attributes = True

class TopicStats(BaseModel):
    """Schema trả về thống kê số lượng của 1 Topic"""
    topic_id: int
    categories_count: int
    programs_count: int

class TopicBulkStatsRequest(BaseModel):
    """Schema dùng để nhận mảng ID khi thống kê hàng loạt bằng POST"""
    topic_ids: List[int]

class TopicWithRootCategories(Topic):
    """
    [MỚI]: Schema trả về thông tin Topic kèm theo CHỈ các danh mục GỐC (parent_id = null).
    """
    # Tái sử dụng Schema CategoryInfoForTopic đã định nghĩa ở phần trước
    categories: List[CategoryInfoForTopic] = []

    class Config:
        from_attributes = True