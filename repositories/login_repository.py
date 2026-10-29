from ast import stmt

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from models.login_model import CoachLogin, Login, LearnerLogin

class LoginRepository:

    # def find_coach_login(self, db: Session, username: str) -> Login:
    #     # logout is null
    #     result: Login = list(
    #         db.scalars(select(CoachLogin).where(CoachLogin.username == username).where(CoachLogin.logout_date.is_(None)))
    #     )
    #     return result

    def find_coach_login(self, db: Session, username: str) -> Login | None:
        result = db.scalars(
            select(CoachLogin)
                .where(CoachLogin.username == username)
                .where(CoachLogin.logout_date.is_(None))
    ).one_or_none()
        return result
    
    def find_learner_login(self, db: Session, username: str) -> Login | None:
        result = db.scalars(
            select(LearnerLogin)
                .where(LearnerLogin.username == username)
                .where(LearnerLogin.logout_date.is_(None))
    ).one_or_none()
        return result

    def find_coach_login_by_session(self, db: Session, session: str) -> Login:
        result: Login = list(
            db.scalars(select(CoachLogin).where(CoachLogin.session == session).where(CoachLogin.logout_date.is_(None)))
        )
        return result

    def find_learner_login_by_session(self, db: Session, session: str) -> Login:
        result: Login = list(
            db.scalars(select(LearnerLogin).where(LearnerLogin.session == session).where(LearnerLogin.logout_date.is_(None)))
        )
        return result

    def create_login_cocach(
        self,
        db: Session,
        login: Login,
    ) -> Login:
        input_login = CoachLogin(username=login.username, session=login.session)
        db.add(input_login)
        db.commit()
        db.refresh(input_login)
        selected_login = self.find_login(db, login.username)
        return selected_login

    def coach_logout(self, db: Session, session: str) -> bool:
        result = db.execute(
            update(CoachLogin)
            .where(CoachLogin.session == session)
            .where(CoachLogin.logout_date.is_(None))
            .values(logout_date=func.now())
        )
        db.commit()
        return result.rowcount > 0

    def create_login_learner(
        self,
        db: Session,
        login: Login,
    ) -> Login:
        input_login = LearnerLogin(username=login.username, session=login.session)
        db.add(input_login)
        db.commit()
        db.refresh(input_login)
        selected_login = self.find_login(db, login.username)
        return selected_login

    def coach_logout(self, db: Session, session: str) -> bool:
        result = db.execute(
            update(LearnerLogin)
            .where(LearnerLogin.session == session)
            .where(LearnerLogin.logout_date.is_(None))
            .values(logout_date=func.now())
        )
        db.commit()
        return result.rowcount > 0
    
    def learner_logout(self, db: Session, session: str) -> bool:
            result = db.execute(
                update(LearnerLogin)
                .where(LearnerLogin.session == session)
                .where(LearnerLogin.logout_date.is_(None))
                .values(logout_date=func.now())
            )
            db.commit()
            return result.rowcount > 0