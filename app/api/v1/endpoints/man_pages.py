from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.crud import crud_man_page
from app.schemas.man_page import ManPage, ManPageCreate, ManPageUpdate
from app.api.deps import get_current_admin_user
from app.models.user import User

router = APIRouter()

@router.get("/program/{program_id}", response_model=List[ManPage])
def read_man_pages_by_program(program_id: int, db: Session = Depends(get_db)) -> Any:
    return crud_man_page.get_man_pages_by_program(db, program_id=program_id)

@router.post("/", response_model=ManPage, status_code=status.HTTP_201_CREATED)
def create_man_page(
    *, db: Session = Depends(get_db), man_page_in: ManPageCreate, current_admin: User = Depends(get_current_admin_user)
) -> Any:
    return crud_man_page.create_man_page(db=db, man_page_in=man_page_in)

@router.put("/{id}", response_model=ManPage)
def update_man_page(
    *, db: Session = Depends(get_db), id: int, man_page_in: ManPageUpdate, current_admin: User = Depends(get_current_admin_user)
) -> Any:
    man_page_exist = crud_man_page.get_man_page(db, man_page_id=id)
    if not man_page_exist:
        raise HTTPException(status_code=404, detail="Man Page không tồn tại.")
    return crud_man_page.update_man_page(db=db, db_man_page=man_page_exist, man_page_in=man_page_in)

@router.delete("/{id}", response_model=ManPage)
def delete_man_page(
    *, db: Session = Depends(get_db), id: int, current_admin: User = Depends(get_current_admin_user)
) -> Any:
    man_page_exist = crud_man_page.get_man_page(db, man_page_id=id)
    if not man_page_exist:
        raise HTTPException(status_code=404, detail="Man Page không tồn tại.")
    return crud_man_page.delete_man_page(db=db, man_page_id=id)