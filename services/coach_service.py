from collections import defaultdict
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.coach_detail_model import CoachDetail, CoachRegisterRequest
from models.response_model import Response_Model
from models.skill_model import AssessmentResponse, AttemptData
from models.user_model import CoachProfile, NameRequest, User, UserResponse
from repositories.coach_repository import CoachRepository
from utils.image_storage import delete_avatar, save_avatar
from utils.phone import normalize_phone

MAX_ABOUT = 1000
MAX_COURSE = 2000
MAX_COST = 100000


class CoachService:

    def __init__(self):
        self.repository = CoachRepository()

    def find_user(self, db: Session, username: str) -> Response_Model[UserResponse]:
        response: Response_Model = Response_Model(status="success", message="OK")

        coach: User = self.repository.find_user(db, {"username": username}, isPassword=False)
        if coach is None:
            response.status = "error"
            response.message = "User does not exist"
            return response

        skills = self.repository.find_skills(db, username)

        result: UserResponse = UserResponse(
            username=coach.username,
            firstname=coach.firstname,
            lastname=coach.lastname,
            phone=coach.phone,
            status=coach.status,
            image_path=coach.image_path,
            create_date=coach.create_date,
            update_date=coach.update_date,
            skills=skills,
        )

        response.data = result
        return response

    def create(self, db: Session, req: CoachRegisterRequest) -> Response_Model[UserResponse]:
        response: Response_Model = Response_Model(status="success", message="User created successfully")

        existing_user = self.repository.find_user(db, {"username": req.username}, isPassword=False)
        if existing_user:
            response.status = "error"
            response.message = "User already exists"
            return response

        phone: str | None = normalize_phone(req.phone)
        if phone is None:
            response.status = "error"
            response.message = "Phone number must be 9 to 15 digits"
            return response

        about_coach: str = req.detail.about_coach.strip()
        if not about_coach:
            response.status = "error"
            response.message = "About coach is required"
            return response

        if len(about_coach) > MAX_ABOUT:
            response.status = "error"
            response.message = f"About coach must be {MAX_ABOUT} characters or fewer"
            return response

        course_description: str = req.detail.course_description.strip()
        if not course_description:
            response.status = "error"
            response.message = "Course description is required"
            return response

        if len(course_description) > MAX_COURSE:
            response.status = "error"
            response.message = f"Course description must be {MAX_COURSE} characters or fewer"
            return response

        if req.detail.cost < 0 or req.detail.cost > MAX_COST:
            response.status = "error"
            response.message = f"Cost must be between 0 and {MAX_COST}"
            return response

        coach: CoachProfile = CoachProfile(
            username=req.username,
            password=req.password,
            firstname=req.firstname,
            lastname=req.lastname,
            phone=phone,
        )
        detail: CoachDetail = CoachDetail(
            username=req.username,
            about_coach=about_coach,
            course_description=course_description,
            cost=req.detail.cost,
            place_to_coach=req.detail.place_to_coach,
            coaching_mode=req.detail.coaching_mode,
        )

        try:
            self.repository.create_with_detail(db, coach, detail)
        except IntegrityError:
            db.rollback()
            response.status = "error"
            response.message = "User already exists"
            return response

        created: CoachProfile = self.repository.find_user(db, {"username": req.username}, isPassword=False)

        result: UserResponse = UserResponse(
            username=created.username,
            firstname=created.firstname,
            lastname=created.lastname,
            phone=created.phone,
            status=created.status,
            image_path=created.image_path,
            create_date=created.create_date,
            update_date=created.update_date,
            skills=[],
        )

        response.data = result
        return response

    def update_image(self, db: Session, username: str, file: UploadFile) -> Response_Model[dict]:
        response: Response_Model = Response_Model(status="success", message="Image updated successfully")

        coach: User = self.repository.find_user(db, {"username": username}, isPassword=False)
        if coach is None:
            response.status = "error"
            response.message = "User does not exist"
            return response

        try:
            name = save_avatar(file)
        except ValueError as e:
            response.status = "error"
            response.message = str(e)
            return response

        previous = coach.image_path
        if not self.repository.update_image(db, username, name):
            delete_avatar(name)
            response.status = "error"
            response.message = "Could not save image"
            return response

        delete_avatar(previous)
        response.data = {"username": username, "image_path": name}
        return response

    def delete_image(self, db: Session, username: str) -> Response_Model[dict]:
        response: Response_Model = Response_Model(status="success", message="Image removed")

        coach: User = self.repository.find_user(db, {"username": username}, isPassword=False)
        if coach is None:
            response.status = "error"
            response.message = "User does not exist"
            return response

        previous = coach.image_path
        self.repository.update_image(db, username, None)
        delete_avatar(previous)

        response.data = {"username": username, "image_path": None}
        return response

    def update_name(self, db: Session, username: str, req: NameRequest) -> Response_Model[dict]:
        response: Response_Model = Response_Model(status="success", message="Name updated successfully")

        coach: User = self.repository.find_user(db, {"username": username}, isPassword=False)
        if coach is None:
            response.status = "error"
            response.message = "User does not exist"
            return response

        firstname: str = req.firstname.strip()
        lastname: str = req.lastname.strip()
        if not firstname or not lastname:
            response.status = "error"
            response.message = "First name and last name are required"
            return response

        if len(firstname) > 50 or len(lastname) > 50:
            response.status = "error"
            response.message = "Names must be 50 characters or fewer"
            return response

        if not self.repository.update_name(db, username, firstname, lastname):
            response.status = "error"
            response.message = "Could not update name"
            return response

        response.data = {"username": username, "firstname": firstname, "lastname": lastname}
        return response

    def find_coach_assessment(self, db: Session, username: str) -> Response_Model[list[AssessmentResponse]]:
        response: Response_Model = Response_Model(status="success", message="OK")

        coach: User = self.repository.find_user(db, {"username": username}, isPassword=False)
        if coach is None:
            response.status = "error"
            response.message = "User does not exist"
            return response

        assessments = self.repository.find_assessment(db, username)
        if not assessments:
            response.data = []
            return response

        skill_by_uuid: dict[UUID, str] = {a.uuid: a.assessment_skill for a, _ in assessments}
        attempts = self.repository.find_assessment_attempts(db, list(skill_by_uuid))

        attempt_data: dict[UUID, list[AttemptData]] = defaultdict(list)
        assessment_data: list[AssessmentResponse] = []

        for t, total_score in attempts:
            attempt_data[t.assessment_uuid].append(
                AttemptData(
                    id=t.id,
                    assessment_uuid=t.assessment_uuid,
                    assessment_skill=skill_by_uuid[t.assessment_uuid],
                    round_attempt=t.round_attempt,
                    score=t.score,
                    total_score=total_score or 100,
                    status=t.status,
                    create_date=t.create_date,
                    update_date=t.update_date,
                )
            )

        for a, category in assessments:
            assessment_data.append(
                AssessmentResponse(
                    id=a.id,
                    uuid=a.uuid,
                    assessment_skill=a.assessment_skill,
                    assessment_skill_category=category,
                    status=a.status,
                    total_attempt=a.total_attempt,
                    attemps=attempt_data.get(a.uuid, []),
                )
            )

        response.data = assessment_data
        return response