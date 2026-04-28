from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Import CRUD và Schemas
from app.crud import crud_example, crud_program, crud_option, crud_option_group
from app.schemas.example import Example, ExampleCreate, ExampleUpdate

# Import DB và Dependency bảo mật
from app.db.session import get_db
from app.api.deps import get_current_admin_user
from app.models.user import User

router = APIRouter()

# ==========================================
# 1. API ĐỌC DỮ LIỆU (PUBLIC - Ai cũng xem được)
# ==========================================

@router.get("/program/{program_id}", response_model=List[Example])
def read_examples_by_program(
    program_id: int, 
    db: Session = Depends(get_db)
) -> Any:
    """
    Lấy danh sách tất cả các ví dụ minh họa của một Câu lệnh (Program).
    Các ví dụ phổ biến (is_common = True) sẽ được ưu tiên hiển thị trước.
    """
    return crud_example.get_examples_by_program(db, program_id=program_id)


# ==========================================
# 2. API GHI DỮ LIỆU (PRIVATE - Chỉ Admin)
# ==========================================

@router.post("/program/{program_id}", response_model=Example, status_code=status.HTTP_201_CREATED)
def create_example_for_program(
    *,
    db: Session = Depends(get_db),
    program_id: int,
    example_in: ExampleCreate,
    current_admin: User = Depends(get_current_admin_user) # BẢO VỆ API
) -> Any:
    """Tạo mới một Ví dụ (Example) cho một Câu lệnh (Admin)"""
    
    # 1. Kiểm tra Program có tồn tại không
    program = crud_program.get_program(db, program_id=program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Không tìm thấy câu lệnh (Program) này.")
        
    # 2. Nếu có truyền group_id, kiểm tra xem Nhóm có tồn tại không
    if example_in.group_id:
        group = crud_option_group.get_option_group(db, group_id=example_in.group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Không tìm thấy Nhóm cờ lệnh (Option Group) này.")
            
    # 3. Nếu có truyền option_id, kiểm tra xem Cờ lệnh có tồn tại không
    if example_in.option_id:
        option = crud_option.get_option(db, option_id=example_in.option_id)
        if not option:
            raise HTTPException(status_code=404, detail="Không tìm thấy Cờ lệnh (Option) này.")

    # 4. Tạo Ví dụ
    return crud_example.create_example(db=db, program_id=program_id, example_in=example_in)

@router.put("/{id}", response_model=Example)
def update_example_api(
    *,
    db: Session = Depends(get_db),
    id: int,
    example_in: ExampleUpdate,
    current_admin: User = Depends(get_current_admin_user) # BẢO VỆ API
) -> Any:
    """Cập nhật thông tin một Ví dụ (Admin)"""
    example = crud_example.get_example(db, example_id=id)
    if not example:
        raise HTTPException(status_code=404, detail="Không tìm thấy ví dụ này.")
        
    # Kiểm tra group_id mới nếu Admin muốn đổi nhóm
    if example_in.group_id and example_in.group_id != example.group_id:
        group = crud_option_group.get_option_group(db, group_id=example_in.group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Không tìm thấy Nhóm cờ lệnh mới để chuyển tới.")

    # Kiểm tra option_id mới nếu Admin muốn đổi cờ lệnh liên kết
    if example_in.option_id and example_in.option_id != example.option_id:
        option = crud_option.get_option(db, option_id=example_in.option_id)
        if not option:
            raise HTTPException(status_code=404, detail="Không tìm thấy Cờ lệnh mới để chuyển tới.")

    return crud_example.update_example(db=db, db_example=example, example_in=example_in)

@router.delete("/{id}", response_model=Example)
def delete_example_api(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_admin: User = Depends(get_current_admin_user) # BẢO VỆ API
) -> Any:
    """Xóa một Ví dụ (Admin)"""
    example = crud_example.get_example(db, example_id=id)
    if not example:
        raise HTTPException(status_code=404, detail="Không tìm thấy ví dụ để xóa.")
    
    return crud_example.delete_example(db=db, example_id=id)