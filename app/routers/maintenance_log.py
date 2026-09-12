from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List

from app.services.member_gear_client import notify_gear_maintenance_completed
from app.database import get_db
from app import models, schemas
from app.auth import verify_api_key

router = APIRouter(prefix="/maintenance_log", tags=["maintenance_log"])


@router.post("", response_model=schemas.MaintenanceLogOut, dependencies=[Depends(verify_api_key)])
def create_maintenance_log(log: schemas.MaintenanceLogCreate, db: Session = Depends(get_db)):
    db_log = models.MaintenanceLog(**log.model_dump())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


@router.get("", response_model=List[schemas.MaintenanceLogOut])
def list_maintenance_logs(
    target_type: Optional[models.TargetType] = None,
    target_id: Optional[int] = None,
    status: Optional[models.MaintenanceStatus] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.MaintenanceLog)
    if target_type:
        query = query.filter(models.MaintenanceLog.target_type == target_type)
    if target_id is not None:
        query = query.filter(models.MaintenanceLog.target_id == target_id)
    if status:
        query = query.filter(models.MaintenanceLog.status == status)
    return query.all()


@router.get("/{log_id}", response_model=schemas.MaintenanceLogOut)
def get_maintenance_log(log_id: int, db: Session = Depends(get_db)):
    log = db.query(models.MaintenanceLog).filter(models.MaintenanceLog.log_id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Maintenance log not found")
    return log


@router.patch("/{log_id}", response_model=schemas.MaintenanceLogOut, dependencies=[Depends(verify_api_key)])
def update_maintenance_log(log_id: int, log_update: schemas.MaintenanceLogUpdate, db: Session = Depends(get_db)):
    log = db.query(models.MaintenanceLog).filter(models.MaintenanceLog.log_id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Maintenance log not found")

    was_completed = log.status == models.MaintenanceStatus.completed

    for field, value in log_update.model_dump(exclude_unset=True).items():
        setattr(log, field, value)
    db.commit()
    db.refresh(log)

    if (
        not was_completed
        and log.status == models.MaintenanceStatus.completed
        and log.target_type == models.TargetType.member_gear
    ):
        notify_gear_maintenance_completed(log.target_id, log.maintenance_type.value, log.note)

    return log


@router.delete("/{log_id}", dependencies=[Depends(verify_api_key)])
def delete_maintenance_log(log_id: int, db: Session = Depends(get_db)):
    log = db.query(models.MaintenanceLog).filter(models.MaintenanceLog.log_id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Maintenance log not found")
    db.delete(log)
    db.commit()
    return {"message": f"Maintenance log {log_id} deleted"}