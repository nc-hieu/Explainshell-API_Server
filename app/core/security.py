from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext

# ==========================================
# CẤU HÌNH BẢO MẬT & JWT
# ==========================================
# Lưu ý: Trong thực tế, SECRET_KEY nên được giấu trong file .env
SECRET_KEY = "explainshell_super_secret_key_thay_doi_trong_production" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # Token có hạn trong 7 ngày

# Cấu hình CryptContext sử dụng thuật toán bcrypt để băm mật khẩu
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ==========================================
# 1. CÁC HÀM XỬ LÝ MẬT KHẨU (PASSWORD)
# ==========================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Kiểm tra xem mật khẩu người dùng nhập vào có khớp với mã băm trong DB không.
    Dùng khi Login.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Băm mật khẩu thành một chuỗi mã hóa không thể dịch ngược.
    Cắt ngắn xuống 72 ký tự để tránh lỗi giới hạn của Bcrypt.
    """
    if isinstance(password, str):
        password = password[:72] 
    return pwd_context.hash(password)


# ==========================================
# 2. CÁC HÀM XỬ LÝ TOKEN (JWT)
# ==========================================

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt