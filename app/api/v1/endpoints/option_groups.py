from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Import CRUD và Schemas
from app.crud import crud_option_group, crud_program
from app.schemas.option_group import OptionGroup, OptionGroupCreate, OptionGroupUpdate

# Import DB và Dependency bảo mật
from app.db.session import get_db
from app.api.deps import get_current_admin_user
from app.models.user import User

router = APIRouter()

# ==========================================
# 1. API ĐỌC DỮ LIỆU (PUBLIC - Ai cũng xem được)
# ==========================================

@router.get("/program/{program_id}", response_model=List[OptionGroup])
def read_groups_by_program(
    program_id: int, 
    db: Session = Depends(get_db)
) -> Any:
    """
    Lấy danh sách tất cả các Nhóm cờ lệnh (Option Groups) của một Câu lệnh (Program).
    Các nhóm đã được tự động sắp xếp theo thứ tự sort_order.
    """
    return crud_option_group.get_option_groups_by_program(db, program_id=program_id)


# ==========================================
# 2. API GHI DỮ LIỆU (PRIVATE - Chỉ Admin)
# ==========================================

@router.post("/program/{program_id}", response_model=OptionGroup, status_code=status.HTTP_201_CREATED)
def create_group_for_program(
    *,
    db: Session = Depends(get_db),
    program_id: int,
    group_in: OptionGroupCreate,
    current_admin: User = Depends(get_current_admin_user) # BẢO VỆ API
) -> Any:
    """Tạo mới một Nhóm cờ lệnh cho một Câu lệnh cụ thể (Admin)"""
    # 1. Kiểm tra xem Program có tồn tại không
    program = crud_program.get_program(db, program_id=program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Không tìm thấy câu lệnh (Program) này.")
    
    # 2. Tạo nhóm
    return crud_option_group.create_option_group(db=db, program_id=program_id, group_in=group_in)

@router.put("/{id}", response_model=OptionGroup)
def update_group_api(
    *,
    db: Session = Depends(get_db),
    id: int,
    group_in: OptionGroupUpdate,
    current_admin: User = Depends(get_current_admin_user) # BẢO VỆ API
) -> Any:
    """Cập nhật thông tin của Nhóm cờ lệnh (Admin)"""
    group = crud_option_group.get_option_group(db, group_id=id)
    if not group:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhóm cờ lệnh này.")
    
    return crud_option_group.update_option_group(db=db, db_group=group, group_in=group_in)

@router.delete("/{id}", response_model=OptionGroup)
def delete_group_api(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_admin: User = Depends(get_current_admin_user) # BẢO VỆ API
) -> Any:
    """
    Xóa Nhóm cờ lệnh (Admin).
    Các cờ lệnh (Options) bên trong nhóm này sẽ tự động bị xóa theo (CASCADE).
    """
    group = crud_option_group.get_option_group(db, group_id=id)
    if not group:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhóm cờ lệnh để xóa.")
    
    return crud_option_group.delete_option_group(db=db, group_id=id)