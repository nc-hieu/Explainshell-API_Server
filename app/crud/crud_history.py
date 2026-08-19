from typing import List, Optional
from datetime import datetime
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


def _apply_date_filter(query, from_date: Optional[datetime], to_date: Optional[datetime]):
    """Helper áp dụng bộ lọc thời gian lên một query History."""
    if from_date:
        query = query.filter(History.created_at >= from_date)
    if to_date:
        query = query.filter(History.created_at <= to_date)
    return query


def get_histories_by_status(
    db: Session,
    status: str,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 50,
    sort_by: str = "created_at",
    sort_order: str = "desc"
) -> List[History]:
    """
    Lấy danh sách histories theo status, có hỗ trợ lọc thời gian, sắp xếp và phân trang.
    Mặc định load kèm danh sách programs liên quan.
    """
    # Chỉ cho phép sắp xếp theo các cột hợp lệ để tránh SQL injection
    allowed_sort_columns = {"created_at", "command_text", "status"}
    if sort_by not in allowed_sort_columns:
        sort_by = "created_at"

    sort_column = getattr(History, sort_by)
    if sort_order.lower() == "asc":
        order_clause = sort_column.asc()
    else:
        order_clause = sort_column.desc()

    query = db.query(History)\
              .options(selectinload(History.programs))\
              .filter(History.status == status)

    query = _apply_date_filter(query, from_date, to_date)

    return query.order_by(order_clause).offset(skip).limit(limit).all()


def get_history_status_summary(
    db: Session,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None
) -> dict:
    """
    Thống kê số lượng histories theo từng status.
    Trả về dict đầy đủ 3 status + TOTAL.
    """
    query = db.query(History.status, func.count(History.id).label("count"))
    query = _apply_date_filter(query, from_date, to_date)

    rows = query.group_by(History.status).all()

    summary = {"FOUND": 0, "PARTIAL": 0, "NOT_FOUND": 0}
    total = 0
    for status_value, count in rows:
        summary[status_value] = count
        total += count

    summary["TOTAL"] = total
    return summary

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

