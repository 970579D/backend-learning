from sqlalchemy.orm import Session

from models.response_model import Response_Model
from models.user_model import User, Coach
from repositories.coach_repository import CoachRepository

class CoachService:

    def __init__(self):
        self.repository = CoachRepository()

    def find_user(self, db: Session, username: str) -> Response_Model[User]:
        return self.repository.find_user(db, username)

    def create(self, db: Session, user: User) -> Response_Model[User]:
        response: Response_Model = Response_Model(status="success", message="User created successfully")

        existing_user = self.repository.find_user(db, user, isPassword=False)
        if existing_user:
            response.status = "error"
            response.message = "User already exists"
            return response

        result: User = None

        input_user = Coach(username = user["username"], password = user["password"])

        self.repository.create(db, input_user)
        result = self.repository.find_user(db, user, False)

        response.data = result
        
        return response