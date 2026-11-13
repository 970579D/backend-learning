from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.exam_model import ExamBooking, ExamSession
from models.skill_model import Assessment, AssessmentAttempt, Skill, SkillCategory
from models.user_model import CoachProfile


class SkillRepository:

    def list_categories(self, db: Session) -> list[SkillCategory]:
        return list(db.scalars(select(SkillCategory).order_by(SkillCategory.category_name)).all())

    def find_category(self, db: Session, category_name: str) -> SkillCategory | None:
        return db.scalar(select(SkillCategory).where(SkillCategory.category_name == category_name))

    def create_category(self, db: Session, category_name: str) -> SkillCategory:
        category = SkillCategory(category_name=category_name)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    def list_skills(self, db: Session) -> list[Skill]:
        return list(db.scalars(select(Skill).order_by(Skill.category_name, Skill.skill_name)).all())

    def find_skill(self, db: Session, skill_name: str) -> Skill | None:
        return db.scalar(select(Skill).where(Skill.skill_name == skill_name))

    def create_skill(self, db: Session, skill_name: str, category_name: str) -> Skill:
        skill = Skill(skill_name=skill_name, category_name=category_name)
        db.add(skill)
        db.commit()
        db.refresh(skill)
        return skill

    def find_skill_assessments(self, db: Session, skill_name: str):
        return db.execute(
            select(Assessment, CoachProfile)
            .join(CoachProfile, CoachProfile.username == Assessment.username)
            .where(
                Assessment.assessment_skill == skill_name,
                Assessment.status.in_(["pass", "fail"]),
        )
    ).all()

    def find_attempts_with_total(self, db: Session, assessment_uuids: list[UUID]):
        return db.execute(
            select(AssessmentAttempt, ExamSession.total_score)
            .outerjoin(ExamBooking, ExamBooking.attempt_id == AssessmentAttempt.id)
            .outerjoin(ExamSession, ExamSession.uuid == ExamBooking.session_uuid)
            .where(AssessmentAttempt.assessment_uuid.in_(assessment_uuids))
    ).all()