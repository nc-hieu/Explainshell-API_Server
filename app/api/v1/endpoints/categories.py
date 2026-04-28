from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Import CRUD và Schemas
from app.crud import crud_category
from app.schemas.category import Category, CategoryCreate, CategoryUpdate, CategoryWithSub, CategoryStats, CategoryBulkStatsRequest, CategoryBasic

# Import DB và Dependency bảo mật
from app.db.session import get_db
from app.api.deps import get_current_admin_user
from app.models.user import User

router = APIRouter()

# ==========================================
# 1. API ĐỌC DỮ LIỆU (PUBLIC - Ai cũng xem được)
# ==========================================

# LƯU Ý: Phải đặt API /tree lên TRƯỚC API /{id} để FastAPI không nhầm chữ "tree" là một ID
@router.get("/tree", response_model=List[CategoryWithSub])
def read_category_tree(
    db: Session = Depends(get_db)
) -> Any:
    """
    Lấy danh sách danh mục theo cấu trúc Cây (Tree).
    Trả về các danh mục gốc (parent_id = null) và lồng ghép sẵn các danh mục con bên trong.
    Tuyệt vời để làm Sidebar Menu cho Frontend.
    """
    return crud_category.get_category_tree(db)

@router.get("/roots", response_model=List[CategoryBasic])
def read_root_categories(
    db: Session = Depends(get_db)
) -> Any:
    """
    [TIỆN ÍCH] Lấy danh sách các Danh mục gốc (Cấp 1 - parent_id = null).
    Thường dùng để vẽ Menu chính hoặc Sidebar.
    """
    return crud_category.get_root_categories(db=db)

@router.post("/bulk-stats", response_model=List[CategoryStats])
def get_bulk_categories_stats_api(
    *,
    db: Session = Depends(get_db),
    payload: CategoryBulkStatsRequest
) -> Any:
    """
    [TIỆN ÍCH] Lấy thống kê số lượng (con + lệnh) cho MỘT CHUỖI danh mục.
    Truyền vào body: {"category_ids": [1, 2, 3]}
    """
    return crud_category.get_multiple_category_stats(db=db, category_ids=payload.category_ids)

@router.get("/", response_model=List[Category])
def read_categories(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """Lấy danh sách danh mục cơ bản (Hỗ trợ phân trang)"""
    return crud_category.get_categories(db, skip=skip, limit=limit)

@router.get("/slug/{slug}", response_model=CategoryWithSub)
def read_category_by_slug(
    slug: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Lấy thông tin danh mục dựa vào Slug (VD: /categories/slug/file-system).
    Rất tốt cho SEO URL. Trả về kèm luôn cả các danh mục con của nó.
    """
    category = crud_category.get_category_by_slug(db, slug=slug)
    if not category:
        raise HTTPException(status_code=404, detail="Không tìm thấy danh mục.")
    return category


@router.get("/{category_id}/stats", response_model=CategoryStats)
def get_single_category_stats_api(
    category_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    [TIỆN ÍCH] Lấy thống kê số lượng của ĐÚNG 1 danh mục.
    """
    stats = crud_category.get_category_stats(db=db, category_id=category_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Không tìm thấy danh mục này.")
    return stats

@router.get("/{id}", response_model=CategoryWithSub)
def read_category_by_id(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    """Lấy thông tin một danh mục theo ID"""
    category = crud_category.get_category(db, category_id=id)
    if not category:
        raise HTTPException(status_code=404, detail="Không tìm thấy danh mục.")
    return category


# ==========================================
# 2. API GHI DỮ LIỆU (PRIVATE - Chỉ Admin)
# ==========================================

@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category_api(
    *,
    db: Session = Depends(get_db),
    category_in: CategoryCreate,
    current_admin: User = Depends(get_current_admin_user) # BẢO VỆ API
) -> Any:
    """Tạo một danh mục mới (Admin)"""
    # Kiểm tra xem slug đã bị trùng chưa (Slug phải là duy nhất)
    category = crud_category.get_category_by_slug(db, slug=category_in.slug)
    if category:
        raise HTTPException(status_code=400, detail="Slug này đã tồn tại, vui lòng chọn slug khác.")
    
    # Nếu có truyền parent_id, kiểm tra xem danh mục cha có tồn tại không
    if category_in.parent_id:
        parent_cat = crud_category.get_category(db, category_id=category_in.parent_id)
        if not parent_cat:
            raise HTTPException(status_code=400, detail="Danh mục cha không tồn tại.")

    return crud_category.create_category(db=db, category_in=category_in)

@router.put("/{id}", response_model=Category)
def update_category_api(
    *,
    db: Session = Depends(get_db),
    id: int,
    category_in: CategoryUpdate,
    current_admin: User = Depends(get_current_admin_user) # BẢO VỆ API
) -> Any:
    """Cập nhật thông tin danh mục (Admin)"""
    category = crud_category.get_category(db, category_id=id)
    if not category:
        raise HTTPException(status_code=404, detail="Không tìm thấy danh mục để cập nhật.")
    
    # Tránh trường hợp Admin tự gán parent_id bằng chính id của nó (gây vòng lặp vô tận)
    if category_in.parent_id == id:
        raise HTTPException(status_code=400, detail="Một danh mục không thể làm cha của chính nó.")

    # Nếu đổi slug, phải check trùng lặp
    if category_in.slug and category_in.slug != category.slug:
        existing_cat = crud_category.get_category_by_slug(db, slug=category_in.slug)
        if existing_cat:
            raise HTTPException(status_code=400, detail="Slug mới đã bị trùng lặp.")

    return crud_category.update_category(db=db, db_category=category, category_in=category_in)

@router.delete("/{id}", response_model=Category)
def delete_category_api(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_admin: User = Depends(get_current_admin_user) # BẢO VỆ API
) -> Any:
    """Xóa một danh mục (Admin)"""
    category = crud_category.get_category(db, category_id=id)
    if not category:
        raise HTTPException(status_code=404, detail="Không tìm thấy danh mục để xóa.")
    return crud_category.delete_category(db=db, category_id=id)



