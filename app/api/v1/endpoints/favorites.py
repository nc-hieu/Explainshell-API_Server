from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Import CRUD và Schemas
from app.crud import crud_favorite, crud_program
from app.schemas.favorite import Favorite, FavoriteCreate

# Import DB và Dependency bảo mật
from app.db.session import get_db
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()

# ==========================================
# 1. API ĐỌC DỮ LIỆU CÁ NHÂN
# ==========================================

@router.get("/me", response_model=List[Favorite])
def read_my_favorites(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Lấy danh sách các lệnh đã Yêu thích của bản thân"""
    return crud_favorite.get_favorites_by_user(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )


# ==========================================
# 2. API GHI & XÓA DỮ LIỆU
# ==========================================

@router.post("/", response_model=Favorite, status_code=status.HTTP_201_CREATED)
def create_favorite_api(
    *,
    db: Session = Depends(get_db),
    favorite_in: FavoriteCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Thả tim (Yêu thích) một Câu lệnh.
    (Hệ thống tự động kiểm tra xem lệnh có tồn tại không và đã thả tim chưa để tránh trùng lặp)
    """
    # 1. Kiểm tra Lệnh (Program) có thực sự tồn tại không
    program = crud_program.get_program(db=db, program_id=favorite_in.program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Không tìm thấy Câu lệnh (Program) này.")
        
    # 2. Kiểm tra xem User đã thả tim Lệnh này chưa
    existing_favorite = crud_favorite.get_favorite_by_user_and_program(
        db=db, user_id=current_user.id, program_id=favorite_in.program_id
    )
    if existing_favorite:
        raise HTTPException(status_code=400, detail="Bạn đã yêu thích câu lệnh này rồi.")
        
    # 3. Lưu vào Database
    return crud_favorite.create_favorite(db=db, user_id=current_user.id, favorite_in=favorite_in)

@router.delete("/program/{program_id}")
def delete_favorite_by_program_id_api(
    *,
    db: Session = Depends(get_db),
    program_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    [TIỆN ÍCH FRONTEND] Bỏ thả tim (Thu hồi) dựa vào ID của Câu lệnh.
    Khi đang ở trang chi tiết lệnh, User bấm bỏ tim, Frontend chỉ việc gọi API này.
    """
    favorite = crud_favorite.get_favorite_by_user_and_program(
        db=db, user_id=current_user.id, program_id=program_id
    )
    if not favorite:
        raise HTTPException(status_code=404, detail="Bạn chưa yêu thích câu lệnh này nên không thể bỏ.")
        
    crud_favorite.delete_favorite(db=db, favorite_id=favorite.id)
    return {"message": "Đã bỏ yêu thích câu lệnh thành công."}

@router.delete("/{id}", response_model=Favorite)
def delete_favorite_api(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Bỏ thả tim dựa vào ID của bản ghi Favorite (Dành cho trang Quản lý Yêu thích).
    Bảo mật: Phải là chủ sở hữu của bản ghi này mới được xóa.
    """
    favorite = crud_favorite.get_favorite(db=db, favorite_id=id)
    if not favorite:
        raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi yêu thích.")
    
    if favorite.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bạn không có quyền gỡ yêu thích của người khác.")
        
    return crud_favorite.delete_favorite(db=db, favorite_id=id)

# ==========================================
# 3. API TIỆN ÍCH CHO FRONTEND (CHECK & TOGGLE)
# ==========================================

@router.get("/program/{program_id}/check")
def check_favorite_status_api(
    *,
    db: Session = Depends(get_db),
    program_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    [TIỆN ÍCH] Kiểm tra xem người dùng đã thả tim Lệnh này chưa.
    Trả về dạng: {"is_favorite": True} hoặc {"is_favorite": False}
    Dùng để Frontend quyết định hiển thị Tim Đỏ hay Tim Trắng khi vừa load trang.
    """
    favorite = crud_favorite.get_favorite_by_user_and_program(
        db=db, user_id=current_user.id, program_id=program_id
    )
    
    return {"is_favorite": favorite is not None}


@router.post("/program/{program_id}/toggle")
def toggle_favorite_api(
    *,
    db: Session = Depends(get_db),
    program_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    [TIỆN ÍCH] Bật/Tắt trạng thái Yêu thích (Toggle).
    Frontend chỉ việc gọi API này mỗi khi User bấm vào nút Trái Tim:
    - Nếu CHƯA thả tim -> Tự động THÊM vào Yêu thích.
    - Nếu ĐÃ thả tim -> Tự động GỠ BỎ Yêu thích.
    """
    # 1. Kiểm tra xem Lệnh (Program) có tồn tại trong hệ thống không
    program = crud_program.get_program(db=db, program_id=program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Không tìm thấy Câu lệnh (Program) này.")
        
    # 2. Kiểm tra xem User đã thả tim chưa
    existing_favorite = crud_favorite.get_favorite_by_user_and_program(
        db=db, user_id=current_user.id, program_id=program_id
    )
    
    if existing_favorite:
        # Nếu đã có -> Xóa đi (Thu hồi tim)
        crud_favorite.delete_favorite(db=db, favorite_id=existing_favorite.id)
        return {
            "message": "Đã bỏ yêu thích câu lệnh.",
            "is_favorite": False # Trả về trạng thái mới để Frontend cập nhật UI ngay lập tức
        }
    else:
        # Nếu chưa có -> Tạo mới (Thả tim)
        favorite_in = FavoriteCreate(program_id=program_id)
        crud_favorite.create_favorite(db=db, user_id=current_user.id, favorite_in=favorite_in)
        return {
            "message": "Đã thêm vào danh sách yêu thích.",
            "is_favorite": True # Trả về trạng thái mới
        }