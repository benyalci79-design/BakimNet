from uuid import uuid4

from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from app.models import (
    Equipment,
    User,
    WorkOrder,
    WorkOrderHistory,
    PartUsage,
    SparePart,
    Notification,
)
from app.security import create_access_token


client = TestClient(app)


def create_token(username: str, role: str):
    return create_access_token(
        username=username,
        role=role
    )


def auth_header(username: str, role: str):
    token = create_token(username, role)

    return {
        "Authorization": f"Bearer {token}"
    }


def cleanup_records(
    work_order_id: int | None = None,
    equipment_id: int | None = None,
    username: str | None = None
):
    db_generator = get_db()
    db = next(db_generator)

    try:
        if work_order_id is not None:
            db.query(WorkOrderHistory).filter(
                WorkOrderHistory.work_order_id == work_order_id
            ).delete(synchronize_session=False)
            db.query(PartUsage).filter(
                PartUsage.work_order_id == work_order_id
            ).delete(synchronize_session=False)
            db.query(WorkOrder).filter(
                WorkOrder.id == work_order_id
            ).delete()

        if equipment_id is not None:
            db.query(Equipment).filter(
                Equipment.id == equipment_id
            ).delete()

        if username is not None:
            user = db.query(User).filter(
                User.username == username
            ).first()
            if user is not None:
                db.query(Notification).filter(
                    Notification.user_id == user.id
                ).delete(synchronize_session=False)
            db.query(User).filter(
                User.username == username
            ).delete()

        db.commit()

    finally:
        db_generator.close()


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_all_equipment():
    response = client.get("/equipment?page=1&page_size=10")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_all_work_orders():
    response = client.get("/work-orders?page=1&page_size=10")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_equipment_not_found():
    response = client.get("/equipment/999999")

    assert response.status_code == 404


def test_get_work_order_not_found():
    response = client.get("/work-orders/999999")

    assert response.status_code == 404


def test_admin_dashboard_requires_authentication():
    response = client.get("/admin/dashboard")

    assert response.status_code == 401


def test_admin_dashboard_requires_manager_role():
    response = client.get(
        "/admin/dashboard",
        headers=auth_header("test-personel", "Personel")
    )

    assert response.status_code == 403


def test_technicians_requires_manager_role():
    response = client.get(
        "/technicians",
        headers=auth_header("test-personel", "Personel")
    )

    assert response.status_code == 403


def test_my_work_orders_requires_technician_role():
    response = client.get(
        "/my-work-orders",
        headers=auth_header("test-personel", "Personel")
    )

    assert response.status_code == 403


def test_start_work_order_requires_technician_role():
    response = client.patch(
        "/work-orders/1/start",
        headers=auth_header("test-personel", "Personel")
    )

    assert response.status_code == 403


def test_complete_work_order_requires_technician_role():
    response = client.patch(
        "/work-orders/1/complete",
        headers=auth_header("test-personel", "Personel"),
        json={
            "work_done": "Test işlemi"
        }
    )

    assert response.status_code == 403


def test_equipment_crud():
    suffix = uuid4().hex[:8]

    equipment_id = None

    try:
        create_response = client.post(
            "/equipment",
            json={
                "code": f"TST-{suffix}",
                "name": "Massey Ferguson 5710 Traktör",
                "location": "Merkez Atölye - 2. Bölüm"
            }
        )

        assert create_response.status_code == 200

        equipment_id = create_response.json()["id"]

        get_response = client.get(
            f"/equipment/{equipment_id}"
        )

        assert get_response.status_code == 200

        update_response = client.patch(
            f"/equipment/{equipment_id}",
            json={
                "location": "Tarım İşletmesi - Açık Saha"
            }
        )

        assert update_response.status_code == 200
        assert update_response.json()["location"] == "Tarım İşletmesi - Açık Saha"

        delete_response = client.delete(
            f"/equipment/{equipment_id}",
            headers=auth_header("test-manager", "Yönetici")
        )

        assert delete_response.status_code == 200

    finally:
        if equipment_id is not None:
            cleanup_records(equipment_id=equipment_id)


def test_user_registration_and_login():
    suffix = uuid4().hex[:8]
    username = f"ayse_kaya_{suffix}"

    try:
        register_response = client.post(
            "/users",
            json={
                "username": username,
                "password": "Test123456",
                "role": "Personel"
            }
        )

        assert register_response.status_code == 200

        login_response = client.post(
            "/login",
            json={
                "username": username,
                "password": "Test123456"
            }
        )

        assert login_response.status_code == 200
        assert "access_token" in login_response.json()

    finally:
        cleanup_records(username=username)


def test_invalid_login():
    response = client.post(
        "/login",
        json={
            "username": "olmayan_kullanici",
            "password": "yanlis_sifre"
        }
    )

    assert response.status_code == 401


def test_invalid_work_order_status():
    equipment_response = client.get("/equipment")
    equipment_list = equipment_response.json()

    assert len(equipment_list) > 0

    response = client.post(
        "/work-orders",
        json={
            "equipment_id": equipment_list[0]["id"],
            "title": "Geçersiz durum testi",
            "description": "Test açıklaması",
            "status": "Geçersiz Durum",
            "priority": "Orta"
        }
    )

    assert response.status_code == 422


def test_admin_dashboard_success():
    response = client.get(
        "/admin/dashboard",
        headers=auth_header("test-manager", "Yönetici")
    )

    assert response.status_code == 200

    data = response.json()

    assert "total_equipment" in data
    assert "total_work_orders" in data
    assert "total_technicians" in data


def test_manager_can_create_and_list_spare_part():
    suffix = uuid4().hex[:8]
    code = f"PRT-{suffix}"
    response = client.post(
        "/spare-parts",
        headers=auth_header("test-manager", "Yönetici"),
        json={"code": code, "name": "Hidrolik Filtre HF-20", "stock_quantity": 5, "critical_level": 1},
    )
    assert response.status_code == 200
    part_id = response.json()["id"]
    try:
        listed = client.get("/spare-parts", headers=auth_header("test-manager", "Yönetici"))
        assert listed.status_code == 200
        assert any(item["id"] == part_id for item in listed.json())
    finally:
        db_generator = get_db()
        db = next(db_generator)
        db.query(SparePart).filter(SparePart.id == part_id).delete()
        db.commit()
        db_generator.close()


def test_technician_workflow():
    suffix = uuid4().hex[:8]
    username = f"mehmet_yildiz_{suffix}"

    equipment_id = None
    work_order_id = None

    try:
        user_response = client.post(
            "/users",
            json={
                "username": username,
                "password": "Test123456",
                "role": "Teknisyen"
            }
        )

        assert user_response.status_code == 200
        technician_id = user_response.json()["id"]

        equipment_response = client.post(
            "/equipment",
            json={
                "code": f"WF-{suffix}",
                "name": "New Holland TD5.110 Traktör",
                "location": "Merkez Atölye - 1. Bölüm"
            }
        )

        assert equipment_response.status_code == 200
        equipment_id = equipment_response.json()["id"]

        work_order_response = client.post(
            "/work-orders",
            json={
                "equipment_id": equipment_id,
                "title": "Motor yağı ve filtre değişimi",
                "description": "Periyodik bakım kapsamında motor yağı ile yağ filtresi değiştirilecek.",
                "status": "Bekliyor",
                "priority": "Orta"
            }
        )

        assert work_order_response.status_code == 200
        work_order_id = work_order_response.json()["id"]

        assign_response = client.patch(
            f"/work-orders/{work_order_id}/assign",
            headers=auth_header("test-manager", "Yönetici"),
            json={
                "technician_id": technician_id
            }
        )

        assert assign_response.status_code == 200

        start_response = client.patch(
            f"/work-orders/{work_order_id}/start",
            headers=auth_header(username, "Teknisyen")
        )

        assert start_response.status_code == 200
        assert start_response.json()["status"] == "Devam Ediyor"

        my_orders_response = client.get(
            "/my-work-orders",
            headers=auth_header(username, "Teknisyen")
        )

        assert my_orders_response.status_code == 200
        assert any(
            order["id"] == work_order_id
            for order in my_orders_response.json()
        )

        complete_response = client.patch(
            f"/work-orders/{work_order_id}/complete",
            headers=auth_header(username, "Teknisyen"),
            json={
                "work_done": "Motor yağı ve filtre değişimi tamamlandı; araç teslim edildi."
            }
        )

        assert complete_response.status_code == 200
        assert complete_response.json()["status"] == "Tamamlandı"
        assert complete_response.json()["work_done"] == (
            "Motor yağı ve filtre değişimi tamamlandı; araç teslim edildi."
        )

    finally:
        cleanup_records(
            work_order_id=work_order_id,
            equipment_id=equipment_id,
            username=username
        )
