from typing import List, Optional
from sqlalchemy.orm import Session, selectinload

from app.models.topic import Topic
from app.schemas.topic import TopicCreate, TopicUpdate

from app.models.category import Category
from app.models.program import Program

# ==========================================
# 1. CÁC HÀM ĐỌC DỮ LIỆU (READ)
# ==========================================

def get_topic(db: Session, topic_id: int) -> Optional[Topic]:
    """Lấy thông tin Topic theo ID cơ bản"""
    return db.query(Topic).filter(Topic.id == topic_id).first()

def get_topic_by_slug(db: Session, slug: str) -> Optional[Topic]:
    """
    Lấy thông tin Topic theo Slug.
    [QUAN TRỌNG]: Dùng selectinload để kéo theo toàn bộ mảng categories nằm trong Topic này.
    Rất phù hợp khi truy cập trang chi tiết của Topic (VD: /topic/linux)
    """
    return db.query(Topic)\
             .filter(Topic.slug == slug)\
             .options(selectinload(Topic.categories))\
             .first()

def get_topic_by_name(db: Session, name: str) -> Optional[Topic]:
    """Lấy Topic theo tên (Dùng để check trùng lặp khi tạo mới)"""
    return db.query(Topic).filter(Topic.name == name).first()

def get_topics(db: Session, skip: int = 0, limit: int = 100, is_featured: Optional[bool] = None) -> List[Topic]:
    """
    Lấy danh sách Topics.
    Hỗ trợ lọc theo is_featured (Topic nổi bật) để hiển thị ngoài trang chủ.
    """
    query = db.query(Topic)
    if is_featured is not None:
        query = query.filter(Topic.is_featured == is_featured)
        
    # Sắp xếp mới nhất lên đầu hoặc có thể thêm cột order/position nếu cần
    return query.order_by(Topic.created_at.desc()).offset(skip).limit(limit).all()

def get_topic_with_only_root_categories(db: Session, slug: str) -> Optional[Topic]:
    """
    Tìm Topic theo slug và chỉ lấy các danh mục gốc (parent_id is null) trực thuộc nó.
    """
    # 1. Lấy thông tin Topic trước
    topic = db.query(Topic).filter(Topic.slug == slug).first()
    if not topic:
        return None

    # 2. Truy vấn riêng danh sách danh mục gốc thuộc topic này để tối ưu performance
    root_categories = db.query(Category).filter(
        Category.topic_id == topic.id,
        Category.parent_id.is_(None)
    ).all()

    # 3. Gán tạm mảng danh mục gốc này vào thuộc tính categories của object topic trước khi trả về
    # Pydantic dựa vào đây để map dữ liệu ra JSON cực kỳ sạch sẽ
    topic.categories = root_categories
    
    return topic

# ==========================================
# 2. CÁC HÀM GHI DỮ LIỆU (CREATE, UPDATE, DELETE)
# ==========================================

def create_topic(db: Session, topic_in: TopicCreate) -> Topic:
    """Tạo mới một Topic"""
    db_topic = Topic(**topic_in.model_dump()) # model_dump() thay cho dict() ở pydantic v2
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return db_topic

def update_topic(db: Session, db_topic: Topic, topic_in: TopicUpdate) -> Topic:
    """Cập nhật Topic"""
    update_data = topic_in.model_dump(exclude_unset=True) # Chỉ cập nhật các trường được gửi lên
    
    for field, value in update_data.items():
        setattr(db_topic, field, value)
        
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return db_topic

def delete_topic(db: Session, topic_id: int) -> Optional[Topic]:
    """Xóa một Topic (các Category con sẽ bị xóa theo nếu thiết lập cascade='all, delete-orphan')"""
    db_topic = get_topic(db, topic_id)
    if db_topic:
        db.delete(db_topic)
        db.commit()
    return db_topic

# ==========================================
# 3. CÁC HÀM THỐNG KÊ (STATS)
# ==========================================

def get_topic_stats(db: Session, topic_id: int) -> Optional[dict]:
    """Đếm số lượng danh mục và số lượng lệnh của 1 Topic"""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        return None
        
    # Đếm số danh mục (Category) trực thuộc Topic này
    cat_count = db.query(Category).filter(Category.topic_id == topic_id).count()
    
    # Đếm số lệnh (Program) nằm trong các danh mục thuộc Topic này.
    # Dùng distinct() để tránh đếm đúp nếu 1 lệnh thuộc nhiều danh mục trong cùng 1 topic.
    prog_count = db.query(Program)\
                   .join(Program.categories)\
                   .filter(Category.topic_id == topic_id)\
                   .distinct()\
                   .count()
    
    return {
        "topic_id": topic_id,
        "categories_count": cat_count,
        "programs_count": prog_count
    }

def get_multiple_topic_stats(db: Session, topic_ids: List[int]) -> List[dict]:
    """Lặp qua mảng ID và trả về thống kê của từng Topic"""
    results = []
    for tid in set(topic_ids): # Dùng set() để loại bỏ các ID trùng lặp gửi lên
        stats = get_topic_stats(db, tid)
        if stats:
            results.append(stats)
    return results