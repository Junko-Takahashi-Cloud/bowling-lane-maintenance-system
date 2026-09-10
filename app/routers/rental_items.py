from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/rental_items", tags=["rental_items"])


@router.post("", response_model=schemas.RentalItemOut)
def create_rental_item(item: schemas.RentalItemCreate, db: Session = Depends(get_db)):
    db_item = models.RentalItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("", response_model=List[schemas.RentalItemOut])
def list_rental_items(
    status: Optional[models.ItemStatus] = None,
    item_type: Optional[models.ItemType] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.RentalItem)
    if status:
        query = query.filter(models.RentalItem.status == status)
    if item_type:
        query = query.filter(models.RentalItem.item_type == item_type)
    return query.all()


@router.get("/{item_id}", response_model=schemas.RentalItemOut)
def get_rental_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.RentalItem).filter(models.RentalItem.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Rental item not found")
    return item


@router.patch("/{item_id}", response_model=schemas.RentalItemOut)
def update_rental_item(item_id: int, item_update: schemas.RentalItemUpdate, db: Session = Depends(get_db)):
    item = db.query(models.RentalItem).filter(models.RentalItem.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Rental item not found")
    for field, value in item_update.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", response_model=schemas.RentalItemOut)
def discard_rental_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.RentalItem).filter(models.RentalItem.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Rental item not found")
    item.status = models.ItemStatus.disposed
    db.commit()
    db.refresh(item)
    return item