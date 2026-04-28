from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Import các hàm xử lý logic từ CRUD
from app.crud.crud_program import (
    get_programs, 
    get_program, 
    get_program_by_name, 
    get_program_by_slug,
    get_program_details, 
    get_program_by_slug,
    get_programs_by_category_slug,
    search_programs, 
    create_program, 
    update_program, 
    delete_program
)

# Import các định dạng dữ liệu từ Schemas
from app.schemas.program import (
    Program as ProgramSchema, 
    ProgramShort,
    ProgramCreate, 
    ProgramUpdate, 
    ProgramDetail
)

# Import DB session và Dependency xác thực
from app.db.session import get_db
from app.api.deps import get_current_admin_user
from app.models.user import User

router = APIRouter()

# ==========================================
# 1. API ĐỌC DỮ LIỆU (PUBLIC - Ai cũng xem được)
# ==========================================

@router.get("/", response_model=List[ProgramSchema])
def read_programs(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """Lấy danh sách các lệnh cơ bản (Hỗ trợ phân trang)"""
    return get_programs(db, skip=skip, limit=limit)

@router.get("/search", response_model=List[ProgramSchema])
def search_programs_api(
    query: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Tìm kiếm lệnh siêu tốc bằng Full-text Search.
    Ví dụ: /api/v1/programs/search?query=list
    """
    return search_programs(db, query=query)

@router.get("/{id}/details", response_model=ProgramDetail)
def read_program_details_api(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Lấy toàn bộ cây dữ liệu chi tiết của 1 lệnh.
    Bao gồm Categories, Option Groups, Options, Examples.
    (API quan trọng nhất cho trang hiển thị chi tiết lệnh trên ReactJS)
    """
    program = get_program_details(db, program_id=id)
    if not program:
        raise HTTPException(status_code=404, detail="Không tìm thấy chương trình này.")
    return program

@router.get("/slug/{slug}/details", response_model=ProgramDetail)
def read_program_details_by_slug_api(
    slug: str,
    db: Session = Depends(get_db)
) -> Any:
    """Lấy thông tin một câu lệnh theo Slug (URL SEO)"""
    program = get_program_by_slug(db, slug=slug)
    if not program:
        raise HTTPException(status_code=404, detail="Không tìm thấy câu lệnh này.")
    return program

@router.get("/{id}", response_model=ProgramSchema)
def read_program_api(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    """Lấy thông tin cơ bản của 1 lệnh (Chỉ ID, Name, Description...)"""
    program = get_program(db, program_id=id)
    if not program:
        raise HTTPException(status_code=404, detail="Không tìm thấy chương trình.")
    return program

@router.get("/category/{category_slug}", response_model=List[ProgramShort])
def read_programs_by_category(
    category_slug: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    [TIỆN ÍCH FRONTEND] Lấy danh sách Câu lệnh thuộc một Danh mục (Bao gồm cả danh mục con).
    Trả về dữ liệu siêu nhẹ (chỉ Name, Slug, Description) để tối ưu tốc độ load trang.
    """
    programs = get_programs_by_category_slug(db=db, category_slug=category_slug)
    
    # Kể cả khi programs là rỗng (không có lệnh nào), ta vẫn trả về [] thay vì báo lỗi 404
    # Để Frontend hiển thị giao diện "Chưa có lệnh nào trong danh mục này".
    return programs


# ==========================================
# 2. API GHI DỮ LIỆU (PRIVATE - Yêu cầu Token của Admin)
# ==========================================

@router.post("/", response_model=ProgramSchema, status_code=status.HTTP_201_CREATED)
def create_program_api(
    *,
    db: Session = Depends(get_db),
    program_in: ProgramCreate,
    current_admin: User = Depends(get_current_admin_user) # BẢO VỆ API
) -> Any:
    """Tạo mới một lệnh. Có thể truyền kèm mảng category_ids để gán danh mục."""
    # Kiểm tra xem tên lệnh đã tồn tại chưa
    program = get_program_by_name(db, name=program_in.name)
    if program:
        raise HTTPException(status_code=400, detail="Tên lệnh này đã tồn tại trong hệ thống.")
    
    # Kiểm tra xem slug đã tồn tại chưa
    program_by_slug = get_program_by_slug(db, slug=program_in.slug)
    if program_by_slug:
        raise HTTPException(status_code=400, detail="Slug này đã tồn tại trong hệ thống.")

    return create_program(db=db, program_in=program_in)

@router.put("/{id}", response_model=ProgramSchema)
def update_program_api(
    *,
    db: Session = Depends(get_db),
    id: int,
    program_in: ProgramUpdate,
    current_admin: User = Depends(get_current_admin_user) # BẢO VỆ API
) -> Any:
    """Cập nhật thông tin của một lệnh. Có thể cập nhật lại danh mục."""
    program = get_program(db, program_id=id)
    if not program:
        raise HTTPException(status_code=404, detail="Không tìm thấy lệnh để cập nhật.")
    
    # Nếu Admin muốn đổi tên, phải đảm bảo tên mới không bị trùng với lệnh khác
    if program_in.name and program_in.name != program.name:
        existing_program = get_program_by_name(db, name=program_in.name)
        if existing_program:
            raise HTTPException(status_code=400, detail="Tên lệnh mới đã bị trùng lặp.")

    return update_program(db=db, program_id=id, program_in=program_in)

@router.delete("/{id}", response_model=ProgramSchema)
def delete_program_api(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_admin: User = Depends(get_current_admin_user) # BẢO VỆ API
) -> Any:
    """
    Xóa một lệnh. 
    LƯU Ý: Do thiết lập CASCADE trong Database, việc xóa Program 
    sẽ tự động xóa sạch các Option, Example, Group liên quan!
    """
    program = get_program(db, program_id=id)
    if not program:
        raise HTTPException(status_code=404, detail="Không tìm thấy lệnh để xóa.")
    return delete_program(db=db, program_id=id)