from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.os_distribution import OSDistribution
from app.schemas.os_distribution import OSDistributionCreate, OSDistributionUpdate

def get_os(db: Session, os_id: int) -> Optional[OSDistribution]:
    return db.query(OSDistribution).filter(OSDistribution.id == os_id).first()

def get_os_by_slug(db: Session, slug: str) -> Optional[OSDistribution]:
    return db.query(OSDistribution).filter(OSDistribution.slug == slug).first()

def get_all_os(db: Session, skip: int = 0, limit: int = 100) -> List[OSDistribution]:
    return db.query(OSDistribution).order_by(OSDistribution.name.asc()).offset(skip).limit(limit).all()

def create_os(db: Session, os_in: OSDistributionCreate) -> OSDistribution:
    db_os = OSDistribution(**os_in.model_dump())
    db.add(db_os)
    db.commit()
    db.refresh(db_os)
    return db_os

def update_os(db: Session, db_os: OSDistribution, os_in: OSDistributionUpdate) -> OSDistribution:
    update_data = os_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_os, field, value)
    db.add(db_os)
    db.commit()
    db.refresh(db_os)
    return db_os

def delete_os(db: Session, os_id: int) -> Optional[OSDistribution]:
    db_os = get_os(db, os_id)
    if db_os:
        db.delete(db_os)
        db.commit()
    return db_os