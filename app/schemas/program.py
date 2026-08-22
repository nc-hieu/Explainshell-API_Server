from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, field_validator

# LƯU Ý: Để dùng được ProgramDetail ở cuối file, 
# bạn cần đảm bảo đã có các file schema cơ bản cho các bảng liên quan.
# Nếu chưa có, bạn tạm thời comment các dòng import và các trường List[...] ở class ProgramDetail lại nhé.
from app.schemas.category import Category
from app.schemas.option_group import OptionGroup
from app.schemas.option import Option
from app.schemas.note import Note
from app.schemas.example import Example
from app.schemas.man_page import ManPage

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
    is_bsd_style: bool = False # Đánh dấu lệnh dùng BSD-style options (VD: ps aux, tar zcf)

    @field_validator('name', 'slug')
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip() if v else v


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
    is_bsd_style: Optional[bool] = None
    category_ids: Optional[List[int]] = None # Dùng để cập nhật lại danh mục nếu cần

    @field_validator('name', 'slug')
    @classmethod
    def strip_whitespace(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if v else v


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
# SCHEMA RÚT GỌN CHO DANH SÁCH
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
    Schema dùng cho API chi tiết (GET /{id}/details).
    Trả về Program kèm theo toàn bộ "họ hàng" của nó.
    """
    categories: List[Category] = []
    option_groups: List[OptionGroup] = []
    options: List[Option] = []
    notes: List[Note] = []
    examples: List[Example] = []
    man_pages: List[ManPage] = []

    class Config:
        from_attributes = True


class ProgramCategoryUpdate(BaseModel):
    """Schema dùng để cập nhật hàng loạt danh mục cho một lệnh"""
    category_ids: List[int] = [] # Ví dụ truyền lên: {"category_ids": [1, 2, 3]}


class BulkProgramCategoryUpdate(BaseModel):
    """Schema dùng để cập nhật danh mục cho NHIỀU lệnh cùng lúc"""
    program_ids: List[int] = []  # Danh sách các lệnh cần sửa (VD: [1, 2, 3])
    category_ids: List[int] = [] # Danh sách danh mục mới sẽ áp dụng (VD: [4, 5])
from app.schemas.option import Option


# ==========================================
# SCHEMA DÙNG KHI TRẢ VỀ (ExplainShell)
# ==========================================
# class ExplainResponse(BaseModel):
#     """Schema trả về cho tính năng Giải thích lệnh (Explain)"""
#     program: ProgramShort         # Dùng ProgramShort cho nhẹ
#     matched_options: List[Option] # Danh sách các cờ lệnh tìm thấy
#     unmatched_args: List[str]     # Các tham số dư thừa (VD: tên file, đường dẫn) để FE có thể highlight màu xám

#     class Config:
#         from_attributes = True

class ParsedProgram(BaseModel):
    id: Optional[int] = None
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    is_found: bool # Cờ quan trọng cho Frontend

class ParsedOption(BaseModel):
    id: Optional[int] = None
    original_text: str # Text người dùng nhập (VD: "-a")
    short_name: Optional[str] = None
    long_name: Optional[str] = None
    description: Optional[str] = None
    is_found: bool # Báo cho Frontend biết có cờ này trong DB không
    value: Optional[str] = None # Giá trị dính liền hoặc từ arg tiếp theo (VD: -p2222 → "2222")

class ExplainResponse(BaseModel):
    type: str = "command" # command | operator | redirect_target
    program: ParsedProgram
    matched_options: List[ParsedOption]
    unmatched_args: List[str] # Dành cho các tham số như "some-dir", "some-server", chuỗi trong ngoặc kép
