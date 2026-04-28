from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.example import Example
from app.schemas.example import ExampleCreate, ExampleUpdate

# ==========================================
# 1. CÁC HÀM ĐỌC DỮ LIỆU (READ)
# ==========================================

def get_example(db: Session, example_id: int) -> Optional[Example]:
    """Lấy chi tiết một ví dụ theo ID"""
    return db.query(Example).filter(Example.id == example_id).first()

def get_examples_by_program(db: Session, program_id: int) -> List[Example]:
    """
    Lấy danh sách tất cả các ví dụ của một Câu lệnh (Program).
    Ưu tiên sắp xếp: Các ví dụ phổ biến (is_common=True) sẽ nổi lên trên.
    """
    return db.query(Example)\
             .filter(Example.program_id == program_id)\
             .order_by(Example.is_common.desc(), Example.id.asc())\
             .all()


# ==========================================
# 2. CÁC HÀM GHI DỮ LIỆU (CREATE, UPDATE, DELETE)
# ==========================================

def create_example(db: Session, program_id: int, example_in: ExampleCreate) -> Example:
    """Tạo một ví dụ mới và gắn vào program_id"""
    db_example = Example(**example_in.dict(), program_id=program_id)
    db.add(db_example)
    db.commit()
    db.refresh(db_example)
    return db_example

def update_example(db: Session, db_example: Example, example_in: ExampleUpdate) -> Example:
    """Cập nhật thông tin của một ví dụ"""
    update_data = example_in.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_example, field, value)
        
    db.add(db_example)
    db.commit()
    db.refresh(db_example)
    return db_example

def delete_example(db: Session, example_id: int) -> Optional[Example]:
    """Xóa một ví dụ khỏi hệ thống"""
    db_example = get_example(db, example_id)
    if db_example:
        db.delete(db_example)
        db.commit()
    return db_example