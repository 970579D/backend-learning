from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.request_model import CoachResponse, LearnerRequest
from models.requirement_model import LearnerRequirement
from models.skill_model import Skill, coach_skill
from models.user_model import CoachProfile, Learner


class RequestRepository:

    def find_learner(self, db: Session, username: str) -> Learner | None:
        return db.scalar(select(Learner).where(Learner.username == username))

    def find_coach(self, db: Session, username: str) -> CoachProfile | None:
        return db.scalar(select(CoachProfile).where(CoachProfile.username == username))

    def skill_exists(self, db: Session, skill: str) -> bool:
        return db.scalar(select(Skill.id).where(Skill.skill_name == skill)) is not None

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

    def find_responders(self, db: Session, request_uuids: list[UUID]):
        return db.execute(
            select(CoachResponse, CoachProfile)
            .join(CoachProfile, CoachProfile.username == CoachResponse.username)
            .where(CoachResponse.request_uuid.in_(request_uuids))
            .order_by(CoachResponse.create_date)
        ).all()

    def create_response(self, db: Session, username: str, request_uuid: UUID) -> CoachResponse:
        response = CoachResponse(username=username, request_uuid=request_uuid)
        db.add(response)
        db.commit()
        db.refresh(response)
        return response