from fastapi import FastAPI
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
    allow_origins=["*"], # Trong thực tế nên giới hạn lại domain của ReactJS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Kết nối router tổng
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Wellcome to the Explainshell API!"}