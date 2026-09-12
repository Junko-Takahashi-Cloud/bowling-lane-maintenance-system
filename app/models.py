from sqlalchemy import Column, Integer, String, Date, DECIMAL, Text, ForeignKey, Enum
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()


class ItemType(str, enum.Enum):
    shoe = "shoe"
    ball = "ball"


class ItemStatus(str, enum.Enum):
    in_stock = "在庫中"
    rented = "貸出中"
    inspecting = "点検中"
    repairing = "修理中"
    suspended = "使用停止"
    disposed = "廃棄"


class TargetType(str, enum.Enum):
    lane = "lane"
    shoe = "shoe"
    ball = "ball"
    member_gear = "member_gear"  # 追加: 第四弾の会員所有ギア(gears.id)を指す


class MaintenanceType(str, enum.Enum):
    clean = "clean"
    inspection = "inspection"
    repair = "repair"
    replace = "replace"


class MaintenanceCategory(str, enum.Enum):
    daily = "日常"
    regular = "定期"
    sudden = "突発"
    legal = "法定"


class MaintenanceStatus(str, enum.Enum):
    not_started = "未対応"
    in_progress = "対応中"
    completed = "完了"


class RepairMethod(str, enum.Enum):
    in_house = "店舗対応"
    vendor = "業者対応"


class RentalItem(Base):
    __tablename__ = "rental_items"

    item_id = Column(Integer, primary_key=True, index=True)
    item_type = Column(Enum(ItemType), nullable=False)
    size_or_weight = Column(String, nullable=True)
    status = Column(Enum(ItemStatus), nullable=False, default=ItemStatus.in_stock)
    acquired_at = Column(Date, nullable=True)
    maintenance_frequency_days = Column(Integer, nullable=True)
    next_maintenance_date = Column(Date, nullable=True)


class MaintenanceLog(Base):
    __tablename__ = "maintenance_log"

    log_id = Column(Integer, primary_key=True, index=True)
    target_type = Column(Enum(TargetType), nullable=False)
    target_id = Column(Integer, nullable=False)  # lanes.lane_id または rental_items.item_id
    maintenance_type = Column(Enum(MaintenanceType), nullable=False)
    maintenance_category = Column(Enum(MaintenanceCategory), nullable=False)
    status = Column(Enum(MaintenanceStatus), nullable=False, default=MaintenanceStatus.not_started)
    repair_method = Column(Enum(RepairMethod), nullable=True)
    vendor_name = Column(String, nullable=True)
    performed_by = Column(String, nullable=True)  # staff_id (今は文字列参照、FK制約は将来検討)
    cost = Column(DECIMAL(10, 2), nullable=True)
    action_date = Column(Date, nullable=False)
    note = Column(Text, nullable=True)