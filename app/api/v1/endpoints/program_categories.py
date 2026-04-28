from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Import CRUD và Schema
from app.crud import crud_program
from app.schemas.program import Program, ProgramCategoryUpdate, BulkProgramCategoryUpdate # Tái sử dụng schema Program đã có categories

# Import DB và Auth
from app.db.session import get_db
from app.api.deps import get_current_admin_user
from app.models.user import User

router = APIRouter()

@router.post("/{program_id}/category/{category_id}", response_model=Program)
def link_program_to_category(
    *,
    db: Session = Depends(get_db),
    program_id: int,
    category_id: int,
    current_admin: User = Depends(get_current_admin_user) # Chỉ Admin được nối dữ liệu
) -> Any:
    """
    Gắn một Câu lệnh (Program) vào một Danh mục (Category).
    (Nếu đã gắn rồi thì không làm gì cả và trả về Program hiện tại).
    """
    program = crud_program.add_category_to_program(db=db, program_id=program_id, category_id=category_id)
    
    if not program:
        raise HTTPException(status_code=404, detail="Không tìm thấy Câu lệnh hoặc Danh mục này.")
        
    return program


@router.put("/bulk-update", response_model=List[Program])
def bulk_update_categories_for_multiple_programs_api(
    *,
    db: Session = Depends(get_db),
    payload: BulkProgramCategoryUpdate,
    current_admin: User = Depends(get_current_admin_user)
) -> Any:
    """
    [CẬP NHẬT HÀNG LOẠT] (Admin)
    Truyền vào một mảng program_ids và một mảng category_ids.
    Hệ thống sẽ đồng bộ toàn bộ các lệnh đó về chung một nhóm danh mục được chỉ định.
    """
    
    # Bắt lỗi nếu Admin truyền mảng program_ids nhưng có ID "ma" không tồn tại
    if payload.program_ids:
        from app.models.program import Program
        valid_programs_count = db.query(Program).filter(Program.id.in_(payload.program_ids)).count()
        if valid_programs_count != len(set(payload.program_ids)):
            raise HTTPException(status_code=400, detail="Một hoặc nhiều ID Câu lệnh truyền lên không tồn tại.")

    # Bắt lỗi tương tự với category_ids
    if payload.category_ids:
        from app.models.category import Category
        valid_cats_count = db.query(Category).filter(Category.id.in_(payload.category_ids)).count()
        if valid_cats_count != len(set(payload.category_ids)):
            raise HTTPException(status_code=400, detail="Một hoặc nhiều ID Danh mục truyền lên không tồn tại.")

    # Chạy hàm CRUD
    updated_programs = crud_program.bulk_update_program_categories(
        db=db, 
        program_ids=payload.program_ids, 
        category_ids=payload.category_ids
    )
    
    return updated_programs



@router.put("/{program_id}", response_model=Program)
def update_categories_for_program_api(
    *,
    db: Session = Depends(get_db),
    program_id: int,
    payload: ProgramCategoryUpdate,
    current_admin: User = Depends(get_current_admin_user)
) -> Any:
    """
    Cập nhật toàn bộ danh mục của một Câu lệnh (Admin).
    Truyền vào một mảng category_ids. Hệ thống sẽ tự động đồng bộ (Thêm mới, gỡ bỏ cũ).
    Nếu muốn gỡ toàn bộ danh mục, chỉ cần truyền lên mảng rỗng: {"category_ids": []}
    """
    
    # (Tùy chọn) Kiểm tra xem các category_ids truyền lên có tồn tại hết không
    # Tránh trường hợp Admin truyền ID linh tinh
    if payload.category_ids:
        from app.models.category import Category # Import model Category
        valid_cats_count = db.query(Category).filter(Category.id.in_(payload.category_ids)).count()
        if valid_cats_count != len(set(payload.category_ids)):
            raise HTTPException(status_code=400, detail="Một hoặc nhiều ID danh mục truyền lên không tồn tại trong hệ thống.")

    program = crud_program.update_program_categories(
        db=db, program_id=program_id, category_ids=payload.category_ids
    )
    
    if not program:
        raise HTTPException(status_code=404, detail="Không tìm thấy Câu lệnh (Program) này.")
        
    return program




@router.delete("/{program_id}/category/{category_id}", response_model=Program)
def unlink_program_from_category(
    *,
    db: Session = Depends(get_db),
    program_id: int,
    category_id: int,
    current_admin: User = Depends(get_current_admin_user) # Chỉ Admin được gỡ dữ liệu
) -> Any:
    """
    Gỡ một Câu lệnh (Program) ra khỏi một Danh mục (Category).
    """
    program = crud_program.remove_category_from_program(db=db, program_id=program_id, category_id=category_id)
    
    if not program:
        raise HTTPException(status_code=404, detail="Không tìm thấy Câu lệnh hoặc Danh mục này.")
        
    return program
