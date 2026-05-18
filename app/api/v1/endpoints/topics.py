from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Import CRUD và Schemas
from app.crud import crud_topic
from app.schemas.topic import Topic, TopicCreate, TopicUpdate, TopicWithCategories, TopicStats, TopicBulkStatsRequest, TopicWithRootCategories

# Import DB và Auth
from app.db.session import get_db
from app.api.deps import get_current_admin_user
from app.models.user import User

router = APIRouter()

# ==========================================
# 1. API ĐỌC DỮ LIỆU (Public)
# ==========================================

@router.get("/", response_model=List[Topic])
def read_topics(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    is_featured: Optional[bool] = None
) -> Any:
    """Lấy danh sách các Topic (Hệ sinh thái)"""
    return crud_topic.get_topics(db=db, skip=skip, limit=limit, is_featured=is_featured)

@router.post("/bulk-stats", response_model=List[TopicStats])
def get_bulk_topics_stats_api(
    *,
    db: Session = Depends(get_db),
    payload: TopicBulkStatsRequest
) -> Any:
    """
    [TIỆN ÍCH FRONTEND] Lấy thống kê số lượng (danh mục + lệnh) cho MỘT CHUỖI Topic.
    Truyền vào body: {"topic_ids": [1, 2, 3]}
    Rất tiện để load con số thống kê cho các thẻ Hệ sinh thái ở trang chủ.
    """
    return crud_topic.get_multiple_topic_stats(db=db, topic_ids=payload.topic_ids)


@router.get("/{topic_id}/stats", response_model=TopicStats)
def get_single_topic_stats_api(
    topic_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    [TIỆN ÍCH] Lấy thống kê số lượng của ĐÚNG 1 Topic.
    """
    stats = crud_topic.get_topic_stats(db=db, topic_id=topic_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Không tìm thấy Hệ sinh thái này.")
    return stats

@router.get("/slug/{slug}/root-categories", response_model=TopicWithRootCategories)
def read_topic_with_root_categories_api(
    slug: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    [TIỆN ÍCH FRONTEND] Lấy chi tiết thông tin 1 Topic theo Slug,
    KÈM THEO danh sách các Danh mục gốc (Cấp 1 - parent_id = null) của Topic đó.
    Rất hoàn hảo để vẽ trang chủ của từng Hệ sinh thái (Ví dụ: Trang chủ Linux, Trang chủ Docker).
    """
    topic = crud_topic.get_topic_with_only_root_categories(db=db, slug=slug)
    if not topic:
        raise HTTPException(status_code=404, detail="Không tìm thấy Hệ sinh thái (Topic) này.")
    return topic

@router.get("/slug/{slug}", response_model=TopicWithCategories)
def read_topic_by_slug(
    slug: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Lấy chi tiết một Topic dựa vào Slug (Phục vụ SEO).
    [QUAN TRỌNG] API này sẽ trả về cả mảng 'categories' (các danh mục con) nằm trong Topic này.
    """
    topic = crud_topic.get_topic_by_slug(db=db, slug=slug)
    if not topic:
        raise HTTPException(status_code=404, detail="Không tìm thấy Hệ sinh thái (Topic) này.")
    return topic


# ==========================================
# 2. API GHI DỮ LIỆU (Chỉ Admin)
# ==========================================

@router.post("/", response_model=Topic, status_code=status.HTTP_201_CREATED)
def create_topic_api(
    *,
    db: Session = Depends(get_db),
    topic_in: TopicCreate,
    current_admin: User = Depends(get_current_admin_user)
) -> Any:
    """Tạo mới một Topic (Chỉ Admin)"""
    # Kiểm tra trùng tên
    if crud_topic.get_topic_by_name(db=db, name=topic_in.name):
        raise HTTPException(status_code=400, detail="Tên Topic này đã tồn tại.")
        
    # Kiểm tra trùng slug
    if crud_topic.get_topic_by_slug(db=db, slug=topic_in.slug):
        raise HTTPException(status_code=400, detail="Slug này đã tồn tại, vui lòng chọn slug khác.")
        
    return crud_topic.create_topic(db=db, topic_in=topic_in)

@router.put("/{topic_id}", response_model=Topic)
def update_topic_api(
    *,
    db: Session = Depends(get_db),
    topic_id: int,
    topic_in: TopicUpdate,
    current_admin: User = Depends(get_current_admin_user)
) -> Any:
    """Cập nhật thông tin Topic (Chỉ Admin)"""
    topic = crud_topic.get_topic(db=db, topic_id=topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Không tìm thấy Topic này.")
        
    # Bắt lỗi trùng tên/slug nếu có thay đổi
    if topic_in.name and topic_in.name != topic.name:
        if crud_topic.get_topic_by_name(db=db, name=topic_in.name):
            raise HTTPException(status_code=400, detail="Tên Topic mới đã bị trùng.")
            
    if topic_in.slug and topic_in.slug != topic.slug:
        if crud_topic.get_topic_by_slug(db=db, slug=topic_in.slug):
            raise HTTPException(status_code=400, detail="Slug mới đã bị trùng.")
            
    return crud_topic.update_topic(db=db, db_topic=topic, topic_in=topic_in)

@router.delete("/{topic_id}", response_model=Topic)
def delete_topic_api(
    *,
    db: Session = Depends(get_db),
    topic_id: int,
    current_admin: User = Depends(get_current_admin_user)
) -> Any:
    """Xóa một Topic (Chỉ Admin)"""
    topic = crud_topic.get_topic(db=db, topic_id=topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Không tìm thấy Topic này.")
        
    return crud_topic.delete_topic(db=db, topic_id=topic_id)