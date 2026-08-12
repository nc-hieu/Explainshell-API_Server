from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.crud import crud_os_distribution
from app.schemas.os_distribution import OSDistribution, OSDistributionCreate, OSDistributionUpdate
from app.api.deps import get_current_admin_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[OSDistribution])
def read_all_os(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> Any:
    return crud_os_distribution.get_all_os(db, skip=skip, limit=limit)

@router.post("/", response_model=OSDistribution, status_code=status.HTTP_201_CREATED)
def create_os(
    *, db: Session = Depends(get_db), os_in: OSDistributionCreate, current_admin: User = Depends(get_current_admin_user)
) -> Any:
    os_exist = crud_os_distribution.get_os_by_slug(db, slug=os_in.slug)
    if os_exist:
        raise HTTPException(status_code=400, detail="Slug hệ điều hành này đã tồn tại.")
    return crud_os_distribution.create_os(db=db, os_in=os_in)

@router.put("/{id}", response_model=OSDistribution)
def update_os(
    *, db: Session = Depends(get_db), id: int, os_in: OSDistributionUpdate, current_admin: User = Depends(get_current_admin_user)
) -> Any:
    os_exist = crud_os_distribution.get_os(db, os_id=id)
    if not os_exist:
        raise HTTPException(status_code=404, detail="Hệ điều hành không tồn tại.")
    return crud_os_distribution.update_os(db=db, db_os=os_exist, os_in=os_in)

@router.delete("/{id}", response_model=OSDistribution)
def delete_os(
    *, db: Session = Depends(get_db), id: int, current_admin: User = Depends(get_current_admin_user)
) -> Any:
    os_exist = crud_os_distribution.get_os(db, os_id=id)
    if not os_exist:
        raise HTTPException(status_code=404, detail="Hệ điều hành không tồn tại.")
    return crud_os_distribution.delete_os(db=db, os_id=id)