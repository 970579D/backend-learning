from fastapi import UploadFile
from sqlalchemy.orm import Session

from models.response_model import Response_Model
from models.user_model import User, Learner
from repositories.learner_repository import LearnerRepository
from utils.image_storage import delete_avatar, save_avatar

class LearnerService:

    def __init__(self):
        self.repository = LearnerRepository()

    def find_user(self, db: Session, username: str) -> Response_Model[User]:
         response: Response_Model = Response_Model(status="success", message="User created successfully")
         input_user = dict(username=username)
         result: User = self.repository.find_user(db, input_user, isPassword=False)
         if result == None:
             response.status = "error"
             response.message = "User does not exist"
             return response
         
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

        input_user = Learner(username = user["username"], 
                            password = user["password"], 
                            firstname = user["firstname"],
                            lastname = user["lastname"])

        self.repository.create(db, input_user)
        result = self.repository.find_user(db, user, False)

        response.data = result
        
        return response

    def update_image(self, db: Session, username: str, file: UploadFile) -> Response_Model[dict]:
        response: Response_Model = Response_Model(status="success", message="Image updated successfully")

        learner = self.repository.find_user(db, {"username": username}, isPassword=False)
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

        learner = self.repository.find_user(db, {"username": username}, isPassword=False)
        if learner is None:
            response.status = "error"
            response.message = "User does not exist"
            return response

        previous = learner.image_path
        self.repository.update_image(db, username, None)
        delete_avatar(previous)

        response.data = {"username": username, "image_path": None}
        return response