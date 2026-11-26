from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.coach_detail_model import CoachDetail
from models.exam_model import ExamBooking, ExamSession
from models.request_model import LearnerRequest
from models.requirement_model import LearnerRequirement
from models.skill_model import Assessment, AssessmentAttempt, Skill, SkillCategory, coach_skill
from models.special_request_model import LearnerSpecialRequest
from models.user_model import CoachProfile, Learner


class RequestRepository:

    def find_learner(self, db: Session, username: str) -> Learner | None:
        return db.scalar(select(Learner).where(Learner.username == username))

    def find_coach(self, db: Session, username: str) -> CoachProfile | None:
        return db.scalar(select(CoachProfile).where(CoachProfile.username == username))

    def skill_exists(self, db: Session, skill: str) -> bool:
        return db.scalar(select(Skill.id).where(Skill.skill_name == skill)) is not None

    def category_exists(self, db: Session, name: str) -> bool:
        return db.scalar(select(SkillCategory.id).where(SkillCategory.category_name == name)) is not None

    def coach_has_skill(self, db: Session, username: str, skill: str) -> bool:
        return (
            db.scalar(
                select(coach_skill.c.id).where(
                    coach_skill.c.username == username,
                    coach_skill.c.skill_name == skill,
                    coach_skill.c.status == "active",
                )
            )
            is not None
        )

    def learner_requested_coach_skill(self, db: Session, learner_username: str, coach_username: str) -> bool:
        return (
            db.scalar(
                select(LearnerRequest.id)
                .join(coach_skill, coach_skill.c.skill_name == LearnerRequest.skill)
                .where(
                    LearnerRequest.username == learner_username,
                    coach_skill.c.username == coach_username,
                    coach_skill.c.status == "active",
                )
                .limit(1)
            )
            is not None
        )

    def find_request_by_uuid(self, db: Session, request_uuid: UUID) -> LearnerRequest | None:
        return db.scalar(select(LearnerRequest).where(LearnerRequest.uuid == request_uuid))

    def create_request(self, db: Session, username: str, skill: str, description: str) -> LearnerRequest:
        request = LearnerRequest(username=username, skill=skill, description=description)
        db.add(request)
        db.commit()
        db.refresh(request)
        return request

    def find_learner_requests(self, db: Session, username: str) -> list[LearnerRequest]:
        return list(
            db.scalars(
                select(LearnerRequest)
                .where(LearnerRequest.username == username)
                .order_by(LearnerRequest.create_date.desc())
            ).all()
        )

    def find_request(self, db: Session, username: str):
        return db.execute(
            select(LearnerRequest, Learner, LearnerRequirement)
            .join(Learner, Learner.username == LearnerRequest.username)
            .outerjoin(LearnerRequirement, LearnerRequirement.username == LearnerRequest.username)
            .where(
                LearnerRequest.skill.in_(
                    select(coach_skill.c.skill_name).where(
                        coach_skill.c.username == username,
                        coach_skill.c.status == "active",
                    )
                )
            )
            .order_by(LearnerRequest.create_date.desc())
        ).all()

    def find_matching_coaches(self, db: Session, skills: list[str]):
        return db.execute(
            select(coach_skill.c.skill_name, CoachProfile, CoachDetail)
            .join(CoachProfile, CoachProfile.username == coach_skill.c.username)
            .outerjoin(CoachDetail, CoachDetail.username == CoachProfile.username)
            .where(coach_skill.c.skill_name.in_(skills), coach_skill.c.status == "active")
        ).all()

    def find_scores(self, db: Session, skills: list[str], usernames: list[str]):
        return db.execute(
            select(
                Assessment.username,
                Assessment.assessment_skill,
                Assessment.total_attempt,
                AssessmentAttempt.score,
                ExamSession.total_score,
            )
            .join(AssessmentAttempt, AssessmentAttempt.assessment_uuid == Assessment.uuid)
            .outerjoin(ExamBooking, ExamBooking.attempt_id == AssessmentAttempt.id)
            .outerjoin(ExamSession, ExamSession.uuid == ExamBooking.session_uuid)
            .where(Assessment.assessment_skill.in_(skills), Assessment.username.in_(usernames))
        ).all()

    def waiting_special_exists(self, db: Session, username: str, skill_name: str) -> bool:
        return (
            db.scalar(
                select(LearnerSpecialRequest.id).where(
                    LearnerSpecialRequest.username == username,
                    LearnerSpecialRequest.status == "waiting",
                    LearnerSpecialRequest.skill_name.ilike(skill_name),
                )
            )
            is not None
        )

    def create_special_request(
        self, db: Session, username: str, skill_name: str, category: str, description: str
    ) -> LearnerSpecialRequest:
        request = LearnerSpecialRequest(
            username=username, skill_name=skill_name, category=category, description=description
        )
        db.add(request)
        db.commit()
        db.refresh(request)
        return request

    def find_special_by_learner(self, db: Session, username: str) -> list[LearnerSpecialRequest]:
        return list(
            db.scalars(
                select(LearnerSpecialRequest)
                .where(LearnerSpecialRequest.username == username)
                .order_by(LearnerSpecialRequest.create_date.desc())
            ).all()
        )

    def find_all_special(self, db: Session):
        return db.execute(
            select(LearnerSpecialRequest, Learner)
            .join(Learner, Learner.username == LearnerSpecialRequest.username)
            .order_by(
                LearnerSpecialRequest.status != "waiting",
                LearnerSpecialRequest.create_date.desc(),
            )
        ).all()