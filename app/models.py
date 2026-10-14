from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column,relationship
from zoneinfo import ZoneInfo
from .database import Base

def turkey_now() -> datetime:
    return datetime.now(
        ZoneInfo("Europe/Istanbul")
    ).replace(tzinfo=None)

class Equipment(Base):
    __tablename__ = "equipment"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    code: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    location: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )


class WorkOrder(Base):
    __tablename__ = "work_orders"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    work_done: Mapped[str | None] = mapped_column(
    Text,
    nullable=True
)

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="Bekliyor"
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="Orta"
    )

    created_at: Mapped[datetime] = mapped_column(
    DateTime,
    nullable=False,
    default=datetime.utcnow
)

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    equipment_id: Mapped[int] = mapped_column(
        ForeignKey("equipment.id"),
        nullable=False
    )
    technician_id: Mapped[int | None] = mapped_column(
    ForeignKey("users.id"),
    nullable=True
)
    technician: Mapped["User"] = relationship(
    "User",
    foreign_keys=[technician_id],
    lazy="joined"
)

@property
def technician_username(self) -> str | None:
    if self.technician is None:
        return None

    return self.technician.username
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )
    username: Mapped[str] = mapped_column(
    String(100),
    unique=True,
    nullable=False
)
    password_hash: Mapped[str] = mapped_column(
    String(255),
    nullable=False
)
    role: Mapped[str] = mapped_column(
    String(30),
    nullable=False,
    default="Personel"
)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column


class ProblemReport(Base):
    __tablename__ = "problem_reports"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )
    equipment_id: Mapped[int] = mapped_column(
        ForeignKey("equipment.id"),
        nullable=False
    )

    reported_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    reported_by_user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[reported_by],
        lazy="joined"
    )

    @property
    def reported_by_username(self) -> str:
        return self.reported_by_user.username

    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    priority: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="Orta"
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Yeni"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    photo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)


class SparePart(Base):
    __tablename__ = "spare_parts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    critical_level: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class PartUsage(Base):
    __tablename__ = "part_usages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    work_order_id: Mapped[int] = mapped_column(ForeignKey("work_orders.id"), nullable=False)
    spare_part_id: Mapped[int] = mapped_column(ForeignKey("spare_parts.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class WorkOrderHistory(Base):
    __tablename__ = "work_order_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    work_order_id: Mapped[int] = mapped_column(ForeignKey("work_orders.id"), nullable=False)
    changed_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    old_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    new_status: Mapped[str] = mapped_column(String(30), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    notification_type: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    is_read: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
