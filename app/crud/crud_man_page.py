from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.man_page import ManPage
from app.schemas.man_page import ManPageCreate, ManPageUpdate

def get_man_page(db: Session, man_page_id: int) -> Optional[ManPage]:
    return db.query(ManPage).options(joinedload(ManPage.os)).filter(ManPage.id == man_page_id).first()

def get_man_pages_by_program(db: Session, program_id: int) -> List[ManPage]:
    """Lấy danh sách tài liệu hướng dẫn của một câu lệnh"""
    return db.query(ManPage).options(joinedload(ManPage.os)).filter(ManPage.program_id == program_id).all()

def create_man_page(db: Session, man_page_in: ManPageCreate) -> ManPage:
    db_man_page = ManPage(**man_page_in.model_dump())
    db.add(db_man_page)
    db.commit()
    db.refresh(db_man_page)
    return get_man_page(db, db_man_page.id) or db_man_page

def update_man_page(db: Session, db_man_page: ManPage, man_page_in: ManPageUpdate) -> ManPage:
    update_data = man_page_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_man_page, field, value)
    db.add(db_man_page)
    db.commit()
    db.refresh(db_man_page)
    return get_man_page(db, db_man_page.id) or db_man_page

def delete_man_page(db: Session, man_page_id: int) -> Optional[ManPage]:
    db_man_page = get_man_page(db, man_page_id)
    if db_man_page:
        # Load quan hệ os trước
        _ = db_man_page.os
        # Tách object ra khỏi session để giữ data trong RAM phục vụ serialize response
        db.expunge(db_man_page)
        db.query(ManPage).filter(ManPage.id == man_page_id).delete()
        db.commit()
    return db_man_page