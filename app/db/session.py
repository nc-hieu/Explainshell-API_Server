import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Tải biến môi trường từ file .env
load_dotenv()

# Lấy URL kết nối Database
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# 1. Tạo Engine: Đây là đối tượng quản lý các kết nối thực tế tới DB
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # pool_pre_ping giúp kiểm tra kết nối còn sống hay không trước khi sử dụng
    pool_pre_ping=True
)

# 2. Tạo SessionLocal: Đây là một 'nhà máy' để tạo ra các phiên làm việc (session)
# Chúng ta đặt autocommit=False để có quyền kiểm soát khi nào dữ liệu thực sự được lưu (commit)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Tạo Base class: Tất cả các Model (User, Program...) sẽ kế thừa từ lớp này
Base = declarative_base()

# 4. Hàm Dependency Injection cho FastAPI
def get_db():
    """
    Hàm này tạo ra một session mới cho mỗi yêu cầu (request) API 
    và đảm bảo đóng nó lại sau khi xử lý xong để tránh rò rỉ bộ nhớ.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()