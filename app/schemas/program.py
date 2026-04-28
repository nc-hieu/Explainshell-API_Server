from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

# LƯU Ý: Để dùng được ProgramDetail ở cuối file, 
# bạn cần đảm bảo đã có các file schema cơ bản cho các bảng liên quan.
# Nếu chưa có, bạn tạm thời comment các dòng import và các trường List[...] ở class ProgramDetail lại nhé.
from app.schemas.category import Category
from app.schemas.option_group import OptionGroup
from app.schemas.option import Option
from app.schemas.example import Example

# ==========================================
# THÊM SCHEMA RÚT GỌN NÀY LÊN ĐẦU HOẶC GIỮA FILE
# (Dùng để hiển thị thông tin Category mà không cần import từ category.py)
# ==========================================
class CategoryInfoForProgram(BaseModel):
    id: int
    name: str
    slug: str
    
    class Config:
        from_attributes = True

# ==========================================
# 1. SCHEMA CƠ BẢN (Dùng chung)
# ==========================================
class ProgramBase(BaseModel):
    """Các trường dữ liệu cơ bản nhất mà Program nào cũng phải có"""
    name: str
    slug: str # Đường dẫn thân thiện (VD: 'ls', 'file-system')
    # man_page_url: Optional[str] = None
    description: Optional[str] = None
    is_featured: bool = False


# ==========================================
# 2. SCHEMA DÙNG KHI THÊM / SỬA (Request)
# ==========================================
class ProgramCreate(ProgramBase):
    """
    Schema dùng khi Admin gửi request POST để tạo mới.
    Mở rộng: Có thể nhận thêm danh sách ID danh mục để tự động nối bảng trung gian.
    """
    category_ids: Optional[List[int]] = []


class ProgramUpdate(BaseModel):
    """
    Schema dùng khi Admin gửi request PUT để cập nhật.
    Tất cả các trường đều là Optional để Admin thích sửa trường nào thì gửi trường đó.
    """
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    is_featured: Optional[bool] = None
    category_ids: Optional[List[int]] = None # Dùng để cập nhật lại danh mục nếu cần


# ==========================================
# 3. SCHEMA DÙNG KHI TRẢ VỀ (Response)
# ==========================================
class Program(ProgramBase):
    """
    Schema mặc định dùng để trả về dữ liệu (GET list).
    Bao gồm ID và thời gian tạo từ Database.
    """
    id: int
    created_at: datetime
    updated_at: datetime

    categories: List[CategoryInfoForProgram] = []

    class Config:
        from_attributes = True # Bắt buộc có để Pydantic dịch được object SQLAlchemy

# ==========================================
# SCHEMA RÚT GỌN CHO DANH SÁCH (Tối ưu băng thông)
# ==========================================
class ProgramShort(BaseModel):
    """Schema siêu nhẹ chỉ trả về các trường cần thiết để vẽ danh sách"""
    name: str
    slug: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class ProgramDetail(Program):
    """
    Schema "Tối thượng": Dùng cho API chi tiết (GET /{id}/details).
    Trả về Program kèm theo toàn bộ "họ hàng" của nó.
    """
    categories: List[Category] = []
    option_groups: List[OptionGroup] = []
    options: List[Option] = []
    examples: List[Example] = []
    
    # man_pages: List[ManPage] = [] # Nếu bạn đã tạo schema ManPage thì bỏ comment dòng này

    class Config:
        from_attributes = True


class ProgramCategoryUpdate(BaseModel):
    """Schema dùng để cập nhật hàng loạt danh mục cho một lệnh"""
    category_ids: List[int] = [] # Ví dụ truyền lên: {"category_ids": [1, 2, 3]}


class BulkProgramCategoryUpdate(BaseModel):
    """Schema dùng để cập nhật danh mục cho NHIỀU lệnh cùng lúc"""
    program_ids: List[int] = []  # Danh sách các lệnh cần sửa (VD: [1, 2, 3])
    category_ids: List[int] = [] # Danh sách danh mục mới sẽ áp dụng (VD: [4, 5])