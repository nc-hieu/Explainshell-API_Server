from typing import List, Optional
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func
from app.models.history import History
from app.models.program import Program
from app.schemas.history import HistoryCreate

# # ==========================================
# # 1. CÁC HÀM ĐỌC DỮ LIỆU (READ)
# # ==========================================
def get_history(db: Session, history_id: int) -> Optional[History]:
    """Lấy thông tin một bản ghi lịch sử cụ thể (Load kèm danh sách lệnh)"""
    return db.query(History)\
             .options(selectinload(History.programs))\
             .filter(History.id == history_id).first()

def get_histories_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 50) -> List[History]:
    """
    Lấy danh sách lịch sử của MỘT người dùng cụ thể.
    """
    return db.query(History)\
             .options(selectinload(History.programs)) \
             .filter(History.user_id == user_id)\
             .order_by(History.created_at.asc())\
             .offset(skip).limit(limit).all()

def get_unique_recent_histories_by_user(db: Session, user_id: int, limit: int = 10) -> List[History]:
    """
    Lấy danh sách lịch sử (Không trùng lặp).
    """
    subquery = (
        db.query(
            History.command_text,
            func.max(History.created_at).label("latest_time")
        )
        .filter(History.user_id == user_id)
        .group_by(History.command_text)
        .subquery()
    )

    results = (
        db.query(History)
        .options(selectinload(History.programs)) 
        .join(
            subquery,
            (History.command_text == subquery.c.command_text) &
            (History.created_at == subquery.c.latest_time)
        )
        .order_by(History.created_at.desc())
        .limit(limit)
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

# # =============================================
# # 2. CÁC HÀM GHI & XÓA DỮ LIỆU (CREATE, DELETE)
# # =============================================
def create_history(db: Session, history_in: HistoryCreate, user_id: Optional[int] = None) -> History:
    """
    Tạo lịch sử mới và tự động lưu các liên kết vào bảng trung gian history_programs.
    """
    # 1. Tạo object History (chưa lưu vào DB)
    db_history = History(
        command_text=history_in.command_text,
        status=history_in.status,
        user_id=user_id
    )
    
    # 2. Xử lý lưu các Program liên quan vào bảng trung gian
    if history_in.program_ids:
        # Lấy danh sách các object Program từ database
        programs_found = db.query(Program).filter(Program.id.in_(history_in.program_ids)).all()
        # SQLAlchemy sẽ tự động insert vào bảng history_programs khi gán mảng này
        db_history.programs = programs_found

    # 3. Lưu toàn bộ xuống DB
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

