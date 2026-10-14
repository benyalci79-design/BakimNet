from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import func
from sqlalchemy.orm import Session

from .models import Equipment, WorkOrder, User, ProblemReport, SparePart, PartUsage, WorkOrderHistory, Notification
from .schemas import (
    EquipmentCreate,
    WorkOrderCreate,
    WorkOrderUpdate,
    UserCreate,
    ProblemReportCreate
)
from .security import get_password_hash


def create_work_order(
    db: Session,
    new_work_order: WorkOrderCreate
):
    db_work_order = WorkOrder(
        equipment_id=new_work_order.equipment_id,
        title=new_work_order.title,
        description=new_work_order.description,
        status=new_work_order.status,
        priority=new_work_order.priority
    )

    db.add(db_work_order)
    db.commit()
    db.refresh(db_work_order)

    return db_work_order


def get_all_equipment(db: Session, page: int = 1, page_size: int = 100):
    return db.query(Equipment).offset((page - 1) * page_size).limit(page_size).all()


def get_all_work_orders(db: Session, page: int = 1, page_size: int = 100):
    rows = (
        db.query(WorkOrder, User.username)
        .outerjoin(
            User,
            WorkOrder.technician_id == User.id
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return [
        {
            "id": work_order.id,
            "equipment_id": work_order.equipment_id,
            "technician_id": work_order.technician_id,
            "technician_username": username,
            "title": work_order.title,
            "description": work_order.description,
            "status": work_order.status,
            "priority": work_order.priority,
            "created_at": work_order.created_at,
            "completed_at": work_order.completed_at,
            "work_done": work_order.work_done
        }
        for work_order, username in rows
    ]


def get_work_order_by_id(
    db: Session,
    work_order_id: int
):
    return db.get(WorkOrder, work_order_id)


def update_work_order(
    db: Session,
    work_order_id: int,
    work_order_update: WorkOrderUpdate
):
    db_work_order = db.get(WorkOrder, work_order_id)

    if db_work_order is None:
        return None

    update_data = work_order_update.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(db_work_order, field, value)

    db.commit()
    db.refresh(db_work_order)

    return db_work_order


def create_equipment(
    db: Session,
    new_equipment: EquipmentCreate
):
    db_equipment = Equipment(
        code=new_equipment.code,
        name=new_equipment.name,
        location=new_equipment.location
    )

    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)

    return db_equipment


def get_equipment_by_id(
    db: Session,
    equipment_id: int
):
    return db.get(Equipment, equipment_id)


def update_equipment_location(
    db: Session,
    equipment_id: int,
    new_location: str
):
    db_equipment = db.get(Equipment, equipment_id)

    if db_equipment is None:
        return None

    db_equipment.location = new_location

    db.commit()
    db.refresh(db_equipment)

    return db_equipment


def delete_equipment(
    db: Session,
    equipment_id: int
):
    db_equipment = db.get(Equipment, equipment_id)

    if db_equipment is None:
        return False

    db.delete(db_equipment)
    db.commit()

    return True


def delete_work_order(
    db: Session,
    work_order_id: int
):
    db_work_order = db.get(WorkOrder, work_order_id)

    if db_work_order is None:
        return False

    db.query(WorkOrderHistory).filter(
        WorkOrderHistory.work_order_id == work_order_id
    ).delete(synchronize_session=False)
    db.query(PartUsage).filter(
        PartUsage.work_order_id == work_order_id
    ).delete(synchronize_session=False)
    db.delete(db_work_order)
    db.commit()

    return True


def create_user(
    db: Session,
    user_data: UserCreate
):
    hashed_password = get_password_hash(
        user_data.password
    )

    db_user = User(
        username=user_data.username,
        password_hash=hashed_password,
        role=user_data.role
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def get_all_spare_parts(db: Session):
    return db.query(SparePart).order_by(SparePart.name).all()


def create_spare_part(db: Session, data):
    part = SparePart(**data.model_dump())
    db.add(part)
    db.commit()
    db.refresh(part)
    return part


def add_part_usage(db: Session, work_order_id: int, data):
    if data.quantity <= 0:
        return None, "Miktar pozitif olmalıdır"
    order = db.get(WorkOrder, work_order_id)
    part = db.get(SparePart, data.spare_part_id)
    if order is None or part is None:
        return None, "İş emri veya parça bulunamadı"
    if order.status == "Tamamlandı":
        return None, "Tamamlanan iş emrine parça eklenemez"
    if part.stock_quantity < data.quantity:
        return None, "Yetersiz stok"
    part.stock_quantity -= data.quantity
    usage = PartUsage(work_order_id=work_order_id, spare_part_id=part.id, quantity=data.quantity)
    db.add(usage)
    if part.stock_quantity <= part.critical_level:
        managers = db.query(User).filter(User.role == "Yönetici").all()
        for manager in managers:
            create_notification(db, manager.id, "critical_stock", f"{part.name} kritik stok seviyesine düştü")
    db.commit()
    db.refresh(usage)
    return usage, None


def get_work_order_history(db: Session, work_order_id: int):
    return db.query(WorkOrderHistory).filter(
        WorkOrderHistory.work_order_id == work_order_id
    ).order_by(WorkOrderHistory.changed_at).all()


def create_notification(db: Session, user_id: int, notification_type: str, message: str):
    notification = Notification(
        user_id=user_id,
        notification_type=notification_type,
        message=message,
    )
    db.add(notification)
    return notification


def get_notifications(db: Session, user_id: int):
    return db.query(Notification).filter(
        Notification.user_id == user_id
    ).order_by(Notification.created_at.desc()).all()


def record_status_change(db: Session, order, changed_by: int, new_status: str):
    history = WorkOrderHistory(
        work_order_id=order.id,
        changed_by=changed_by,
        old_status=order.status,
        new_status=new_status,
    )
    order.status = new_status
    db.add(history)


def get_user_by_username(
    db: Session,
    username: str
):
    return db.query(User).filter(
        User.username == username
    ).first()


def update_user_active(db: Session, user_id: int, is_active: bool):
    user = db.get(User, user_id)
    if user is None:
        return None
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user


def assign_work_order(
    db: Session,
    work_order_id: int,
    technician_id: int,
    changed_by: int | None = None
):
    db_work_order = db.get(
        WorkOrder,
        work_order_id
    )

    if db_work_order is None:
        return None

    db_work_order.technician_id = technician_id
    create_notification(
        db,
        technician_id,
        "assignment",
        f"İş emri #{work_order_id} size atandı",
    )
    db.add(WorkOrderHistory(
        work_order_id=work_order_id,
        changed_by=changed_by or technician_id,
        old_status=db_work_order.status,
        new_status="Atandı",
    ))

    db.commit()
    db.refresh(db_work_order)

    return db_work_order


def get_all_technicians(db: Session):
    technicians = db.query(User).filter(
        User.role == "Teknisyen"
    ).all()

    result = []

    for technician in technicians:
        active_work_order = db.query(WorkOrder).filter(
            WorkOrder.technician_id == technician.id,
            WorkOrder.status.in_([
                "Bekliyor",
                "Devam Ediyor"
            ])
        ).first()

        if active_work_order is not None:
            availability = "Meşgul"
        else:
            availability = "Müsait"

        result.append({
            "id": technician.id,
            "username": technician.username,
            "role": technician.role,
            "availability": availability
        })

    return result


def start_work_order(
    db: Session,
    work_order_id: int,
    technician_id: int
):
    db_work_order = db.get(
        WorkOrder,
        work_order_id
    )

    if db_work_order is None:
        return None

    if db_work_order.technician_id != technician_id:
        return None

    if db_work_order.status != "Bekliyor":
        return None

    record_status_change(db, db_work_order, technician_id, "Devam Ediyor")

    db.commit()
    db.refresh(db_work_order)

    return db_work_order


def complete_work_order(
    db: Session,
    work_order_id: int,
    technician_id: int,
    work_done: str
):
    db_work_order = db.get(
        WorkOrder,
        work_order_id
    )

    if db_work_order is None:
        return None

    if db_work_order.technician_id != technician_id:
        return None

    if db_work_order.status != "Devam Ediyor":
        return None

    record_status_change(db, db_work_order, technician_id, "Tamamlandı")
    db_work_order.work_done = work_done
    db_work_order.completed_at = datetime.now(
        ZoneInfo("Europe/Istanbul")
    ).replace(tzinfo=None)

    db.commit()
    db.refresh(db_work_order)

    return db_work_order


def get_work_orders_for_technician(
    db: Session,
    technician_id: int
):
    return db.query(WorkOrder).filter(
        WorkOrder.technician_id == technician_id
    ).all()


def get_dashboard_data(db: Session):
    total_equipment = db.query(
        func.count(Equipment.id)
    ).scalar() or 0

    total_work_orders = db.query(
        func.count(WorkOrder.id)
    ).scalar() or 0

    pending_work_orders = db.query(
        func.count(WorkOrder.id)
    ).filter(
        WorkOrder.status == "Bekliyor"
    ).scalar() or 0

    in_progress_work_orders = db.query(
        func.count(WorkOrder.id)
    ).filter(
        WorkOrder.status == "Devam Ediyor"
    ).scalar() or 0

    completed_work_orders = db.query(
        func.count(WorkOrder.id)
    ).filter(
        WorkOrder.status == "Tamamlandı"
    ).scalar() or 0

    total_technicians = db.query(
        func.count(User.id)
    ).filter(
        User.role == "Teknisyen"
    ).scalar() or 0

    busy_technicians = db.query(
        func.count(
            func.distinct(WorkOrder.technician_id)
        )
    ).filter(
        WorkOrder.technician_id.isnot(None),
        WorkOrder.status.in_([
            "Bekliyor",
            "Devam Ediyor"
        ])
    ).scalar() or 0

    return {
        "total_equipment": total_equipment,
        "total_work_orders": total_work_orders,
        "pending_work_orders": pending_work_orders,
        "in_progress_work_orders": in_progress_work_orders,
        "completed_work_orders": completed_work_orders,
        "total_technicians": total_technicians,
        "busy_technicians": busy_technicians,
        "available_technicians": max(
            total_technicians - busy_technicians,
            0
        )
    }


def create_problem_report(
    db: Session,
    problem_report: ProblemReportCreate,
    user_id: int
):
    db_problem_report = ProblemReport(
        equipment_id=problem_report.equipment_id,
        reported_by=user_id,
        title=problem_report.title,
        description=problem_report.description,
        priority=problem_report.priority
    )

    db.add(db_problem_report)
    db.commit()
    db.refresh(db_problem_report)

    return db_problem_report


def get_all_problem_reports(db: Session, page: int = 1, page_size: int = 100):
    return db.query(ProblemReport).offset((page - 1) * page_size).limit(page_size).all()


def update_problem_report(db: Session, report_id: int, data, user_id: int):
    report = db.get(ProblemReport, report_id)
    if report is None or report.reported_by != user_id:
        return None
    if report.status != "Yeni":
        return False
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(report, field, value)
    db.commit()
    db.refresh(report)
    return report


def convert_problem_report(
    db: Session,
    problem_report_id: int
):
    problem_report = db.get(
        ProblemReport,
        problem_report_id
    )

    if problem_report is None:
        return None

    if problem_report.status == "İş Emrine Dönüştürüldü":
        return problem_report, None

    work_order = WorkOrder(
        equipment_id=problem_report.equipment_id,
        title=problem_report.title,
        description=problem_report.description,
        priority=problem_report.priority,
        status="Bekliyor"
    )

    db.add(work_order)

    problem_report.status = "İş Emrine Dönüştürüldü"

    db.commit()
    db.refresh(problem_report)
    db.refresh(work_order)

    return problem_report, work_order
