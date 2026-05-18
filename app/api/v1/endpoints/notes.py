from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Import CRUD và Schemas
from app.crud import crud_note, crud_program
from app.schemas.note import Note, NoteCreate, NoteUpdate

# Import DB và Dependency bảo mật
from app.db.session import get_db
from app.api.deps import get_current_admin_user
from app.models.user import User

router = APIRouter()

# ==========================================
# 1. API ĐỌC DỮ LIỆU (PUBLIC)
# ==========================================

@router.get("/program/{program_id}", response_model=List[Note])
def read_notes_by_program(
    program_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """Lấy danh sách tất cả các Ghi chú (Notes) của một Câu lệnh cụ thể"""
    return crud_note.get_notes_by_program(db=db, program_id=program_id)

@router.get("/{id}", response_model=Note)
def read_note(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    """Lấy chi tiết 1 Ghi chú bằng ID"""
    note = crud_note.get_note(db=db, note_id=id)
    if not note:
        raise HTTPException(status_code=404, detail="Không tìm thấy Ghi chú này.")
    return note

# ==========================================
# 2. API GHI DỮ LIỆU (PRIVATE - CHỈ ADMIN)
# ==========================================

@router.post("/", response_model=Note, status_code=status.HTTP_201_CREATED)
def create_note_api(
    *,
    db: Session = Depends(get_db),
    note_in: NoteCreate,
    current_admin: User = Depends(get_current_admin_user)
) -> Any:
    """Tạo mới một Ghi chú cho Câu lệnh (Chỉ Admin)"""
    # Xác minh xem program_id gửi lên có tồn tại không
    program = crud_program.get_program(db=db, program_id=note_in.program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Không tìm thấy Câu lệnh (Program) để gắn ghi chú.")
        
    return crud_note.create_note(db=db, note_in=note_in)

@router.put("/{id}", response_model=Note)
def update_note_api(
    *,
    db: Session = Depends(get_db),
    id: int,
    note_in: NoteUpdate,
    current_admin: User = Depends(get_current_admin_user)
) -> Any:
    """Cập nhật Ghi chú (Chỉ Admin)"""
    note = crud_note.get_note(db=db, note_id=id)
    if not note:
        raise HTTPException(status_code=404, detail="Không tìm thấy Ghi chú này.")
        
    # Nếu đổi program_id, kiểm tra xem program mới có tồn tại không
    if note_in.program_id:
        program = crud_program.get_program(db=db, program_id=note_in.program_id)
        if not program:
            raise HTTPException(status_code=404, detail="Không tìm thấy Câu lệnh (Program) mới.")
            
    return crud_note.update_note(db=db, db_note=note, note_in=note_in)

@router.delete("/{id}", response_model=Note)
def delete_note_api(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_admin: User = Depends(get_current_admin_user)
) -> Any:
    """Xóa Ghi chú (Chỉ Admin)"""
    note = crud_note.get_note(db=db, note_id=id)
    if not note:
        raise HTTPException(status_code=404, detail="Không tìm thấy Ghi chú này.")
        
    return crud_note.delete_note(db=db, note_id=id)