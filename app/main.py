from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles # Import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import app.db.base
from app.api.v1.api import api_router

app = FastAPI(
    title="Explainshell API",
    description="Backend for project command shell solution",
    version="1.0.0"
)

# Cấu hình CORS để ReactJS (thường chạy ở port 3000) có thể gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Giới hạn lại domain của ReactJS nếu đưa lên production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Phục vụ thư mục uploads
# Ảnh lưu tại uploads/icon.png có thể xem qua URL: http://localhost:8000/uploads/icon.png
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Kết nối router tổng
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Wellcome to the Explainshell API!"}