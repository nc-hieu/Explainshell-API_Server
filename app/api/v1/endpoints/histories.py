from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Import CRUD và Schemas
from app.crud import crud_history
from app.schemas.history import History, HistoryCreate

# Import DB và Dependency bảo mật
from app.db.session import get_db
from app.api.deps import get_current_active_user, get_current_admin_user
from app.models.user import User

router = APIRouter()

# ==========================================
# 1. API CÁ NHÂN (Dành cho User đã đăng nhập)
# ==========================================

@router.post("/", response_model=History, status_code=status.HTTP_201_CREATED)
def create_user_history_api(
    *,
    db: Session = Depends(get_db),
    history_in: HistoryCreate,
    current_user: User = Depends(get_current_active_user) # Yêu cầu đăng nhập
) -> Any:
    """
    Lưu lại một lịch sử tra cứu.
    (Hệ thống tự động lấy ID của người dùng từ Token)
    """
    return crud_history.create_history(db=db, user_id=current_user.id, history_in=history_in)

@router.get("/me", response_model=List[History])
def read_my_histories(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Lấy danh sách lịch sử của chính mình"""
    return crud_history.get_histories_by_user(db=db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/me/recent-unique", response_model=List[History])
def read_my_unique_recent_histories(
    db: Session = Depends(get_db),
    limit: int = 10, # Mặc định lấy 10, Frontend có thể truyền số khác nếu muốn
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """     
    Lấy danh sách lịch sử tra cứu của bản thân (Tối đa 10 lần gần nhất).
    ĐẶC BIỆT: Các câu lệnh (command_text) sẽ KHÔNG BỊ TRÙNG LẶP.
    Tuyệt vời để làm tính năng "Lịch sử tìm kiếm gần đây" dạng Dropdown.
    """
    return crud_history.get_unique_recent_histories_by_user(
        db=db, 
        user_id=current_user.id, 
        limit=limit
    )

@router.delete("/me/clear")
def clear_all_my_history_api(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Xóa toàn bộ lịch sử của bản thân"""
    deleted_count = crud_history.clear_user_history(db=db, user_id=current_user.id)
    return {"message": f"Đã xóa thành công {deleted_count} bản ghi lịch sử."}

@router.delete("/{id}", response_model=History)
def delete_single_history_api(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Xóa 1 bản ghi lịch sử.
    Bảo mật: Phải là chủ sở hữu của lịch sử đó, hoặc là Admin mới được xóa.
    """
    history = crud_history.get_history(db=db, history_id=id)
    if not history:
        raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi lịch sử.")
    
    if history.user_id != current_user.id and current_user.roles != "admin":
        raise HTTPException(status_code=403, detail="Bạn không có quyền xóa lịch sử của người khác.")
        
    return crud_history.delete_history(db=db, history_id=id)


# ==========================================
# 2. API QUẢN TRỊ (Chỉ Admin)
# ==========================================

@router.get("/", response_model=List[History])
def read_all_histories(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_admin: User = Depends(get_current_admin_user) # Chặn người dùng thường
) -> Any:
    """Lấy toàn bộ lịch sử của hệ thống (Dành cho Admin theo dõi)"""
    return crud_history.get_all_histories(db=db, skip=skip, limit=limit)