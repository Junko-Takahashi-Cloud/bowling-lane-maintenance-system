from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/maintenance_log", tags=["maintenance_log"])


@router.post("", response_model=schemas.MaintenanceLogOut)
def create_maintenance_log(log: schemas.MaintenanceLogCreate, db: Session = Depends(get_db)):
    db_log = models.MaintenanceLog(**log.model_dump())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


@router.get("", response_model=List[schemas.MaintenanceLogOut])
def list_maintenance_logs(
    target_type: Optional[models.TargetType] = None,
    status: Optional[models.MaintenanceStatus] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.MaintenanceLog)
    if target_type:
        query = query.filter(models.MaintenanceLog.target_type == target_type)
    if status:
        query = query.filter(models.MaintenanceLog.status == status)
    return query.all()


@router.get("/{log_id}", response_model=schemas.MaintenanceLogOut)
def get_maintenance_log(log_id: int, db: Session = Depends(get_db)):
    log = db.query(models.MaintenanceLog).filter(models.MaintenanceLog.log_id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Maintenance log not found")
    return log


@router.patch("/{log_id}", response_model=schemas.MaintenanceLogOut)
def update_maintenance_log(log_id: int, log_update: schemas.MaintenanceLogUpdate, db: Session = Depends(get_db)):
    log = db.query(models.MaintenanceLog).filter(models.MaintenanceLog.log_id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Maintenance log not found")
    for field, value in log_update.model_dump(exclude_unset=True).items():
        setattr(log, field, value)
    db.commit()
    db.refresh(log)
    return log


@router.delete("/{log_id}")
def delete_maintenance_log(log_id: int, db: Session = Depends(get_db)):
    log = db.query(models.MaintenanceLog).filter(models.MaintenanceLog.log_id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Maintenance log not found")
    db.delete(log)
    db.commit()
    return {"message": f"Maintenance log {log_id} deleted"}