from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.option_group import OptionGroup
from app.schemas.option_group import OptionGroupCreate, OptionGroupUpdate

# ==========================================
# 1. CÁC HÀM ĐỌC DỮ LIỆU (READ)
# ==========================================

def get_option_group(db: Session, group_id: int) -> Optional[OptionGroup]:
    """Lấy thông tin một nhóm cụ thể theo ID"""
    return db.query(OptionGroup).filter(OptionGroup.id == group_id).first()

def get_option_groups_by_program(db: Session, program_id: int) -> List[OptionGroup]:
    """
    Lấy danh sách tất cả các nhóm của một Câu lệnh (Program).
    Sắp xếp tự động theo trường sort_order (từ nhỏ đến lớn).
    """
    return db.query(OptionGroup)\
             .filter(OptionGroup.program_id == program_id)\
             .order_by(OptionGroup.sort_order.asc())\
             .all()


# ==========================================
# 2. CÁC HÀM GHI DỮ LIỆU (CREATE, UPDATE, DELETE)
# ==========================================

def create_option_group(db: Session, program_id: int, group_in: OptionGroupCreate) -> OptionGroup:
    """Tạo mới một nhóm cờ lệnh và gắn nó vào một Program cụ thể"""
    # Nối program_id vào data trước khi lưu
    db_group = OptionGroup(**group_in.dict(), program_id=program_id)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

def update_option_group(db: Session, db_group: OptionGroup, group_in: OptionGroupUpdate) -> OptionGroup:
    """Cập nhật thông tin của một nhóm cờ lệnh"""
    update_data = group_in.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_group, field, value)
        
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

def delete_option_group(db: Session, group_id: int) -> Optional[OptionGroup]:
    """
    Xóa một nhóm cờ lệnh.
    LƯU Ý CỦA DATABASE: Những Option (cờ lệnh) và Example (ví dụ) thuộc nhóm này
    sẽ TỰ ĐỘNG BỊ XÓA THEO do bạn đã set cascade="all, delete-orphan" ở bảng Program.
    """
    db_group = get_option_group(db, group_id)
    if db_group:
        db.delete(db_group)
        db.commit()
    return db_group