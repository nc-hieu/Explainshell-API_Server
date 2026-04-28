from datetime import datetime, timedelta
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
    Dùng khi Đăng ký hoặc Admin tạo/đổi mật khẩu.
    """
    return pwd_context.hash(password)


# ==========================================
# 2. CÁC HÀM XỬ LÝ TOKEN (JWT)
# ==========================================

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """
    Tạo ra một chuỗi JWT mã hóa thông tin người dùng (subject thường là user_id).
    Token này là "chìa khóa" để gọi các API Private.
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt