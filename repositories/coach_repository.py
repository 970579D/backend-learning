from unittest import result

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from models.exam_model import ExamBooking, ExamSession
from models.user_model import User, CoachProfile
from models.skill_model import AssessmentAttempt, Assessment, Skill, Skill, coach_skill
from uuid import UUID
class CoachRepository:

    def find_user(self, db: Session, user: CoachProfile, isPassword: bool) -> User:
        user: User | None = db.scalars(select(CoachProfile).where(
        CoachProfile.username == user["username"],
        CoachProfile.password == user["password"]
    ) if isPassword else
    select(CoachProfile).where(
        CoachProfile.username == user["username"]
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
            update(CoachProfile)
            .where(CoachProfile.username == username)
            .values(image_path=image_path)
        )
        db.commit()
        return result.rowcount > 0
    

    def find_skills(self, db: Session, username: str) -> list[dict]:
        rows = db.execute(
            select(coach_skill.c.skill_name, coach_skill.c.status)
            .where(coach_skill.c.username == username)
            .order_by(coach_skill.c.skill_name)
        ).all()

        return [{"skill_name": r.skill_name, "status": r.status} for r in rows]


    def find_assessment(self, db: Session, username: str):
        return db.execute(
                select(Assessment, Skill.category_name)
                .join(Skill, Skill.skill_name == Assessment.assessment_skill)
                .where(Assessment.username == username)
                .order_by(Assessment.assessment_skill)
               ).all()


    def find_assessment_attempts(self, db: Session, assessment_uuids: list[UUID]):
        return db.execute(
            select(AssessmentAttempt, ExamSession.total_score)
            .outerjoin(ExamBooking, ExamBooking.attempt_id == AssessmentAttempt.id)
            .outerjoin(ExamSession, ExamSession.uuid == ExamBooking.session_uuid)
            .where(AssessmentAttempt.assessment_uuid.in_(assessment_uuids))
            .order_by(AssessmentAttempt.assessment_uuid, AssessmentAttempt.round_attempt)
        ).all()

    def update_name(self, db: Session, username: str, firstname: str, lastname: str) -> bool:
        result = db.execute(
            update(CoachProfile)
            .where(CoachProfile.username == username)
            .values(firstname=firstname, lastname=lastname)
        )
        db.commit()
        return result.rowcount > 0