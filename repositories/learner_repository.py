from sqlalchemy import select, update
from sqlalchemy.orm import Session

from models.requirement_model import LearnerRequirement
from models.user_model import Learner


class LearnerRepository:

    def find_user(self, db: Session, user, isPassword: bool) -> Learner | None:
        username: str = user["username"] if isinstance(user, dict) else user.username
        query = select(Learner).where(Learner.username == username)

        if isPassword:
            password: str = user["password"] if isinstance(user, dict) else user.password
            query = query.where(Learner.password == password)

        return db.scalars(query).one_or_none()

    def create_with_requirement(self, db: Session, learner: Learner, requirement: LearnerRequirement) -> None:
        db.add(learner)
        db.flush()
        db.add(requirement)
        db.commit()

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