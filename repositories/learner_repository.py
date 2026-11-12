from sqlalchemy import select, update
from sqlalchemy.orm import Session

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

    def update_image(self, db: Session, username: str, image_path: str | None) -> bool:
        result = db.execute(
            update(Learner)
            .where(Learner.username == username)
            .values(image_path=image_path)
        )
        db.commit()
        return result.rowcount > 0

    def update_name(self, db: Session, username: str, firstname: str, lastname: str) -> bool:
        result = db.execute(
            update(Learner)
            .where(Learner.username == username)
            .values(firstname=firstname, lastname=lastname)
        )
        db.commit()
        return result.rowcount > 0