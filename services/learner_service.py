from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.requirement_model import LearnerRegisterRequest, LearnerRequirement
from models.response_model import Response_Model
from models.user_model import Learner, LearnerResponse, NameRequest
from repositories.learner_repository import LearnerRepository
from utils.image_storage import delete_avatar, save_avatar
from utils.phone import normalize_phone


class LearnerService:

    def __init__(self):
        self.repository = LearnerRepository()

    def find_user(self, db: Session, username: str) -> Response_Model[LearnerResponse]:
        response: Response_Model = Response_Model(status="success", message="OK")

        learner: Learner = self.repository.find_user(db, {"username": username}, isPassword=False)
        if learner is None:
            response.status = "error"
            response.message = "User does not exist"
            return response

        result: LearnerResponse = LearnerResponse(
            username=learner.username,
            firstname=learner.firstname,
            lastname=learner.lastname,
            phone=learner.phone,
            image_path=learner.image_path,
            create_date=learner.create_date,
            update_date=learner.update_date,
        )

        response.data = result
        return response

    def create(self, db: Session, req: LearnerRegisterRequest) -> Response_Model[LearnerResponse]:
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

        learner: Learner = Learner(
            username=req.username,
            password=req.password,
            firstname=req.firstname,
            lastname=req.lastname,
            phone=phone,
        )
        requirement: LearnerRequirement = LearnerRequirement(
            username=req.username,
            **req.requirement.model_dump(),
        )

        try:
            self.repository.create_with_requirement(db, learner, requirement)
        except IntegrityError:
            db.rollback()
            response.status = "error"
            response.message = "User already exists"
            return response

        created: Learner = self.repository.find_user(db, {"username": req.username}, isPassword=False)

        result: LearnerResponse = LearnerResponse(
            username=created.username,
            firstname=created.firstname,
            lastname=created.lastname,
            phone=created.phone,
            image_path=created.image_path,
            create_date=created.create_date,
            update_date=created.update_date,
        )

        response.data = result
        return response

    def update_image(self, db: Session, username: str, file: UploadFile) -> Response_Model[dict]:
        response: Response_Model = Response_Model(status="success", message="Image updated successfully")

        learner: Learner = self.repository.find_user(db, {"username": username}, isPassword=False)
        if learner is None:
            response.status = "error"
            response.message = "User does not exist"
            return response

        try:
            name = save_avatar(file)
        except ValueError as e:
            response.status = "error"
            response.message = str(e)
            return response

        previous = learner.image_path
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

        learner: Learner = self.repository.find_user(db, {"username": username}, isPassword=False)
        if learner is None:
            response.status = "error"
            response.message = "User does not exist"
            return response

        previous = learner.image_path
        self.repository.update_image(db, username, None)
        delete_avatar(previous)

        response.data = {"username": username, "image_path": None}
        return response

    def update_name(self, db: Session, username: str, req: NameRequest) -> Response_Model[dict]:
        response: Response_Model = Response_Model(status="success", message="Name updated successfully")

        learner: Learner = self.repository.find_user(db, {"username": username}, isPassword=False)
        if learner is None:
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