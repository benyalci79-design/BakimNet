from fastapi import FastAPI, HTTPException, Depends, Query, UploadFile, File
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from uuid import uuid4
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud

from .security import (
    verify_password,
    create_access_token,
    get_current_token,
    require_role
)

from .database import get_db
from .models import Equipment, User, WorkOrder, ProblemReport

from .schemas import (
    EquipmentCreate,
    EquipmentUpdate,
    EquipmentResponse,
    WorkOrderCreate,
    WorkOrderResponse,
    WorkOrderUpdate,
    UserCreate,
    UserResponse,
    UserLogin,
    UserActiveUpdate,
    WorkOrderAssign,
    WorkOrderComplete,
    DashboardResponse,
    ProblemReportCreate,
    ProblemReportUpdate,
    ProblemReportResponse,
    NotificationResponse,
    TechnicianResponse
    , SparePartCreate, SparePartResponse, PartUsageCreate,
    WorkOrderHistoryResponse
)


app = FastAPI(title="BakımNet")
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get(
    "/equipment",
    response_model=list[EquipmentResponse]
)
def get_all_equipment(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return crud.get_all_equipment(db, page, page_size)


@app.post(
    "/equipment",
    response_model=EquipmentResponse
)
def create_equipment(
    new_equipment: EquipmentCreate,
    db: Session = Depends(get_db)
):
    return crud.create_equipment(
        db,
        new_equipment
    )


@app.get(
    "/equipment/{equipment_id}",
    response_model=EquipmentResponse
)
def get_equipment_by_id(
    equipment_id: int,
    db: Session = Depends(get_db)
):
    db_equipment = crud.get_equipment_by_id(
        db,
        equipment_id
    )

    if db_equipment is None:
        raise HTTPException(
            status_code=404,
            detail="Ekipman Bulunamadı"
        )

    return db_equipment


@app.patch(
    "/equipment/{equipment_value}",
    response_model=EquipmentResponse
)
def change_equipment_value(
    equipment_value: int,
    equipment_update: EquipmentUpdate,
    db: Session = Depends(get_db)
):
    db_equipment = crud.update_equipment_location(
        db,
        equipment_value,
        equipment_update.location
    )

    if db_equipment is None:
        raise HTTPException(
            status_code=404,
            detail="Ekipman Bulunamadı"
        )

    return db_equipment


@app.delete("/equipment/{equipment_delete}")
def delete_equipment(
    equipment_delete: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_role("Yönetici")
    )
):
    deleted = crud.delete_equipment(
        db,
        equipment_delete
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Ekipman Bulunamadı"
        )

    return {
        "detail": "Ekipman başarıyla silindi"
    }


@app.post(
    "/work-orders",
    response_model=WorkOrderResponse
)
def create_work_order(
    new_work_order: WorkOrderCreate,
    db: Session = Depends(get_db)
):
    db_equipment = db.get(
        Equipment,
        new_work_order.equipment_id
    )

    if db_equipment is None:
        raise HTTPException(
            status_code=404,
            detail="Ekipman Bulunamadı"
        )

    return crud.create_work_order(
        db,
        new_work_order
    )


@app.get(
    "/work-orders",
    response_model=list[WorkOrderResponse]
)
def get_all_work_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return crud.get_all_work_orders(db, page, page_size)


@app.get(
    "/work-orders/{work_order_id}",
    response_model=WorkOrderResponse
)
def get_work_order_by_id(
    work_order_id: int,
    db: Session = Depends(get_db)
):
    db_work_order = crud.get_work_order_by_id(
        db,
        work_order_id
    )

    if db_work_order is None:
        raise HTTPException(
            status_code=404,
            detail="İş emri bulunamadı"
        )

    return db_work_order


@app.patch(
    "/work-orders/{work_order_id}",
    response_model=WorkOrderResponse
)
def update_work_order(
    work_order_id: int,
    work_order_update: WorkOrderUpdate,
    db: Session = Depends(get_db),
    token_data: dict = Depends(get_current_token)
):
    if work_order_update.status is not None:
        raise HTTPException(
            status_code=409,
            detail="Durum değişiklikleri başlatma ve tamamlama endpointleriyle yapılmalıdır"
        )
    db_work_order = crud.update_work_order(
        db,
        work_order_id,
        work_order_update
    )

    if db_work_order is None:
        raise HTTPException(
            status_code=404,
            detail="İş emri bulunamadı"
        )

    return db_work_order


@app.delete("/work-orders/{work_order_id}")
def delete_work_order(
    work_order_id: int,
    db: Session = Depends(get_db)
):
    deleted = crud.delete_work_order(
        db,
        work_order_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="İş emri bulunamadı"
        )

    return {
        "detail": "İş emri başarıyla silindi"
    }


@app.post(
    "/users",
    response_model=UserResponse
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    return crud.create_user(
        db,
        user_data
    )


@app.patch("/users/{user_id}/active", response_model=UserResponse)
def update_user_active(
    user_id: int,
    data: UserActiveUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("Yönetici")),
):
    user = crud.update_user_active(db, user_id, data.is_active)
    if user is None:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    return user


@app.post("/login")
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    db_user = crud.get_user_by_username(
        db,
        user_data.username
    )

    if db_user is None or not db_user.is_active or not verify_password(
        user_data.password,
        db_user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Kullanıcı adı veya parola hatalı"
        )

    access_token = create_access_token(
        username=db_user.username,
        role=db_user.role
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.get("/spare-parts", response_model=list[SparePartResponse])
def get_spare_parts(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("Yönetici")),
):
    return crud.get_all_spare_parts(db)


@app.get("/notifications", response_model=list[NotificationResponse])
def get_notifications(
    db: Session = Depends(get_db),
    token_data: dict = Depends(get_current_token),
):
    user = crud.get_user_by_username(db, token_data.get("sub"))
    if user is None:
        raise HTTPException(status_code=401, detail="Kullanıcı bulunamadı")
    return crud.get_notifications(db, user.id)


@app.post("/spare-parts", response_model=SparePartResponse)
def create_spare_part(
    data: SparePartCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("Yönetici")),
):
    if data.stock_quantity < 0 or data.critical_level < 0:
        raise HTTPException(status_code=422, detail="Stok değerleri negatif olamaz")
    return crud.create_spare_part(db, data)


@app.post("/work-orders/{work_order_id}/parts")
def add_part_to_work_order(
    work_order_id: int,
    data: PartUsageCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("Teknisyen")),
):
    technician = crud.get_user_by_username(db, current_user["sub"])
    order = crud.get_work_order_by_id(db, work_order_id)
    if order is None or order.technician_id != technician.id:
        raise HTTPException(status_code=403, detail="Bu iş emrine erişim yetkiniz yok")
    usage, error = crud.add_part_usage(db, work_order_id, data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return usage


@app.get("/work-orders/{work_order_id}/history", response_model=list[WorkOrderHistoryResponse])
def get_work_order_history(
    work_order_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_token),
):
    if crud.get_work_order_by_id(db, work_order_id) is None:
        raise HTTPException(status_code=404, detail="İş emri bulunamadı")
    return crud.get_work_order_history(db, work_order_id)


@app.get("/me")
def get_current_user(
    token_data: dict = Depends(get_current_token)
):
    return token_data


@app.patch(
    "/work-orders/{work_order_id}/assign",
    response_model=WorkOrderResponse
)
def assign_work_order_to_technician(
    work_order_id: int,
    assignment: WorkOrderAssign,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_role("Yönetici")
    )
):
    technician = db.get(
        User,
        assignment.technician_id
    )

    if technician is None:
        raise HTTPException(
            status_code=404,
            detail="Teknisyen bulunamadı"
        )

    if technician.role != "Teknisyen":
        raise HTTPException(
            status_code=400,
            detail="Seçilen kullanıcı teknisyen değil"
        )

    active_work_order = db.query(WorkOrder).filter(
        WorkOrder.technician_id == technician.id,
        WorkOrder.status.in_([
            "Bekliyor",
            "Devam Ediyor"
        ]),
        WorkOrder.id != work_order_id
    ).first()

    if active_work_order is not None:
        raise HTTPException(
            status_code=409,
            detail="Bu teknisyen şu anda meşgul"
        )

    manager = crud.get_user_by_username(db, current_user["sub"])
    db_work_order = crud.assign_work_order(
        db,
        work_order_id,
        assignment.technician_id,
        manager.id if manager else None
    )

    if db_work_order is None:
        raise HTTPException(
            status_code=404,
            detail="İş emri bulunamadı"
        )

    return db_work_order


@app.get(
    "/technicians",
    response_model=list[TechnicianResponse]
)
def get_all_technicians(
    db: Session = Depends(get_db),
    token_data: dict = Depends(get_current_token)
):
    if token_data.get("role") != "Yönetici":
        raise HTTPException(
            status_code=403,
            detail="Bu listeyi sadece yöneticiler görebilir"
        )

    return crud.get_all_technicians(db)


@app.patch(
    "/work-orders/{work_order_id}/start",
    response_model=WorkOrderResponse
)
def start_work_order(
    work_order_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_role("Teknisyen")
    )
):
    technician = crud.get_user_by_username(
        db,
        current_user["sub"]
    )

    if technician is None:
        raise HTTPException(
            status_code=404,
            detail="Teknisyen bulunamadı"
        )

    db_work_order = crud.start_work_order(
        db,
        work_order_id,
        technician.id
    )

    if db_work_order is None:
        raise HTTPException(
            status_code=403,
            detail="Bu iş emri size atanmamış veya başlatılamaz"
        )

    return db_work_order


@app.patch(
    "/work-orders/{work_order_id}/complete",
    response_model=WorkOrderResponse
)
def complete_work_order(
    work_order_id: int,
    completion: WorkOrderComplete,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_role("Teknisyen")
    )
):
    technician = crud.get_user_by_username(
        db,
        current_user["sub"]
    )

    if technician is None:
        raise HTTPException(
            status_code=404,
            detail="Teknisyen bulunamadı"
        )

    db_work_order = crud.complete_work_order(
        db,
        work_order_id,
        technician.id,
        completion.work_done
    )

    if db_work_order is None:
        raise HTTPException(
            status_code=403,
            detail="Bu iş emri size atanmamış veya tamamlanamaz"
        )

    return db_work_order


@app.get(
    "/my-work-orders",
    response_model=list[WorkOrderResponse]
)
def get_my_work_orders(
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_role("Teknisyen")
    )
):
    technician = crud.get_user_by_username(
        db,
        current_user["sub"]
    )

    if technician is None:
        raise HTTPException(
            status_code=404,
            detail="Teknisyen bulunamadı"
        )

    return crud.get_work_orders_for_technician(
        db,
        technician.id
    )


@app.get(
    "/admin/dashboard",
    response_model=DashboardResponse
)
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_role("Yönetici")
    )
):
    return crud.get_dashboard_data(db)


@app.post(
    "/problem-reports",
    response_model=ProblemReportResponse
)
def create_problem_report(
    problem_report: ProblemReportCreate,
    db: Session = Depends(get_db),
    token_data: dict = Depends(get_current_token)
):
    if token_data.get("role") not in [
        "Personel",
        "Yönetici"
    ]:
        raise HTTPException(
            status_code=403,
            detail="Sorun bildirimi oluşturma yetkiniz yok"
        )

    current_user = db.query(User).filter(
        User.username == token_data.get("sub")
    ).first()

    if current_user is None:
        raise HTTPException(
            status_code=401,
            detail="Kullanıcı bulunamadı"
        )

    return crud.create_problem_report(
        db,
        problem_report,
        current_user.id
    )


@app.get(
    "/problem-reports",
    response_model=list[ProblemReportResponse]
)
def get_all_problem_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    token_data: dict = Depends(get_current_token)
):
    if token_data.get("role") != "Yönetici":
        raise HTTPException(
            status_code=403,
            detail="Bu listeyi sadece yöneticiler görebilir"
        )

    return crud.get_all_problem_reports(db, page, page_size)


@app.patch("/problem-reports/{problem_report_id}", response_model=ProblemReportResponse)
def update_problem_report(
    problem_report_id: int,
    data: ProblemReportUpdate,
    db: Session = Depends(get_db),
    token_data: dict = Depends(get_current_token),
):
    if token_data.get("role") != "Personel":
        raise HTTPException(status_code=403, detail="Bu işlem yalnızca personel içindir")
    user = crud.get_user_by_username(db, token_data.get("sub"))
    if user is None:
        raise HTTPException(status_code=401, detail="Kullanıcı bulunamadı")
    result = crud.update_problem_report(db, problem_report_id, data, user.id)
    if result is None:
        raise HTTPException(status_code=404, detail="Sorun bildirimi bulunamadı")
    if result is False:
        raise HTTPException(status_code=409, detail="Bu bildirim artık güncellenemez")
    return result


@app.post("/problem-reports/{problem_report_id}/photo")
async def upload_problem_photo(
    problem_report_id: int,
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    token_data: dict = Depends(get_current_token),
):
    if token_data.get("role") not in ["Personel", "Yönetici"]:
        raise HTTPException(status_code=403, detail="Fotoğraf yükleme yetkiniz yok")
    report = db.get(ProblemReport, problem_report_id)
    user = crud.get_user_by_username(db, token_data.get("sub"))
    if report is None or user is None or (report.reported_by != user.id and token_data.get("role") != "Yönetici"):
        raise HTTPException(status_code=404, detail="Sorun bildirimi bulunamadı")
    allowed = {"image/jpeg", "image/png", "image/webp"}
    if photo.content_type not in allowed:
        raise HTTPException(status_code=415, detail="Sadece JPEG, PNG veya WebP yüklenebilir")
    content = await photo.read(5 * 1024 * 1024 + 1)
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Dosya boyutu 5 MB'dan büyük olamaz")
    suffix = Path(photo.filename or "photo").suffix.lower()
    filename = f"{uuid4().hex}{suffix}"
    (UPLOAD_DIR / filename).write_bytes(content)
    report.photo_url = f"/uploads/{filename}"
    db.commit()
    return {"photo_url": report.photo_url}


@app.post(
    "/problem-reports/{problem_report_id}/convert"
)
def convert_problem_report(
    problem_report_id: int,
    db: Session = Depends(get_db),
    token_data: dict = Depends(get_current_token)
):
    if token_data.get("role") != "Yönetici":
        raise HTTPException(
            status_code=403,
            detail="Bu işlemi sadece yönetici yapabilir"
        )

    result = crud.convert_problem_report(
        db,
        problem_report_id
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Sorun bildirimi bulunamadı"
        )

    problem_report, work_order = result

    if work_order is None:
        raise HTTPException(
            status_code=400,
            detail="Bu bildirim zaten iş emrine dönüştürülmüş"
        )

    return {
        "detail": "Sorun bildirimi iş emrine dönüştürüldü",
        "problem_report_id": problem_report.id,
        "work_order_id": work_order.id
    }
