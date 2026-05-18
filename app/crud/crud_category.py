from typing import List, Optional
from sqlalchemy.orm import Session, selectinload, with_parent
from app.models.category import Category
from app.models.program import Program
from app.models.topic import Topic
from app.schemas.category import CategoryCreate, CategoryUpdate

# ==========================================
# 1. CÁC HÀM ĐỌC DỮ LIỆU (READ)
# ==========================================

def get_category(db: Session, category_id: int) -> Optional[Category]:
    return db.query(Category)\
             .filter(Category.id == category_id)\
             .options(
                 selectinload(Category.programs),
                 selectinload(Category.topic) 
             )\
             .first()

def get_category_by_slug(db: Session, slug: str) -> Optional[Category]:
    return db.query(Category)\
             .filter(Category.slug == slug)\
             .options(
                 selectinload(Category.programs),
                 selectinload(Category.topic)
             )\
             .first()

def get_categories(db: Session, skip: int = 0, limit: int = 100, topic_id: Optional[int] = None) -> List[Category]:
    """Lấy danh sách danh mục (có hỗ trợ lọc theo topic_id)"""
    query = db.query(Category).options(selectinload(Category.topic))
    
    if topic_id is not None:
        query = query.filter(Category.topic_id == topic_id)
        
    return query.offset(skip).limit(limit).all()

def get_category_tree(db: Session, topic_id: Optional[int] = None) -> List[Category]:
    """
    Lấy danh sách danh mục theo dạng cây (Gốc -> Bậc 2 -> Bậc 3).
    [CẬP NHẬT]: Hỗ trợ lọc theo topic_id để hiển thị cây của từng Hệ sinh thái riêng biệt.
    """
    query = db.query(Category).filter(Category.parent_id == None)
    
    # Nếu truyền topic_id, chỉ lấy các danh mục gốc thuộc topic đó
    if topic_id is not None:
        query = query.filter(Category.topic_id == topic_id)
        
    return query.options(
        selectinload(Category.topic), # Tải thông tin Topic
        selectinload(Category.subcategories)\
        .selectinload(Category.subcategories)
    ).all()


# 1. Hàm lấy danh mục gốc (cha)
def get_root_categories(db: Session, topic_slug: Optional[str] = None) -> List[Category]:
    """
    Lấy danh sách các danh mục cấp 1 (Không có parent_id).
    [CẬP NHẬT]: Có hỗ trợ lọc theo topic_id (Hệ sinh thái).
    """
    query = db.query(Category).filter(Category.parent_id.is_(None))
    
    # Nếu có truyền topic_slug, thêm điều kiện lọc
    if topic_slug:
        query = query.join(Category.topic).filter(Topic.slug == topic_slug)
        
    return query.all()

# 2. Hàm đếm số lượng cho 1 danh mục
def get_category_stats(db: Session, category_id: int) -> Optional[dict]:
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        return None
        
    sub_count = db.query(Category).filter(Category.parent_id == category_id).count()
    
    # Sửa lại dòng này: dùng chuỗi 'programs' thay vì Category.programs
    prog_count = db.query(Program).with_parent(category, Category.programs).count()
    
    return {
        "category_id": category_id,
        "subcategories_count": sub_count,
        "programs_count": prog_count
    }

# 3. Hàm đếm số lượng cho 1 mảng danh mục
def get_multiple_category_stats(db: Session, category_ids: List[int]) -> List[dict]:
    """Lặp qua mảng ID và trả về thống kê của từng cái"""
    results = []
    for cid in category_ids:
        stats = get_category_stats(db, cid)
        if stats:
            results.append(stats)
    return results

# ==========================================
# 2. CÁC HÀM GHI DỮ LIỆU (CREATE, UPDATE, DELETE)
# ==========================================

def create_category(db: Session, category_in: CategoryCreate) -> Category:
    """Tạo mới một danh mục"""
    db_category = Category(**category_in.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def update_category(db: Session, db_category: Category, category_in: CategoryUpdate) -> Category:
    """Cập nhật danh mục"""
    update_data = category_in.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_category, field, value)
        
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int) -> Optional[Category]:
    """
    Xóa danh mục.
    LƯU Ý: Do thiết lập ondelete="SET NULL" ở parent_id,
    nếu xóa danh mục cha, các danh mục con sẽ trở thành danh mục gốc (parent_id = NULL).
    """
    db_category = get_category(db, category_id)
    if db_category:
        db.delete(db_category)
        db.commit()
    return db_category

