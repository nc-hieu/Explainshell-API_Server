from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.history import History
from app.schemas.history import HistoryCreate

# ==========================================
# 1. CÁC HÀM ĐỌC DỮ LIỆU (READ)
# ==========================================

def get_history(db: Session, history_id: int) -> Optional[History]:
    """Lấy thông tin một bản ghi lịch sử cụ thể"""
    return db.query(History).filter(History.id == history_id).first()

def get_histories_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 50) -> List[History]:
    """
    Lấy danh sách lịch sử của MỘT người dùng cụ thể.
    Luôn sắp xếp theo thời gian mới nhất (created_at DESC).
    """
    return db.query(History)\
             .filter(History.user_id == user_id)\
             .order_by(History.created_at.desc())\
             .offset(skip).limit(limit).all()

def get_unique_recent_histories_by_user(db: Session, user_id: int, limit: int = 10) -> List[History]:
    """
    Lấy danh sách lịch sử của người dùng (Không trùng lặp command_text, lấy thời gian mới nhất).
    Dùng Subquery để tối ưu hiệu năng Database.
    """
    # Bước 1: Tạo một bảng ảo (subquery) gom nhóm theo command_text
    # và tìm ra thời gian tra cứu gần nhất (MAX created_at) của từng lệnh đó.
    subquery = (
        db.query(
            History.command_text,
            func.max(History.created_at).label("latest_time")
        )
        .filter(History.user_id == user_id)
        .group_by(History.command_text)
        .subquery()
    )

    # Bước 2: Join bảng History gốc với cái bảng ảo vừa tạo
    # Chỉ lấy những bản ghi nào có thời gian khớp chính xác với latest_time
    results = (
        db.query(History)
        .join(
            subquery,
            (History.command_text == subquery.c.command_text) &
            (History.created_at == subquery.c.latest_time)
        )
        .order_by(History.created_at.desc()) # Sắp xếp mới nhất lên đầu
        .limit(limit) # Chỉ lấy đúng 10 dòng
        .all()
    )
    
    return results

def get_all_histories(db: Session, skip: int = 0, limit: int = 100) -> List[History]:
    """
    Lấy toàn bộ lịch sử của hệ thống (CHỈ DÀNH CHO ADMIN kiểm tra hệ thống).
    """
    return db.query(History)\
             .order_by(History.created_at.desc())\
             .offset(skip).limit(limit).all()


# ==========================================
# 2. CÁC HÀM GHI & XÓA DỮ LIỆU (CREATE, DELETE)
# ==========================================

def create_history(db: Session, user_id: int, history_in: HistoryCreate) -> History:
    """Lưu lại một lượt tra cứu của người dùng vào Database"""
    db_history = History(**history_in.dict(), user_id=user_id)
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history

def delete_history(db: Session, history_id: int) -> Optional[History]:
    """Xóa một dòng lịch sử cụ thể"""
    db_history = get_history(db, history_id)
    if db_history:
        db.delete(db_history)
        db.commit()
    return db_history

def clear_user_history(db: Session, user_id: int) -> int:
    """
    Tính năng xịn: Xóa toàn bộ lịch sử của một người dùng.
    Trả về số lượng bản ghi đã bị xóa.
    """
    deleted_count = db.query(History).filter(History.user_id == user_id).delete()
    db.commit()
    return deleted_count