from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.schemas.os_distribution import OSDistribution

class ManPageBase(BaseModel):
    section: Optional[int] = None
    content: Optional[str] = None
    source_url: Optional[str] = None
    program_id: int
    os_id: Optional[int] = None

class ManPageCreate(ManPageBase):
    pass

class ManPageUpdate(BaseModel):
    section: Optional[int] = None
    content: Optional[str] = None
    source_url: Optional[str] = None
    os_id: Optional[int] = None

class ManPage(ManPageBase):
    id: int
    updated_at: datetime
    # Trả về thông tin OS đi kèm (rất tốt cho Frontend hiển thị tên hệ điều hành)
    os: Optional[OSDistribution] = None

    class Config:
        from_attributes = True