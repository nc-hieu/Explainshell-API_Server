from typing import List, Optional
from sqlalchemy.orm import Session, selectinload
from app.models.favorite import Favorite
from app.schemas.favorite import FavoriteCreate

# ==========================================
# 1. CÁC HÀM ĐỌC DỮ LIỆU (READ)
# ==========================================

def get_favorite(db: Session, favorite_id: int) -> Optional[Favorite]:
    """Lấy thông tin một bản ghi yêu thích theo ID"""
    return db.query(Favorite).filter(Favorite.id == favorite_id).first()

def get_favorite_by_user_and_program(db: Session, user_id: int, program_id: int) -> Optional[Favorite]:
    """
    Kiểm tra xem User này đã yêu thích Program này chưa.
    Rất quan trọng để chặn lỗi trùng lặp dữ liệu.
    """
    return db.query(Favorite).filter(
        Favorite.user_id == user_id,
        Favorite.program_id == program_id
    ).first()

def get_favorites_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 50) -> List[Favorite]:
    """
    Lấy danh sách các lệnh đã Yêu thích của MỘT người dùng.
    Dùng selectinload để tải sẵn thông tin Lệnh (Program).
    Sắp xếp mới nhất lên đầu.
    """
    return db.query(Favorite)\
             .filter(Favorite.user_id == user_id)\
             .options(selectinload(Favorite.program))\
             .order_by(Favorite.created_at.desc())\
             .offset(skip).limit(limit).all()


# ==========================================
# 2. CÁC HÀM GHI & XÓA DỮ LIỆU (CREATE, DELETE)
# ==========================================

def create_favorite(db: Session, user_id: int, favorite_in: FavoriteCreate) -> Favorite:
    """Thêm một Lệnh vào danh sách Yêu thích của User"""
    db_favorite = Favorite(
        user_id=user_id,
        program_id=favorite_in.program_id
    )
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite

def delete_favorite(db: Session, favorite_id: int) -> Optional[Favorite]:
    """Gỡ bỏ (Xóa) một Lệnh khỏi danh sách Yêu thích"""
    db_favorite = get_favorite(db, favorite_id)
    if db_favorite:
        db.delete(db_favorite)
        db.commit()
    return db_favorite