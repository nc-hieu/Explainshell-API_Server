from typing import Optional
from datetime import datetime
from pydantic import BaseModel

# ==========================================
# THÊM SCHEMA RÚT GỌN CỦA PROGRAM
# (Để hiển thị kèm thông tin lệnh mà không bị lỗi Circular Import)
# ==========================================
class ProgramInfoForFavorite(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

# ==========================================
# 1. SCHEMA CƠ BẢN & GHI DỮ LIỆU (Request)
# ==========================================
class FavoriteBase(BaseModel):
    """Trường dữ liệu bắt buộc khi người dùng bấm nút Yêu thích"""
    program_id: int

class FavoriteCreate(FavoriteBase):
    """
    Schema dùng khi tạo mới. 
    (user_id sẽ tự động lấy từ Token đăng nhập nên không cần truyền)
    """
    pass

# LƯU Ý: Không có FavoriteUpdate vì Yêu thích thì chỉ có Thêm hoặc Gỡ (Xóa)


# ==========================================
# 2. SCHEMA ĐỌC DỮ LIỆU (Response)
# ==========================================
class Favorite(FavoriteBase):
    """Schema chuẩn trả về cho Frontend"""
    id: int
    user_id: int
    created_at: datetime
    
    # BỔ SUNG: Trả về kèm thông tin của Câu lệnh được yêu thích
    # (Đòi hỏi trong Model Favorite của bạn phải có relationship tên là 'program')
    program: Optional[ProgramInfoForFavorite] = None

    class Config:
        from_attributes = True