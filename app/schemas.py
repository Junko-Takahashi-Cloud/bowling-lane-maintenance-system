from pydantic import BaseModel
from datetime import date
from typing import Optional
from app.models import ItemType, ItemStatus
from app.models import MaintenanceType, MaintenanceCategory, MaintenanceStatus, RepairMethod, TargetType



class RentalItemBase(BaseModel):
    item_type: ItemType
    size_or_weight: Optional[str] = None
    acquired_at: Optional[date] = None
    maintenance_frequency_days: Optional[int] = None
    next_maintenance_date: Optional[date] = None


class RentalItemCreate(RentalItemBase):
    pass


class RentalItemUpdate(BaseModel):
    item_type: Optional[ItemType] = None
    size_or_weight: Optional[str] = None
    status: Optional[ItemStatus] = None
    acquired_at: Optional[date] = None
    maintenance_frequency_days: Optional[int] = None
    next_maintenance_date: Optional[date] = None


class RentalItemOut(RentalItemBase):
    item_id: int
    status: ItemStatus

    class Config:
        from_attributes = True


class MaintenanceLogBase(BaseModel):
    target_type: TargetType
    target_id: int
    maintenance_type: MaintenanceType
    maintenance_category: MaintenanceCategory
    repair_method: Optional[RepairMethod] = None
    vendor_name: Optional[str] = None
    performed_by: Optional[str] = None
    cost: Optional[float] = None
    action_date: date
    note: Optional[str] = None


class MaintenanceLogCreate(MaintenanceLogBase):
    pass


class MaintenanceLogUpdate(BaseModel):
    target_type: Optional[TargetType] = None
    target_id: Optional[int] = None
    maintenance_type: Optional[MaintenanceType] = None
    maintenance_category: Optional[MaintenanceCategory] = None
    status: Optional[MaintenanceStatus] = None
    repair_method: Optional[RepairMethod] = None
    vendor_name: Optional[str] = None
    performed_by: Optional[str] = None
    cost: Optional[float] = None
    action_date: Optional[date] = None
    note: Optional[str] = None


class MaintenanceLogOut(MaintenanceLogBase):
    log_id: int
    status: MaintenanceStatus

    class Config:
        from_attributes = True