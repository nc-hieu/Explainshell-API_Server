from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.option import Option
from app.schemas.option import OptionCreate, OptionUpdate

# ==========================================
# 1. CÁC HÀM ĐỌC DỮ LIỆU (READ)
# ==========================================

def get_option(db: Session, option_id: int) -> Optional[Option]:
    """Lấy thông tin chi tiết một cờ lệnh theo ID"""
    return db.query(Option).filter(Option.id == option_id).first()

def get_options_by_program(db: Session, program_id: int) -> List[Option]:
    """
    Lấy danh sách tất cả các cờ lệnh của một Câu lệnh (Program).
    Có thể dùng để liệt kê danh sách cờ lệnh cho người dùng xem.
    """
    return db.query(Option).filter(Option.program_id == program_id).all()


# ==========================================
# 2. CÁC HÀM GHI DỮ LIỆU (CREATE, UPDATE, DELETE)
# ==========================================

def create_option(db: Session, program_id: int, option_in: OptionCreate) -> Option:
    """
    Tạo mới một cờ lệnh và tự động gắn nó vào program_id.
    Nếu có group_id, cờ lệnh sẽ tự động được xếp vào nhóm đó.
    """
    db_option = Option(**option_in.dict(), program_id=program_id)
    db.add(db_option)
    db.commit()
    db.refresh(db_option)
    return db_option

def update_option(db: Session, db_option: Option, option_in: OptionUpdate) -> Option:
    """Cập nhật thông tin của một cờ lệnh"""
    update_data = option_in.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_option, field, value)
        
    db.add(db_option)
    db.commit()
    db.refresh(db_option)
    return db_option

def delete_option(db: Session, option_id: int) -> Optional[Option]:
    """
    Xóa một cờ lệnh.
    Lưu ý: Các Example (ví dụ) có liên kết cụ thể đến option_id này 
    sẽ bị set NULL ở trường option_id do chúng ta đã cấu hình ondelete='SET NULL' trong DB.
    """
    db_option = get_option(db, option_id)
    if db_option:
        db.delete(db_option)
        db.commit()
    return db_option