from unittest import result

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from models.user_model import User, AdminProfile
from uuid import UUID
class AdminRepository:

    def find_user(self, db: Session, user: AdminProfile, isPassword: bool) -> User:
        user: User | None = db.scalars(select(AdminProfile).where(
        AdminProfile.username == user["username"],
        AdminProfile.password == user["password"]
    ) if isPassword else
    select(AdminProfile).where(
        AdminProfile.username == user["username"]
    )).one_or_none()
        
        return user

    def create(
        self,
        db: Session,
        user: User,
    ) -> bool:
        
        db.add(user)
        db.commit()
        db.refresh(user)

        return True