from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate

# ==========================================
# 1. CÁC HÀM ĐỌC DỮ LIỆU (READ)
# ==========================================

def get_note(db: Session, note_id: int) -> Optional[Note]:
    """Lấy chi tiết 1 Note dựa vào ID"""
    return db.query(Note).filter(Note.id == note_id).first()

def get_notes_by_program(db: Session, program_id: int) -> List[Note]:
    """
    Lấy toàn bộ Notes của 1 Câu lệnh (Program).
    Sắp xếp từ mới nhất đến cũ nhất.
    """
    return db.query(Note)\
             .filter(Note.program_id == program_id)\
             .order_by(Note.created_at.asc())\
             .all()

# ==========================================
# 2. CÁC HÀM GHI DỮ LIỆU (CREATE, UPDATE, DELETE)
# ==========================================

def create_note(db: Session, note_in: NoteCreate) -> Note:
    """Tạo mới Note"""
    # Sử dụng model_dump() (Pydantic v2) thay vì dict()
    db_note = Note(**note_in.model_dump())
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def update_note(db: Session, db_note: Note, note_in: NoteUpdate) -> Note:
    """Cập nhật Note hiện tại"""
    update_data = note_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_note, field, value)
        
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def delete_note(db: Session, note_id: int) -> Optional[Note]:
    """Xóa Note"""
    db_note = get_note(db, note_id)
    if db_note:
        db.delete(db_note)
        db.commit()
    return db_note