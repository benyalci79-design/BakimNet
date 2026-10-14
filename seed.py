from app.database import SessionLocal
from app.models import Equipment, SparePart, User
from app.crud import create_user
from app.schemas import UserCreate


def get_or_create_user(db, username, password, role):
    user = db.query(User).filter(User.username == username).first()
    if user:
        return user
    return create_user(db, UserCreate(username=username, password=password, role=role))


def seed():
    db = SessionLocal()
    try:
        get_or_create_user(db, "admin", "Admin123!", "Yönetici")
        get_or_create_user(db, "personel", "Personel123!", "Personel")
        get_or_create_user(db, "teknisyen", "Teknisyen123!", "Teknisyen")
        get_or_create_user(db, "MertAlbay", "Teknisyen123!", "Teknisyen")
        get_or_create_user(db, "KemalGungoren", "Teknisyen123!", "Teknisyen")
        get_or_create_user(db, "AdaPinar", "Teknisyen123!", "Teknisyen")
        if not db.query(Equipment).filter(Equipment.code == "TRK-001").first():
            db.add(Equipment(code="TRK-001", name="New Holland TD5.110 Traktör", location="Merkez Atölye - 1. Bölüm"))
        if not db.query(SparePart).filter(SparePart.code == "YAG-001").first():
            db.add(SparePart(code="YAG-001", name="Motor yağı", stock_quantity=20, critical_level=5))
        db.commit()
        print("Seed verileri hazırlandı.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
