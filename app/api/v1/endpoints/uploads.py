import os
import shutil
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from typing import Any

from app.api.deps import get_current_admin_user
from app.models.user import User

router = APIRouter()

# Thư mục đích để lưu file (đường dẫn tương đối so với vị trí chạy server)
UPLOAD_DIR = "uploads"

# Đảm bảo thư mục upload tồn tại khi server chạy
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
def upload_image(
    *,
    file: UploadFile = File(...),
    current_admin: User = Depends(get_current_admin_user) # Chỉ Admin mới được upload
) -> Any:
    """
    API Upload ảnh (Chỉ dành cho Admin).
    Nhận file, đổi tên ngẫu nhiên (để tránh trùng lặp) và lưu vào thư mục 'uploads'.
    Trả về đường dẫn URL của ảnh.
    """
    # 1. Kiểm tra định dạng file (Chỉ cho phép ảnh)
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ định dạng hình ảnh.")

    # 2. Tạo tên file mới (Bảo vệ bảo mật và tránh trùng tên file)
    # Lấy đuôi file (ví dụ: .png, .jpg)
    file_extension = os.path.splitext(file.filename)[1]
    # Tạo chuỗi ngẫu nhiên + đuôi file
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    
    # Đường dẫn đầy đủ để lưu file
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # 3. Lưu file vào ổ cứng
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Không thể lưu file: {str(e)}")
    finally:
        file.file.close()

    # 4. Trả về đường dẫn để Frontend sử dụng
    # Lưu ý: Cần điều chỉnh domain nếu bạn deploy lên server thật. Ở đây trả về path tĩnh.
    # Frontend sẽ nối với BASE_URL: http://localhost:8000/uploads/ten_file.png
    return {
        "url": f"/uploads/{unique_filename}",
        "message": "Upload thành công!"
    }