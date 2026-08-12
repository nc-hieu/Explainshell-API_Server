from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class OSDistributionBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None

class OSDistributionCreate(OSDistributionBase):
    pass

class OSDistributionUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None

class OSDistribution(OSDistributionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True