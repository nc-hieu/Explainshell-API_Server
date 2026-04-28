# Explainshell - API Server (Backend)

Chào mừng bạn đến với trái tim xử lý dữ liệu của dự án Explainshell Clone. Đây là hệ thống Backend được xây dựng để quản lý, tìm kiếm và giải thích các câu lệnh shell.

## 🚀 Công nghệ sử dụng
* **Ngôn ngữ:** Python 3.10+
* **Framework:** FastAPI (Hiệu suất cao, hỗ trợ Async)
* **Cơ sở dữ liệu:** PostgreSQL
* **ORM:** SQLAlchemy (Quản lý DB qua code Python)
* **Công cụ GUI:** DBeaver

## 🛠 Cài đặt môi trường (Ubuntu)

### 1. Chuẩn bị
Đảm bảo bạn đã cài đặt Python và môi trường ảo:
```python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
### 2. Cấu hình biến môi trường
Tạo file .env tại thư mục gốc và cấu hình theo mẫu:
```python
DATABASE_URL=postgresql://user:password@localhost/explainshell_db
SECRET_KEY=your_secret_key
```
### 3.Chạy Server
```python
uvicorn app.main:app --reload
```
Hệ thống sẽ chạy tại: http://127.0.0.1:8000


## 📂 Cấu trúc thư mục chính
/app/models: Khai báo cấu trúc bảng Database.

/app/api: Định nghĩa các đường dẫn API (Endpoints).

/app/schemas: Quy định định dạng dữ liệu đầu vào/đầu ra (Pydantic).

/app/db: Cấu hình kết nối PostgreSQL.


## 📝 Tính năng hiện có
[x] Quản lý thông tin câu lệnh (programs).

[x] Tra cứu cờ lệnh (options).

[x] Hệ thống tài liệu (man_pages).

[x] API cho trang Admin (CRUD).
