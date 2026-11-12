from collections import defaultdict
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.orm import Session

from models.response_model import Response_Model
from models.skill_model import AssessmentResponse, AttemptData
from models.user_model import CoachProfile, NameRequest, User, UserResponse
from repositories.coach_repository import CoachRepository
from utils.image_storage import delete_avatar, save_avatar


class CoachService:

    def __init__(self):
        self.repository = CoachRepository()

    def find_user(self, db: Session, username: str) -> Response_Model[UserResponse]:
        response: Response_Model = Response_Model(status="success", message="User created successfully")
        input_user = dict(username=username)
        coach: User = self.repository.find_user(db, input_user, isPassword=False)
        if coach == None:
            response.status = "error"
            response.message = "User does not exist"
            return response

        skills = self.repository.find_skills(db, username)

        result: UserResponse = UserResponse(
            username=coach.username,
            firstname=coach.firstname,
            lastname=coach.lastname,
            status=coach.status,
            image_path=coach.image_path,
            create_date=coach.create_date,
            update_date=coach.update_date,
            skills=skills,
        )

        response.data = result
        return response

    def create(self, db: Session, user: User) -> Response_Model[User]:
        response: Response_Model = Response_Model(status="success", message="User created successfully")

        existing_user = self.repository.find_user(db, user, isPassword=False)
        if existing_user:
            response.status = "error"
            response.message = "User already exists"
            return response

        result: User = None

        input_user = CoachProfile(username = user["username"],
                                  password = user["password"],
                                  firstname = user["firstname"],
                                  lastname = user["lastname"])

        self.repository.create(db, input_user)
        result = self.repository.find_user(db, user, False)

        response.data = result

        return response

    def update_image(self, db: Session, username: str, file: UploadFile) -> Response_Model[dict]:
        response: Response_Model = Response_Model(status="success", message="Image updated successfully")

        coach = self.repository.find_user(db, {"username": username}, isPassword=False)
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

        coach = self.repository.find_user(db, {"username": username}, isPassword=False)
        if coach is None:
            response.status = "error"
            response.message = "User does not exist"
            return response

        previous = coach.image_path
        self.repository.update_image(db, username, None)
        delete_avatar(previous)

        response.data = {"username": username, "image_path": None}
        return response

    def find_coach_assessment(self, db: Session, username: str) -> Response_Model[list[AssessmentResponse]]:
        response: Response_Model = Response_Model(status="success", message="OK")

        coach = self.repository.find_user(db, {"username": username}, isPassword=False)
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

    def update_name(self, db: Session, username: str, req: NameRequest) -> Response_Model[dict]:
        response: Response_Model = Response_Model(status="success", message="Name updated successfully")

        coach = self.repository.find_user(db, {"username": username}, isPassword=False)
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

        if not self.repository.update_name(db, username, firstname, lastname):
            response.status = "error"
            response.message = "Could not update name"
            return response

        response.data = {"username": username, "firstname": firstname, "lastname": lastname}
        return response