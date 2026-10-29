from sqlalchemy import select
from sqlalchemy.orm import Session

from models.response_model import Response_Model
from models.user_model import User, Coach

class CoachRepository:

    def find_user(self, db: Session, user: Coach, isPassword: bool) -> User:
        user: User | None = db.scalars(select(Coach).where(
        Coach.username == user["username"],
        Coach.password == user["password"]
    ) if isPassword else
    select(Coach).where(
        Coach.username == user["username"]
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
    