from datetime import datetime
from pydantic import BaseModel, ConfigDict, computed_field
from typing import Literal


WorkOrderStatus = Literal[
    "Bekliyor",
    "Devam Ediyor",
    "Tamamlandı"
]
UserRole = Literal[
    "Personel",
    "Teknisyen",
    "Yönetici"
]
class UserCreate(BaseModel):
    username: str
    password: str
    role: UserRole = "Personel"
class UserLogin(BaseModel):
    username: str
    password: str
class UserResponse(BaseModel):
    id: int
    username: str
    role: UserRole
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class UserActiveUpdate(BaseModel):
    is_active: bool

class EquipmentResponse(BaseModel):
    id: int
    code: str
    name: str
    location: str

    model_config = ConfigDict(from_attributes=True)


class EquipmentCreate(BaseModel):
    code: str
    name: str
    location: str


class SparePartCreate(BaseModel):
    code: str
    name: str
    stock_quantity: int = 0
    critical_level: int = 0


class SparePartResponse(SparePartCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class PartUsageCreate(BaseModel):
    spare_part_id: int
    quantity: int


class WorkOrderHistoryResponse(BaseModel):
    id: int
    work_order_id: int
    changed_by: int
    old_status: str | None
    new_status: str
    changed_at: datetime
    model_config = ConfigDict(from_attributes=True)


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    notification_type: str
    message: str
    is_read: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
class WorkOrderCreate(BaseModel):
    equipment_id: int
    title: str
    description: str
    status: WorkOrderStatus = "Bekliyor"
    priority: str = "Orta"
    
class WorkOrderResponse(BaseModel):
    id: int
    equipment_id: int
    technician_id: int | None
    technician_username: str | None = None
    title: str
    description: str
    work_done: str | None
    status: str
    priority: str
    created_at: datetime
    completed_at: datetime | None
    @computed_field
    @property
    def assignment_status(self) -> str:
        if self.technician_id is None:
            return "Atama yapılmadı"

        return "Teknisyen atandı"
    model_config = ConfigDict(from_attributes=True)

class WorkOrderUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: WorkOrderStatus | None = None
    priority: str | None = None
    completed_at: datetime | None = None

class WorkOrderComplete(BaseModel):
    work_done: str
    
class WorkOrderAssign(BaseModel):
    technician_id: int

class EquipmentUpdate(BaseModel):
    location: str

class DashboardResponse(BaseModel):
    total_equipment: int
    total_work_orders: int
    pending_work_orders: int
    in_progress_work_orders: int
    completed_work_orders: int
    total_technicians: int
    busy_technicians: int
    available_technicians: int

ProblemReportStatus = Literal[
    "Yeni",
    "İnceleniyor",
    "İş Emrine Dönüştürüldü",
    "Reddedildi"
]


class ProblemReportCreate(BaseModel):
    equipment_id: int
    title: str
    description: str
    priority: str = "Orta"
    photo_url: str | None = None


class ProblemReportUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: str | None = None


class ProblemReportResponse(BaseModel):
    id: int
    equipment_id: int
    reported_by: int
    title: str
    description: str
    priority: str
    status: ProblemReportStatus
    created_at: datetime
    reported_by: int
    reported_by_username: str
    photo_url: str | None = None

    model_config = ConfigDict(from_attributes=True)

class TechnicianResponse(BaseModel):
    id: int
    username: str
    role: str
    availability: str
