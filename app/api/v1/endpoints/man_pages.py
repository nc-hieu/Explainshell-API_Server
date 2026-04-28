from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Import CRUD và Schemas
from app.crud import crud_man_page, crud_program
from app.schemas.man_page import ManPage, ManPageCreate, ManPageUpdate

# Import DB và Dependency bảo mật
from app.db.session import get_db
from app.api.deps import get_current_admin_user
from app.models.user import User

router = APIRouter()

# ==========================================
# 1. API ĐỌC DỮ LIỆU (PUBLIC - Ai cũng xem được)
# ==========================================

@router.get("/program/{program_id}", response_model=List[ManPage])
def read_man_pages_by_program(
    program_id: int, 
    db: Session = Depends(get_db)
) -> Any:
    """
    Lấy danh sách tất cả các trang tài liệu (Man Pages) của một Câu lệnh (Program).
    Một lệnh có thể có nhiều trang tài liệu chia theo các section khác nhau (Ví dụ: section 1, section 8).
    """
    return crud_man_page.get_man_pages_by_program(db, program_id=program_id)

@router.get("/{id}", response_model=ManPage)
def read_man_page(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    """Lấy chi tiết nội dung toàn văn của một trang tài liệu cụ thể bằng ID"""
    man_page = crud_man_page.get_man_page(db, man_page_id=id)
    if not man_page:
        raise HTTPException(status_code=404, detail="Không tìm thấy trang tài liệu.")
    return man_page


# ==========================================
# 2. API GHI DỮ LIỆU (PRIVATE - Chỉ Admin)
# ==========================================

@router.post("/program/{program_id}", response_model=ManPage, status_code=status.HTTP_201_CREATED)
def create_man_page_for_program(
    *,
    db: Session = Depends(get_db),
    program_id: int,
    man_page_in: ManPageCreate,
    current_admin: User = Depends(get_current_admin_user) # BẢO VỆ API
) -> Any:
    """Tạo mới một trang tài liệu cho một Câu lệnh (Admin)"""
    
    # Kiểm tra xem Program có thực sự tồn tại trong DB không
    program = crud_program.get_program(db, program_id=program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Không tìm thấy câu lệnh (Program) này.")
        
    return crud_man_page.create_man_page(db=db, program_id=program_id, man_page_in=man_page_in)

@router.put("/{id}", response_model=ManPage)
def update_man_page_api(
    *,
    db: Session = Depends(get_db),
    id: int,
    man_page_in: ManPageUpdate,
    current_admin: User = Depends(get_current_admin_user) # BẢO VỆ API
) -> Any:
    """Cập nhật nội dung trang tài liệu (Admin)"""
    man_page = crud_man_page.get_man_page(db, man_page_id=id)
    if not man_page:
        raise HTTPException(status_code=404, detail="Không tìm thấy trang tài liệu để cập nhật.")
        
    return crud_man_page.update_man_page(db=db, db_man_page=man_page, man_page_in=man_page_in)

@router.delete("/{id}", response_model=ManPage)
def delete_man_page_api(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_admin: User = Depends(get_current_admin_user) # BẢO VỆ API
) -> Any:
    """Xóa trang tài liệu (Admin)"""
    man_page = crud_man_page.get_man_page(db, man_page_id=id)
    if not man_page:
        raise HTTPException(status_code=404, detail="Không tìm thấy trang tài liệu để xóa.")
    
    return crud_man_page.delete_man_page(db=db, man_page_id=id)