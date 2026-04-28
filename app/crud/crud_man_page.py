from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.man_page import ManPage
from app.schemas.man_page import ManPageCreate, ManPageUpdate

# ==========================================
# 1. CÁC HÀM ĐỌC DỮ LIỆU (READ)
# ==========================================

def get_man_page(db: Session, man_page_id: int) -> Optional[ManPage]:
    """Lấy chi tiết một trang tài liệu theo ID"""
    return db.query(ManPage).filter(ManPage.id == man_page_id).first()

def get_man_pages_by_program(db: Session, program_id: int) -> List[ManPage]:
    """
    Lấy danh sách tất cả các trang tài liệu (các sections) của một Câu lệnh (Program).
    Sắp xếp theo section.
    """
    return db.query(ManPage)\
             .filter(ManPage.program_id == program_id)\
             .order_by(ManPage.section.asc())\
             .all()


# ==========================================
# 2. CÁC HÀM GHI DỮ LIỆU (CREATE, UPDATE, DELETE)
# ==========================================

def create_man_page(db: Session, program_id: int, man_page_in: ManPageCreate) -> ManPage:
    """Tạo mới một trang tài liệu và gắn vào Program"""
    db_man_page = ManPage(**man_page_in.dict(), program_id=program_id)
    db.add(db_man_page)
    db.commit()
    db.refresh(db_man_page)
    return db_man_page

def update_man_page(db: Session, db_man_page: ManPage, man_page_in: ManPageUpdate) -> ManPage:
    """Cập nhật nội dung của trang tài liệu"""
    update_data = man_page_in.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_man_page, field, value)
        
    db.add(db_man_page)
    db.commit()
    db.refresh(db_man_page)
    return db_man_page

def delete_man_page(db: Session, man_page_id: int) -> Optional[ManPage]:
    """Xóa một trang tài liệu"""
    db_man_page = get_man_page(db, man_page_id)
    if db_man_page:
        db.delete(db_man_page)
        db.commit()
    return db_man_page