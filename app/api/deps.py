from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session
from typing import Optional

# Import cấu hình và DB
from app.db.session import SessionLocal, get_db
from app.core.security import SECRET_KEY, ALGORITHM

# Import Models, Schemas, CRUD
from app.models.user import User
from app.schemas.token import TokenPayload
from app.crud.crud_user import (
    get_user,
    get_users, 
)

# Cấu hình OAuth2: Khai báo URL mà Frontend sẽ gọi để lấy Token
# Đường dẫn này phải khớp chính xác với router auth.py (không có dấu gạch chéo ở cuối)
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)


# ==========================================
# DEPENDENCY TÙY CHỌN (KHÔNG BẮT BUỘC ĐĂNG NHẬP)
# ==========================================
# auto_error=False giúp FastAPI không quăng lỗi 401 nếu request không có Token
reusable_oauth2_optional = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False 
)

def get_current_user_optional(
    db: Session = Depends(get_db), 
    token: Optional[str] = Depends(reusable_oauth2_optional)
) -> Optional[User]:
    """
    Dependency này dùng cho các API dạng "Public nhưng có ưu đãi cho User".
    - Nếu không có token -> Trả về None (Không báo lỗi)
    - Nếu có token -> Giải mã và trả về object User.
    - Nếu token sai/hết hạn -> Vẫn trả về None để coi như là khách.
    """
    if not token:
        return None
        
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        return None
    
    user = get_user(db, user_id=int(token_data.sub))
    return user


# ==========================================
# 1. DEPENDENCY XÁC THỰC NGƯỜI DÙNG BẰNG TOKEN
# ==========================================
def get_current_user(
    db: Session = Depends(get_db), 
    token: str = Depends(reusable_oauth2)
) -> User:
    """
    Nhận Token từ request, giải mã để lấy user_id, 
    sau đó truy vấn Database để lấy thông tin User.
    """
    try:
        # Giải mã token
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không thể xác thực được chứng chỉ (Token không hợp lệ hoặc đã hết hạn)",
        )
    
    # Lấy thông tin user từ DB dựa vào 'sub' (user_id) trong token
    user = get_user(db, user_id=int(token_data.sub))
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
    
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Kiểm tra xem tài khoản có đang bị khóa (inactive) hay không.
    Dùng cho các API cần đăng nhập (VD: Lấy profile cá nhân /me)
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Tài khoản của bạn đã bị vô hiệu hóa")
    return current_user

# ==========================================
# 2. DEPENDENCY PHÂN QUYỀN QUẢN TRỊ (ADMIN)
# ==========================================
def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Kiểm tra xem user hiện tại có phải là Admin hay không.
    Dùng để bảo vệ các API Thêm/Sửa/Xóa (Programs, Options, Categories...)
    """
    if current_user.roles != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền quản trị (Admin) để thực hiện hành động này"
        )
    return current_user

