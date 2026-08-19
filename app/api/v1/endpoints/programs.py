from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Import các hàm xử lý logic từ CRUD
from app.crud.crud_program import (
    get_programs,
    get_program,
    get_program_by_name,
    get_program_by_slug,
    get_program_details,
    get_program_details_by_slug,
    get_programs_by_category_slug,
    get_programs_by_topic_slug,
    search_programs,
    explain_command,
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

from app.schemas.history import HistoryCreate

# Import ExplainResponse từ schemas
from app.schemas.program import ExplainResponse

# Import DB session và Dependency xác thực
from app.db.session import get_db
from app.api.deps import get_current_admin_user
from app.api.deps import get_current_user_optional
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

# @router.get("/search", response_model=List[ProgramSchema])
# def search_programs_api(
#     query: str,
#     db: Session = Depends(get_db)
# ) -> Any:
#     """
#     Tìm kiếm lệnh siêu tốc bằng Full-text Search.
#     Ví dụ: /api/v1/programs/search?query=list
#     """
#     return search_programs(db, query=query)

@router.get("/search", response_model=List[ProgramSchema])
def search_programs_api(
    query: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> Any:
    """
    Tìm kiếm lệnh siêu tốc bằng Full-text Search.
    """
    # 1. Gọi hàm search tìm kết quả
    results = search_programs(db, query=query)

    # [TẠM THỜI TẮT] Lưu lịch sử tìm kiếm đã được chuyển sang Frontend.
    # Nếu cần bật lại logic cũ, uncomment đoạn code dưới đây:
    # if current_user:
    #     if results and len(results) > 0:
    #         history_data = HistoryCreate(
    #             command_text=query,
    #             status="FOUND",
    #             program_ids=[results[0].id]
    #         )
    #     else:
    #         history_data = HistoryCreate(
    #             command_text=query,
    #             status="NOT_FOUND",
    #             program_ids=[]
    #         )
    #     create_history(db=db, history_in=history_data, user_id=current_user.id)

    # 2. Trả về kết quả tìm kiếm cho Frontend như bình thường (Dù là Khách hay User)
    return results


@router.get("/explain", response_model=List[ExplainResponse])
def explain_command_api(
    query: str, 
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> Any:
    """
    API Phân tích và Giải thích toàn bộ một câu lệnh.
    """
    # 1. Gọi hàm parser (result bây giờ là một List các object)
    result = explain_command(db, full_command=query)

    # [TẠM THỜI TẮT] Lưu lịch sử tìm kiếm đã được chuyển sang Frontend.
    # Nếu cần bật lại logic cũ, uncomment đoạn code dưới đây:
    # if current_user:
    #     if result and len(result) > 0:
    #         found_ids = [
    #             item["program"]["id"]
    #             for item in result
    #             if item["program"]["is_found"] and item["program"]["id"] is not None
    #         ]
    #         total_commands = len(result)
    #         found_count = len(found_ids)
    #         if found_count == total_commands:
    #             overall_status = "FOUND"
    #         elif found_count == 0:
    #             overall_status = "NOT_FOUND"
    #         else:
    #             overall_status = "PARTIAL"
    #         history_data = HistoryCreate(
    #             command_text=query,
    #             status=overall_status,
    #             program_ids=found_ids
    #         )
    #     else:
    #         history_data = HistoryCreate(
    #             command_text=query,
    #             status="NOT_FOUND",
    #             program_ids=[]
    #         )
    #     create_history(db=db, history_in=history_data, user_id=current_user.id)

    # 2. Trả về kết quả trực tiếp cho Frontend
    # Đã bỏ phần raise HTTPException 404 để Frontend tự xử lý giao diện hiển thị
    # các từ khóa không tìm thấy thông qua cờ `is_found = False`.
    return result

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
    program = get_program_details_by_slug(db, slug=slug)
    if not program:
        raise HTTPException(status_code=404, detail="Không tìm thấy câu lệnh này.")
    # Sắp xếp options theo id tại đây để tránh thay đổi trạng thái ORM trong session
    if program.options:
        program.options = sorted(program.options, key=lambda opt: opt.id)
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

@router.get("/topic/{topic_slug}", response_model=List[ProgramShort])
def read_programs_by_topic_slug_api(
    topic_slug: str,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    [TIỆN ÍCH FRONTEND] Lấy danh sách câu lệnh thuộc một Hệ sinh thái (Topic) qua Slug.
    - URL mẫu: GET /api/v1/programs/topic/linux?skip=0&limit=20
    - Dữ liệu trả về siêu nhẹ (chỉ có name, slug, description) phù hợp làm trang danh sách, từ điển tra cứu.
    """
    programs = get_programs_by_topic_slug(
        db=db, topic_slug=topic_slug, skip=skip, limit=limit
    )
    
    # Trả về mảng rỗng [] nếu chưa có dữ liệu chứ không báo lỗi 404, 
    # giúp Frontend dễ dàng hiển thị giao diện "Chưa có câu lệnh nào".
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