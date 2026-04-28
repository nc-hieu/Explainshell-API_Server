from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

# Import hàm băm mật khẩu từ core (Giả định bạn đang dùng thư viện passlib/bcrypt)
from app.core.security import get_password_hash 

# ==========================================
# 1. CÁC HÀM ĐỌC DỮ LIỆU (READ)
# ==========================================

def get_user(db: Session, user_id: int) -> Optional[User]:
    """Lấy thông tin User theo ID"""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Lấy User theo Email (Dùng khi đăng nhập hoặc kiểm tra trùng lặp)"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Lấy User theo Username (Kiểm tra trùng lặp khi đăng ký)"""
    return db.query(User).filter(User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Lấy danh sách tất cả Users (Chỉ dành cho Admin)"""
    return db.query(User).offset(skip).limit(limit).all()


# ==========================================
# 2. CÁC HÀM GHI DỮ LIỆU (CREATE, UPDATE, DELETE)
# ==========================================

def create_user(db: Session, user_in: UserCreate) -> User:
    """Tạo mới User (Có xử lý băm mật khẩu)"""
    
    # 1. Băm mật khẩu từ dữ liệu gốc
    hashed_password = get_password_hash(user_in.password)
    
    # 2. Tạo object User mới, KHÔNG truyền password gốc vào
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        password=hashed_password, # Lưu password đã băm
        roles=user_in.roles,
        is_active=user_in.is_active
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, db_user: User, user_in: UserUpdate) -> User:
    """Cập nhật thông tin User (Nếu có password mới thì băm lại)"""
    
    # Chuyển đổi dữ liệu update sang dict, loại bỏ những trường không gửi lên
    update_data = user_in.dict(exclude_unset=True)
    
    # Nếu người dùng muốn đổi mật khẩu, ta phải băm mật khẩu mới đó
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        update_data["password"] = hashed_password
        
    # Cập nhật các trường còn lại vào db_user
    for field, value in update_data.items():
        setattr(db_user, field, value)
        
    # db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> Optional[User]:
    """Xóa User khỏi hệ thống"""
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user