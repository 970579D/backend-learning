from collections import defaultdict
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.request_model import (
    CoachResponseCreate, CoachResponseResult, LearnerInfo, LearnerRequest, LearnerRequestCreate,
    LearnerRequestResponse, MatchRequestResponse, RequirementResponse, ResponderResponse,
)
from models.requirement_model import LearnerRequirement
from models.response_model import Response_Model
from repositories.request_repository import RequestRepository

MAX_DESCRIPTION = 500


class RequestService:

    def __init__(self):
        self.repository = RequestRepository()

    def to_learner_request(
        self, request: LearnerRequest, responses: list[ResponderResponse]
    ) -> LearnerRequestResponse:
        return LearnerRequestResponse(
            uuid=request.uuid,
            skill=request.skill,
            description=request.description,
            create_date=request.create_date,
            responses=responses,
        )

    def to_requirement(self, requirement: LearnerRequirement | None) -> RequirementResponse | None:
        if requirement is None:
            return None
        return RequirementResponse(
            level=requirement.level,
            learning_for=requirement.learning_for,
            day=requirement.day,
            time=requirement.time,
            priority=requirement.priority,
            learning_mode=requirement.learning_mode,
            place_to_learn=requirement.place_to_learn,
            province=requirement.province,
        )

    def create_request(self, db: Session, req: LearnerRequestCreate) -> Response_Model[LearnerRequestResponse]:
        response: Response_Model = Response_Model(
            status="success", message="Requested, waiting for coach response"
        )

        learner = self.repository.find_learner(db, req.username)
        if learner is None:
            response.status = "error"
            response.message = "User does not exist"
            return response

        skill: str = req.skill.strip()
        if not self.repository.skill_exists(db, skill):
            response.status = "error"
            response.message = "Skill does not exist"
            return response

        description: str = req.description.strip()
        if len(description) > MAX_DESCRIPTION:
            response.status = "error"
            response.message = f"Description must be {MAX_DESCRIPTION} characters or fewer"
            return response

        try:
            request: LearnerRequest = self.repository.create_request(db, req.username, skill, description)
        except IntegrityError:
            db.rollback()
            response.status = "error"
            response.message = "You have already requested this skill"
            return response

        response.data = self.to_learner_request(request, [])
        return response

    def find_learner_requests(self, db: Session, username: str) -> Response_Model[list[LearnerRequestResponse]]:
        response: Response_Model = Response_Model(status="success", message="OK")

        learner = self.repository.find_learner(db, username)
        if learner is None:
            response.status = "error"
            response.message = "User does not exist"
            return response

        requests: list[LearnerRequest] = self.repository.find_learner_requests(db, username)
        if not requests:
            response.data = []
            return response

        rows = self.repository.find_responders(db, [r.uuid for r in requests])

        by_request: dict[UUID, list[ResponderResponse]] = defaultdict(list)
        for coach_response, coach in rows:
            by_request[coach_response.request_uuid].append(
                ResponderResponse(
                    uuid=coach_response.uuid,
                    username=coach.username,
                    firstname=coach.firstname,
                    lastname=coach.lastname,
                    image_path=coach.image_path,
                    create_date=coach_response.create_date,
                )
            )

        items: list[LearnerRequestResponse] = []
        for request in requests:
            items.append(self.to_learner_request(request, by_request.get(request.uuid, [])))

        response.data = items
        return response

    def find_request(self, db: Session, username: str) -> Response_Model[list[MatchRequestResponse]]:
        response: Response_Model = Response_Model(status="success", message="OK")

        coach = self.repository.find_coach(db, username)
        if coach is None:
            response.status = "error"
            response.message = "User does not exist"
            return response

        rows = self.repository.find_request(db, username)
        if not rows:
            response.data = []
            return response

        responders = self.repository.find_responders(db, [r.uuid for r, _, _ in rows])

        count: dict[UUID, int] = defaultdict(int)
        responded: set[UUID] = set()
        for coach_response, responder in responders:
            count[coach_response.request_uuid] += 1
            if responder.username == username:
                responded.add(coach_response.request_uuid)

        items: list[MatchRequestResponse] = []
        for request, learner, requirement in rows:
            items.append(
                MatchRequestResponse(
                    uuid=request.uuid,
                    skill=request.skill,
                    description=request.description,
                    create_date=request.create_date,
                    learner=LearnerInfo(
                        username=learner.username,
                        firstname=learner.firstname,
                        lastname=learner.lastname,
                        image_path=learner.image_path,
                    ),
                    requirement=self.to_requirement(requirement),
                    response_count=count.get(request.uuid, 0),
                    responded=request.uuid in responded,
                )
            )

        response.data = items
        return response

    def create_response(self, db: Session, req: CoachResponseCreate) -> Response_Model[CoachResponseResult]:
        response: Response_Model = Response_Model(
            status="success", message="Response sent, the learner can see it now"
        )

        coach = self.repository.find_coach(db, req.username)
        if coach is None:
            response.status = "error"
            response.message = "User does not exist"
            return response

        request: LearnerRequest = self.repository.find_request_by_uuid(db, req.request_uuid)
        if request is None:
            response.status = "error"
            response.message = "Request does not exist"
            return response

        if not self.repository.coach_has_skill(db, req.username, request.skill):
            response.status = "error"
            response.message = "You have not passed this skill yet"
            return response

        try:
            created = self.repository.create_response(db, req.username, req.request_uuid)
        except IntegrityError:
            db.rollback()
            response.status = "error"
            response.message = "You have already responded to this request"
            return response

        response.data = CoachResponseResult(
            uuid=created.uuid,
            request_uuid=created.request_uuid,
            skill=request.skill,
            create_date=created.create_date,
        )
        return response