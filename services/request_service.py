from collections import defaultdict
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.request_model import (
    LearnerInfo, LearnerMatchResponse, LearnerRequest, LearnerRequestCreate, LearnerRequestResponse,
    MatchCoachResponse, MatchRequestResponse, PhoneResponse, RequirementResponse,
)
from models.requirement_model import LearnerRequirement
from models.response_model import Response_Model
from models.special_request_model import (
    AdminSpecialRequestResponse, LearnerSpecialRequest, SpecialRequestCreate, SpecialRequestResponse,
)
from repositories.request_repository import RequestRepository
from datetime import date as dt_date, datetime, time as dt_time, timezone
from zoneinfo import ZoneInfo
from models.special_request_model import (
        AdminSpecialRequestResponse, CoachInterest, CoachInterestCreate, CoachSpecialResponse,
        InterestedCoachResponse, LearnerSpecialRequest, SpecialRequestCreate, SpecialRequestResponse,
    )
MAX_DESCRIPTION = 500
MAX_NAME = 100
OTHER_CATEGORY = "Other"
INTEREST_TIMEZONE = ZoneInfo("Asia/Bangkok")
INTEREST_FIRST_MINUTE = 8 * 60
INTEREST_LAST_MINUTE = 21 * 60


class RequestService:

    def __init__(self):
        self.repository = RequestRepository()

    def to_learner_request(self, request: LearnerRequest) -> LearnerRequestResponse:
        return LearnerRequestResponse(
            uuid=request.uuid,
            skill=request.skill,
            description=request.description,
            create_date=request.create_date,
        )

    def to_special_response(self, request: LearnerSpecialRequest) -> SpecialRequestResponse:
        return SpecialRequestResponse(
            uuid=request.uuid,
            skill_name=request.skill_name,
            category=request.category,
            description=request.description,
            status=request.status,
            create_date=request.create_date,
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

    def best_scores(
        self, db: Session, skills: list[str], usernames: list[str]
    ) -> dict[tuple[str, str], tuple[int, int, int]]:
        best: dict[tuple[str, str], tuple[int, int, int]] = {}
        if not usernames:
            return best

        for username, skill, total_attempt, score, total in self.repository.find_scores(db, skills, usernames):
            total_score: int = total or 100
            current = best.get((username, skill))
            if current is None or score * current[1] > current[0] * total_score:
                best[(username, skill)] = (score, total_score, total_attempt)
        return best

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

        response.data = self.to_learner_request(request)
        return response

    def find_learner_requests(self, db: Session, username: str) -> Response_Model[list[LearnerRequestResponse]]:
        response: Response_Model = Response_Model(status="success", message="OK")

        learner = self.repository.find_learner(db, username)
        if learner is None:
            response.status = "error"
            response.message = "User does not exist"
            return response

        items: list[LearnerRequestResponse] = []
        for request in self.repository.find_learner_requests(db, username):
            items.append(self.to_learner_request(request))

        response.data = items
        return response

    def find_learner_match(self, db: Session, username: str) -> Response_Model[list[LearnerMatchResponse]]:
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

        skills: list[str] = list({r.skill for r in requests})
        rows = self.repository.find_matching_coaches(db, skills)
        usernames: list[str] = list({coach.username for _, coach, _ in rows})
        best = self.best_scores(db, skills, usernames)

        by_skill: dict[str, list[MatchCoachResponse]] = defaultdict(list)
        for skill, coach, detail in rows:
            score, total_score, total_attempt = best.get((coach.username, skill), (0, 100, 0))
            by_skill[skill].append(
                MatchCoachResponse(
                    username=coach.username,
                    firstname=coach.firstname,
                    lastname=coach.lastname,
                    image_path=coach.image_path,
                    about_coach=detail.about_coach if detail else None,
                    course_description=detail.course_description if detail else None,
                    cost=detail.cost if detail else None,
                    place_to_coach=detail.place_to_coach if detail else None,
                    coaching_mode=detail.coaching_mode if detail else None,
                    best_score=score,
                    best_total_score=total_score,
                    best_percent=round(score * 100 / total_score),
                    total_attempt=total_attempt,
                )
            )

        for coaches in by_skill.values():
            coaches.sort(key=lambda c: (-c.best_percent, -c.best_score, c.username))

        items: list[LearnerMatchResponse] = []
        for request in requests:
            items.append(
                LearnerMatchResponse(
                    uuid=request.uuid,
                    skill=request.skill,
                    description=request.description,
                    create_date=request.create_date,
                    coaches=by_skill.get(request.skill, []),
                )
            )

        response.data = items
        return response

    def find_request(self, db: Session, username: str) -> Response_Model[list[MatchRequestResponse]]:
        response: Response_Model = Response_Model(status="success", message="OK")

        coach = self.repository.find_coach(db, username)
        if coach is None:
            response.status = "error"
            response.message = "User does not exist"
            return response

        items: list[MatchRequestResponse] = []
        for request, learner, requirement in self.repository.find_request(db, username):
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
                )
            )

        response.data = items
        return response

    def find_learner_phone(self, db: Session, coach_username: str, request_uuid: UUID) -> Response_Model[PhoneResponse]:
        response: Response_Model = Response_Model(status="success", message="OK")

        coach = self.repository.find_coach(db, coach_username)
        if coach is None:
            response.status = "error"
            response.message = "User does not exist"
            return response

        request: LearnerRequest = self.repository.find_request_by_uuid(db, request_uuid)
        if request is None:
            response.status = "error"
            response.message = "Request does not exist"
            return response

        if not self.repository.coach_has_skill(db, coach_username, request.skill):
            response.status = "error"
            response.message = "You have not passed this skill yet"
            return response

        learner = self.repository.find_learner(db, request.username)
        if learner is None:
            response.status = "error"
            response.message = "Learner does not exist"
            return response

        response.data = PhoneResponse(username=learner.username, phone=learner.phone)
        return response

    def find_coach_phone(self, db: Session, learner_username: str, coach_username: str) -> Response_Model[PhoneResponse]:
        response: Response_Model = Response_Model(status="success", message="OK")

        learner = self.repository.find_learner(db, learner_username)
        if learner is None:
            response.status = "error"
            response.message = "User does not exist"
            return response

        coach = self.repository.find_coach(db, coach_username)
        if coach is None:
            response.status = "error"
            response.message = "Coach does not exist"
            return response

        if not self.repository.learner_requested_coach_skill(db, learner_username, coach_username):
            response.status = "error"
            response.message = "This coach does not match your requests"
            return response

        response.data = PhoneResponse(username=coach.username, phone=coach.phone)
        return response

    def create_special_request(self, db: Session, req: SpecialRequestCreate) -> Response_Model[SpecialRequestResponse]:
        response: Response_Model = Response_Model(status="success", message="Requested, waiting for admin")

        learner = self.repository.find_learner(db, req.username)
        if learner is None:
            response.status = "error"
            response.message = "User does not exist"
            return response

        skill_name: str = req.skill_name.strip()
        if not skill_name:
            response.status = "error"
            response.message = "Skill name is required"
            return response

        if len(skill_name) > MAX_NAME:
            response.status = "error"
            response.message = f"Skill name must be {MAX_NAME} characters or fewer"
            return response

        category: str = req.category.strip()
        if category != OTHER_CATEGORY and not self.repository.category_exists(db, category):
            response.status = "error"
            response.message = "Category does not exist"
            return response

        description: str = req.description.strip()
        if len(description) > MAX_DESCRIPTION:
            response.status = "error"
            response.message = f"Description must be {MAX_DESCRIPTION} characters or fewer"
            return response

        if self.repository.waiting_special_exists(db, req.username, skill_name):
            response.status = "error"
            response.message = "You already have a waiting request for this skill"
            return response

        request = self.repository.create_special_request(db, req.username, skill_name, category, description)

        response.data = self.to_special_response(request)
        return response

    def find_special_by_learner(self, db: Session, username: str) -> Response_Model[list[SpecialRequestResponse]]:
        response: Response_Model = Response_Model(status="success", message="OK")

        learner = self.repository.find_learner(db, username)
        if learner is None:
            response.status = "error"
            response.message = "User does not exist"
            return response

        items: list[SpecialRequestResponse] = []
        for request in self.repository.find_special_by_learner(db, username):
            items.append(self.to_special_response(request))

        response.data = items
        return response

    def find_all_special(self, db: Session) -> Response_Model[list[AdminSpecialRequestResponse]]:
        response: Response_Model = Response_Model(status="success", message="OK")

        rows = self.repository.find_all_special(db)

        by_request: dict[UUID, list[InterestedCoachResponse]] = defaultdict(list)
        if rows:
            for interest, coach in self.repository.find_interests(db, [r.uuid for r, _ in rows]):
                by_request[interest.learner_request_uuid].append(self.to_interest(interest, coach))

        items: list[AdminSpecialRequestResponse] = []
        for request, learner in rows:
            items.append(
                AdminSpecialRequestResponse(
                    uuid=request.uuid,
                    skill_name=request.skill_name,
                    category=request.category,
                    description=request.description,
                    status=request.status,
                    create_date=request.create_date,
                    username=learner.username,
                    firstname=learner.firstname,
                    lastname=learner.lastname,
                    image_path=learner.image_path,
                    interests=by_request.get(request.uuid, []),
                )
            )

        response.data = items
        return response

    def start_finding(self, db: Session, request_uuid: UUID) -> Response_Model[SpecialRequestResponse]:
        response: Response_Model = Response_Model(status="success", message="Finding a coach")

        request: LearnerSpecialRequest = self.repository.find_special_by_uuid(db, request_uuid)
        if request is None:
            response.status = "error"
            response.message = "Request does not exist"
            return response

        if request.status != "waiting":
            response.status = "error"
            response.message = "Only a waiting request can start finding a coach"
            return response

        request = self.repository.set_special_status(db, request, "finding_coach")

        response.data = self.to_special_response(request)
        return response

    def find_special_for_coach(self, db: Session, username: str) -> Response_Model[list[CoachSpecialResponse]]:
        response: Response_Model = Response_Model(status="success", message="OK")

        coach = self.repository.find_coach(db, username)
        if coach is None:
            response.status = "error"
            response.message = "User does not exist"
            return response

        requests: list[LearnerSpecialRequest] = self.repository.find_finding_special(db)
        if not requests:
            response.data = []
            return response

        count: dict[UUID, int] = defaultdict(int)
        own: dict[UUID, CoachInterest] = {}
        for interest, _ in self.repository.find_interests(db, [r.uuid for r in requests]):
            count[interest.learner_request_uuid] += 1
            if interest.username == username:
                own[interest.learner_request_uuid] = interest

        items: list[CoachSpecialResponse] = []
        for request in requests:
            mine = own.get(request.uuid)
            items.append(
                CoachSpecialResponse(
                    uuid=request.uuid,
                    skill_name=request.skill_name,
                    category=request.category,
                    description=request.description,
                    create_date=request.create_date,
                    interest_count=count.get(request.uuid, 0),
                    interested=mine is not None,
                    interest_date=mine.date.isoformat() if mine else None,
                    interest_time=mine.time.strftime("%H:%M") if mine else None,
                )
            )

        response.data = items
        return response

    def create_interest(self, db: Session, req: CoachInterestCreate) -> Response_Model[InterestedCoachResponse]:
        response: Response_Model = Response_Model(status="success", message="Interest saved")

        coach = self.repository.find_coach(db, req.username)
        if coach is None:
            response.status = "error"
            response.message = "User does not exist"
            return response

        request: LearnerSpecialRequest = self.repository.find_special_by_uuid(db, req.request_uuid)
        if request is None:
            response.status = "error"
            response.message = "Request does not exist"
            return response

        if request.status != "finding_coach":
            response.status = "error"
            response.message = "This request is not looking for a coach"
            return response

        try:
            day: dt_date = dt_date.fromisoformat(req.date)
            slot: dt_time = dt_time.fromisoformat(req.time)
        except ValueError:
            response.status = "error"
            response.message = "Date or time is not valid"
            return response

        minutes: int = slot.hour * 60 + slot.minute
        if (
            slot.second != 0
            or slot.microsecond != 0
            or slot.minute % 15 != 0
            or minutes < INTEREST_FIRST_MINUTE
            or minutes > INTEREST_LAST_MINUTE
        ):
            response.status = "error"
            response.message = "Time must be between 08:00 and 21:00 in 15-minute steps"
            return response

        when: datetime = datetime.combine(day, slot, tzinfo=INTEREST_TIMEZONE)
        if when <= datetime.now(timezone.utc):
            response.status = "error"
            response.message = "Date and time must be in the future"
            return response

        try:
            interest = self.repository.create_interest(db, req.username, req.request_uuid, day, slot)
        except IntegrityError:
            db.rollback()
            response.status = "error"
            response.message = "You have already shown interest in this request"
            return response

        response.data = self.to_interest(interest, coach)
        return response


    def to_interest(self, interest: CoachInterest, coach) -> InterestedCoachResponse:
        return InterestedCoachResponse(
            username=coach.username,
            firstname=coach.firstname,
            lastname=coach.lastname,
            image_path=coach.image_path,
            date=interest.date.isoformat(),
            time=interest.time.strftime("%H:%M"),
        )