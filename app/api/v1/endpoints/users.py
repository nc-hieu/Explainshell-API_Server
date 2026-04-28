from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Import CRUD và Schemas
from app.crud.crud_user import (
    get_user_by_email,
    get_user_by_username,
    create_user,
    update_user,
    delete_user,
    get_users,
    get_user,
)
from app.schemas.user import UserCreate, UserUpdate, UserResponse

# Import DB và Dependency bảo mật
from app.db.session import get_db
from app.api.deps import get_current_active_user, get_current_admin_user
from app.models.user import User

router = APIRouter()

# ==========================================
# 1. API CÁ NHÂN & ĐĂNG KÝ (PUBLIC / USER THƯỜNG)
# ==========================================

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_signup(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate
) -> Any:
    """Đăng ký tài khoản mới (Public)"""
    # Kiểm tra email và username đã tồn tại chưa
    if get_user_by_email(db, email=user_in.email):
        raise HTTPException(status_code=400, detail="Email này đã được sử dụng.")
    if get_user_by_username(db, username=user_in.username):
        raise HTTPException(status_code=400, detail="Tên đăng nhập này đã có người dùng.")
    
    # Ép buộc user đăng ký ngoài luồng luôn là role 'user' để bảo mật
    user_in.roles = "user"
    return create_user(db=db, user_in=user_in)

@router.get("/me", response_model=UserResponse)
def read_user_me(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Lấy thông tin profile của chính mình (Cần Token)"""
    return current_user

@router.put("/me", response_model=UserResponse)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Tự cập nhật thông tin cá nhân của mình"""
    # Không cho phép người dùng tự đổi role của mình thành admin
    if user_in.roles and user_in.roles != current_user.roles:
        raise HTTPException(status_code=403, detail="Bạn không có quyền thay đổi role của mình.")
    
    return update_user(db=db, db_user=current_user, user_in=user_in)


# ==========================================
# 2. API QUẢN TRỊ (CHỈ DÀNH CHO ADMIN)
# ==========================================

@router.get("/", response_model=List[UserResponse])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_admin: User = Depends(get_current_admin_user) # BẢO VỆ API
) -> Any:
    """Lấy danh sách tất cả người dùng (Admin)"""
    return get_users(db, skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserResponse)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
) -> Any:
    """Lấy thông tin một người dùng theo ID (Admin)"""
    user = get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user_by_admin(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    user_in: UserUpdate,
    current_admin: User = Depends(get_current_admin_user)
) -> Any:
    """Cập nhật thông tin bất kỳ ai (Admin có thể đổi cả role)"""
    user = get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
    return update_user(db=db, db_user=user, user_in=user_in)

@router.delete("/{user_id}", response_model=UserResponse)
def delete_user_by_admin(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_admin: User = Depends(get_current_admin_user)
) -> Any:
    """Xóa người dùng (Admin)"""
    user = get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
    # Ngăn Admin tự xóa chính mình
    if user.id == current_admin.id:
        raise HTTPException(status_code=400, detail="Bạn không thể tự xóa chính mình!")
    return delete_user(db=db, user_id=user_id)