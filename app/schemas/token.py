from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    """Schema trả về cho Frontend khi đăng nhập thành công"""
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    """Schema dùng để giải mã JWT (lấy ID của user)"""
    sub: Optional[str] = None