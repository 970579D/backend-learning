from sqlalchemy import select

from database import SessionLocal, init_db
from models.user_model import AdminProfile

init_db()
with SessionLocal() as db:
    if db.scalar(select(AdminProfile).where(AdminProfile.username == "admin")) is None:
        db.add(AdminProfile(username="admin", password="admin1234", firstname="AdminProfile", lastname="User"))
        db.commit()