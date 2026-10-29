from sqlalchemy import select
from sqlalchemy.orm import Session

from models.response_model import Response_Model
from models.user_model import User, Learner

class LearnerRepository:

    def find_user(self, db: Session, user: Learner, isPassword: bool) -> User:
        user: User | None = db.scalars(select(Learner).where(
        Learner.username == user["username"],
        Learner.password == user["password"]
    ) if isPassword else
    select(Learner).where(
        Learner.username == user["username"]
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
    