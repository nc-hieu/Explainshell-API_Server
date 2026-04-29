# Sử dụng image Python nhỏ gọn làm nền tảng
FROM python:3.10-slim

# Thiết lập thư mục làm việc bên trong container
WORKDIR /app

# Copy file requirements.txt vào container trước
# (Điều này giúp Docker tận dụng bộ nhớ đệm, cài đặt nhanh hơn ở các lần sau)
COPY requirements.txt .

# Cài đặt các thư viện cần thiết (FastAPI, Uvicorn, SQLAlchemy, psycopg2...)
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn từ máy bạn vào thư mục /app trong container
COPY . .

# Khai báo cổng 8000 để giao tiếp
EXPOSE 8000

# Lệnh khởi chạy server FastAPI khi container bắt đầu chạy
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"
