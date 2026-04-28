from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# Import CRUD và Schemas
from app.crud import crud_option, crud_program, crud_option_group
from app.schemas.option import Option, OptionCreate, OptionUpdate
from app.models.option import Option as OptionModel

# Import DB và Dependency bảo mật
from app.db.session import get_db
from app.api.deps import get_current_admin_user
from app.models.user import User

router = APIRouter()

# ==========================================
# 1. API ĐỌC DỮ LIỆU (PUBLIC - Ai cũng xem được)
# ==========================================

@router.get("/program/{program_id}", response_model=List[Option])
def read_options_by_program(
    program_id: int, 
    db: Session = Depends(get_db)
) -> Any:
    """Lấy danh sách tất cả các cờ lệnh của một Câu lệnh (Program) cụ thể"""
    return crud_option.get_options_by_program(db, program_id=program_id)


# ==========================================
# 2. API GHI DỮ LIỆU (PRIVATE - Chỉ Admin)
# ==========================================

@router.post("/program/{program_id}", response_model=Option, status_code=status.HTTP_201_CREATED)
def create_option_for_program(
    *,
    db: Session = Depends(get_db),
    program_id: int,
    option_in: OptionCreate,
    current_admin: User = Depends(get_current_admin_user) # BẢO VỆ API
) -> Any:
    """Tạo mới một Cờ lệnh (Option) cho một Câu lệnh (Admin)"""
    
    # 1. Kiểm tra Program có tồn tại không
    program = crud_program.get_program(db, program_id=program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Không tìm thấy câu lệnh (Program) này.")
        
    # 2. Nếu có truyền group_id, kiểm tra xem Nhóm có tồn tại không
    if option_in.group_id:
        group = crud_option_group.get_option_group(db, group_id=option_in.group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Không tìm thấy Nhóm cờ lệnh (Option Group) này.")
            
    # 3. Tạo Option (Có bắt lỗi UniqueConstraint từ Database)
    try:
        return crud_option.create_option(db=db, program_id=program_id, option_in=option_in)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail="Cờ lệnh này (short_name hoặc long_name) đã tồn tại trong Program này. Vui lòng không tạo trùng lặp."
        )

@router.put("/{id}", response_model=Option)
def update_option_api(
    *,
    db: Session = Depends(get_db),
    id: int,
    option_in: OptionUpdate,
    current_admin: User = Depends(get_current_admin_user) # BẢO VỆ API
) -> Any:
    """Cập nhật thông tin một Cờ lệnh (Admin)"""
    option = crud_option.get_option(db, option_id=id)
    if not option:
        raise HTTPException(status_code=404, detail="Không tìm thấy cờ lệnh này.")
        
    # Kiểm tra group_id mới nếu Admin muốn đổi nhóm
    if option_in.group_id and option_in.group_id != option.group_id:
        group = crud_option_group.get_option_group(db, group_id=option_in.group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Không tìm thấy Nhóm cờ lệnh mới để chuyển tới.")

    try:
        return crud_option.update_option(db=db, db_option=option, option_in=option_in)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail="Tên cờ lệnh cập nhật bị trùng lặp với một cờ lệnh khác trong cùng Program."
        )

@router.delete("/{id}", response_model=Option)
def delete_option_api(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_admin: User = Depends(get_current_admin_user) # BẢO VỆ API
) -> Any:
    """
    Xóa một Cờ lệnh (Admin).
    Những ví dụ (Examples) đang dùng cờ lệnh này sẽ tự động bị SET NULL (chỉ mất liên kết, không mất ví dụ).
    """
    option = crud_option.get_option(db, option_id=id)
    if not option:
        raise HTTPException(status_code=404, detail="Không tìm thấy cờ lệnh để xóa.")
    
    return crud_option.delete_option(db=db, option_id=id)