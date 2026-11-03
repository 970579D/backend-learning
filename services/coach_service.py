from urllib import response

from sqlalchemy.orm import Session

from models.response_model import Response_Model
from models.user_model import ImageRequest, User, CoachProfile
from repositories.coach_repository import CoachRepository

class CoachService:

    def __init__(self):
        self.repository = CoachRepository()

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
        return self.repository.find_user(db, input_user, isPassword=False)

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

    def update_image(self, db: Session, req: ImageRequest) -> Response_Model[dict]:
        response = Response_Model(status="success", message="Image updated successfully")

        if not self.repository.update_image(db, req.username, req.image_path):
            response.status = "error"
            response.message = "User does not exist"
            return response

        response.data = {"username": req.username, "image_path": req.image_path}
        return response