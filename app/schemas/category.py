from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

# ==========================================
# SCHEMA RÚT GỌN NÀY LÊN ĐẦU HOẶC GIỮA FILE
# (Dùng để hiển thị thông tin Program cơ bản nằm trong Category)
# ==========================================
class ProgramInfoForCategory(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None # Lấy thêm mô tả ngắn gọn của lệnh
    
    class Config:
        from_attributes = True

# ==========================================
# 1. SCHEMA CƠ BẢN (Dùng chung)
# ==========================================
class CategoryBasic(BaseModel):
    """
    Schema siêu nhẹ chỉ trả về thông tin danh mục.
    Dùng cho các hàm danh sách (như lấy roots) để không bị phình to dữ liệu.
    """
    id: int
    name: str
    slug: str # Đường dẫn thân thiện (VD: 'file-system')
    description: Optional[str] = None
    icon_url: Optional[str] = None
    is_featured: bool = False
    
    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    """Các trường dữ liệu cơ bản của một danh mục"""
    name: str
    slug: str # Đường dẫn thân thiện (VD: 'file-system')
    description: Optional[str] = None
    icon_url: Optional[str] = None
    is_featured: bool = False
    parent_id: Optional[int] = None # ID của danh mục cha (Nếu là Null thì đây là danh mục gốc)


# ==========================================
# 2. SCHEMA GHI DỮ LIỆU (Request)
# ==========================================
class CategoryCreate(CategoryBase):
    """Schema dùng khi Admin tạo danh mục mới"""
    pass

class CategoryUpdate(BaseModel):
    """Schema dùng khi Admin cập nhật danh mục (Tất cả đều Optional)"""
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    icon_url: Optional[str] = None
    is_featured: Optional[bool] = None
    parent_id: Optional[int] = None


# ==========================================
# 3. SCHEMA ĐỌC DỮ LIỆU (Response)
# ==========================================
class Category(CategoryBase):
    """Schema chuẩn trả về cho Frontend"""
    id: int
    updated_at: Optional[datetime] = None

    programs: List[ProgramInfoForCategory] = []

    class Config:
        from_attributes = True # Dành cho Pydantic V2 để đọc Object SQLAlchemy

class CategoryWithSub(Category):
    """
    Schema nâng cao: Đệ quy để lấy nhiều cấp danh mục.
    Bậc 1 sẽ chứa Bậc 2, Bậc 2 sẽ chứa Bậc 3...
    """
    # LƯU Ý KỸ: Có dấu nháy đơn bao quanh 'CategoryWithSub' để Pydantic hiểu đây là gọi lại chính nó
    subcategories: List['CategoryWithSub'] = [] 

    class Config:
        from_attributes = True


class CategoryStats(BaseModel):
    """Schema trả về thống kê số lượng của 1 danh mục"""
    category_id: int
    subcategories_count: int
    programs_count: int

class CategoryBulkStatsRequest(BaseModel):
    """Schema dùng để nhận mảng ID khi thống kê hàng loạt"""
    category_ids: List[int]