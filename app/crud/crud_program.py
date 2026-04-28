from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func
from app.models.program import Program
from app.models.category import Category
from app.schemas.program import ProgramCreate, ProgramUpdate
from typing import List, Optional

# ==========================================
# 1. CÁC HÀM ĐỌC DỮ LIỆU (READ)
# ==========================================

def get_program(db: Session, program_id: int) -> Optional[Program]:
    """Lấy thông tin Program và kèm theo danh mục của nó"""
    return db.query(Program)\
             .filter(Program.id == program_id)\
             .options(selectinload(Program.categories))\
             .first()

def get_programs(db: Session, skip: int = 0, limit: int = 100) -> List[Program]:
    """Lấy danh sách Program kèm danh mục"""
    return db.query(Program)\
             .options(selectinload(Program.categories))\
             .offset(skip).limit(limit).all()


def get_program_by_name(db: Session, name: str):
    """Lấy lệnh theo tên (Để kiểm tra trùng lặp khi tạo mới)"""
    return db.query(Program).filter(Program.name == name).options(selectinload(Program.categories)).first()

def get_program_by_slug(db: Session, slug: str):
    """Lấy lệnh theo slug (Để kiểm tra trùng lặp khi tạo mới)"""
    return db.query(Program).filter(Program.slug == slug).options(selectinload(Program.categories)).first()

def get_program_by_slug(db: Session, slug: str):
    """
    [QUAN TRỌNG] Lấy toàn bộ chi tiết của 1 lệnh dựa vào Slug (Phục vụ SEO URL).
    Dùng `selectinload` để tải sẵn Categories, Options, Groups và Examples.
    """
    return db.query(Program).options(
        selectinload(Program.categories),
        selectinload(Program.option_groups),
        selectinload(Program.options),
        selectinload(Program.examples)
        # selectinload(Program.man_pages) # Bỏ comment nếu bạn muốn kéo luôn Man Page
    ).filter(Program.slug == slug).first()

def get_program_details(db: Session, program_id: int):
    """
    [QUAN TRỌNG] Lấy toàn bộ chi tiết của 1 lệnh.
    Dùng `selectinload` để tải sẵn Categories, Options, Groups và Examples.
    Việc này giúp tránh lỗi N+1 Query, tăng tốc độ phản hồi API lên gấp nhiều lần!
    """
    return db.query(Program).options(
        selectinload(Program.categories),
        selectinload(Program.option_groups),
        selectinload(Program.options),
        selectinload(Program.examples)
        # selectinload(Program.man_pages) # Mở ra nếu bạn dùng bảng này
    ).filter(Program.id == program_id).first()

def search_programs(db: Session, query: str):
    """
    Tìm kiếm Full-text bằng TSVECTOR trong PostgreSQL.
    Sử dụng toán tử @@ để match với vector đã được index.
    """
    return db.query(Program).filter(
        Program.fts_program_vector.op('@@')(func.plainto_tsquery('english', query))
    ).all()


def get_programs_by_category_slug(db: Session, category_slug: str) -> List[Program]:
    """
    Lấy danh sách các lệnh thuộc về một Danh mục (dựa vào slug).
    BAO GỒM CẢ: Các lệnh nằm trong danh mục con của danh mục đó.
    """
    # 1. Tìm Category gốc dựa vào slug
    category = db.query(Category).filter(Category.slug == category_slug).first()
    if not category:
        return []

    # 2. Lấy ID của category này VÀ các category con trực tiếp của nó
    # (Nếu hệ thống của bạn chỉ gán lệnh vào category con thì nó vẫn quét chuẩn)
    category_ids = [category.id]
    for sub in category.subcategories:
        category_ids.append(sub.id)

    # 3. Query JOIN để lấy các Program có chứa ít nhất 1 category_id nằm trong danh sách trên
    # Dùng distinct() để tránh việc 1 lệnh thuộc cả cha lẫn con bị nhân đôi kết quả
    programs = db.query(Program)\
                 .join(Program.categories)\
                 .filter(Category.id.in_(category_ids))\
                 .distinct()\
                 .all()
                 
    return programs

# ==========================================
# 2. CÁC HÀM GHI DỮ LIỆU (CREATE, UPDATE, DELETE)
# ==========================================

def create_program(db: Session, program_in: ProgramCreate):
    """Tạo lệnh mới, có xử lý tự động gán Danh mục (Categories)"""
    
    # 1. Tách category_ids ra khỏi dữ liệu chính (vì bảng Program không có cột này)
    program_data = program_in.dict(exclude={"category_ids"})
    db_program = Program(**program_data)
    
    # 2. Xử lý gán danh mục nếu người dùng có gửi lên
    if program_in.category_ids:
        categories = db.query(Category).filter(Category.id.in_(program_in.category_ids)).all()
        db_program.categories = categories # SQLAlchemy sẽ tự động lưu vào bảng trung gian program_categories

    db.add(db_program)
    db.commit()
    db.refresh(db_program)
    return db_program

def update_program(db: Session, program_id: int, program_in: ProgramUpdate):
    """Cập nhật lệnh, có hỗ trợ cập nhật lại danh sách Danh mục"""
    db_program = get_program(db, program_id)
    if not db_program:
        return None

    update_data = program_in.dict(exclude_unset=True) # Chỉ lấy những trường được gửi lên
    
    # Xử lý cập nhật danh mục riêng biệt
    if "category_ids" in update_data:
        category_ids = update_data.pop("category_ids")
        # Tìm các danh mục theo ID và gán đè lên danh sách cũ
        categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
        db_program.categories = categories

    # Cập nhật các trường thông tin chữ (name, description, is_featured)
    for key, value in update_data.items():
        setattr(db_program, key, value)

    db.commit()
    db.refresh(db_program)
    return db_program

def delete_program(db: Session, program_id: int):
    """Xóa lệnh (PostgreSQL sẽ tự động CASCADE xóa luôn các Options, Examples...)"""
    db_program = get_program(db, program_id)
    if db_program:
        db.delete(db_program)
        db.commit()
    return db_program

def add_category_to_program(db: Session, program_id: int, category_id: int) -> Optional[Program]:
    """Nối một Danh mục vào một Câu lệnh (Thêm vào bảng trung gian)"""
    program = get_program(db, program_id=program_id)
    category = db.query(Category).filter(Category.id == category_id).first()
    
    # Kiểm tra nếu cả 2 tồn tại và danh mục chưa được gắn vào lệnh này
    if program and category and category not in program.categories:
        program.categories.append(category) # SQLAlchemy tự động xử lý bảng trung gian!
        db.commit()
        db.refresh(program)
        
    return program

def remove_category_from_program(db: Session, program_id: int, category_id: int) -> Optional[Program]:
    """Gỡ một Danh mục khỏi một Câu lệnh (Xóa khỏi bảng trung gian)"""
    program = get_program(db, program_id=program_id)
    category = db.query(Category).filter(Category.id == category_id).first()
    
    # Kiểm tra nếu cả 2 tồn tại và danh mục ĐANG ĐƯỢC GẮN vào lệnh này
    if program and category and category in program.categories:
        program.categories.remove(category) # SQLAlchemy tự động xóa dòng ở bảng trung gian
        db.commit()
        db.refresh(program)
        
    return program


def update_program_categories(db: Session, program_id: int, category_ids: List[int]) -> Optional[Program]:
    """Cập nhật toàn bộ danh mục của một lệnh chỉ bằng 1 mảng ID"""
    program = get_program(db, program_id=program_id)
    if not program:
        return None
        
    # Lấy toàn bộ các object Category hợp lệ dựa vào mảng category_ids gửi lên
    categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
    
    # [PHÉP MÀU SQLALCHEMY] - Gán thẳng mảng object mới vào relationship.
    # SQLAlchemy sẽ tự động so sánh với mảng cũ để xóa cái thừa và thêm cái thiếu!
    program.categories = categories
    
    db.commit()
    db.refresh(program)
    return program


def bulk_update_program_categories(
    db: Session, 
    program_ids: List[int], 
    category_ids: List[int]
) -> List[Program]:
    """
    Cập nhật hàng loạt. 
    Lấy ra tất cả các Program trong mảng program_ids,
    sau đó gán lại mảng categories của chúng bằng các category_ids mới.
    """
    if not program_ids:
        return []

    # 1. Lấy tất cả các Object Program cần cập nhật
    programs = db.query(Program).filter(Program.id.in_(program_ids)).all()
    
    # 2. Lấy tất cả các Object Category chuẩn bị gán vào
    categories = []
    if category_ids:
        categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
        
    # 3. Lặp qua từng lệnh và gán mảng danh mục mới (SQLAlchemy sẽ tự lo việc thêm/xóa ở bảng trung gian)
    for program in programs:
        program.categories = categories
        
    # 4. Lưu toàn bộ thay đổi chỉ với 1 lần commit
    db.commit()
    
    # Tùy chọn: Làm mới (refresh) dữ liệu để trả về cho chắc chắn
    for program in programs:
        db.refresh(program)
        
    return programs