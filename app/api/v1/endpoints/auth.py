from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.crud.crud_user import get_user_by_username

from app.core.security import verify_password, create_access_token
from app.schemas.token import Token
from app.db.session import get_db

router = APIRouter()

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    API Đăng nhập (OAuth2 compatible).
    Lấy thông tin username/password từ Form, trả về JWT Access Token.
    """
    # 1. Tìm user trong Database theo username
    user = get_user_by_username(db, username=form_data.username)
    
    # 2. Kiểm tra user có tồn tại không & mật khẩu có khớp không
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không chính xác",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 3. Kiểm tra xem tài khoản có đang bị khóa không
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Tài khoản này đã bị khóa")

    # 4. Đăng nhập thành công -> Tạo và trả về JWT Token
    return {
        "access_token": create_access_token(subject=user.id),
        "token_type": "bearer",
    }