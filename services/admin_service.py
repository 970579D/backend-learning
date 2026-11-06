from collections import defaultdict
from urllib import response

from fastapi import UploadFile
from sqlalchemy import UUID
from sqlalchemy.orm import Session

from models.response_model import Response_Model
from models.skill_model import Assessment, AssessmentAttempt, AssessmentResponse, AttemptData
from models.user_model import Image, User, AdminProfile, UserResponse
from repositories.admin_repository import AdminRepository
from utils.image_storage import delete_avatar, save_avatar

class AdminService:

    def __init__(self):
        self.repository = AdminRepository()

    def find_user(self, db: Session, username: str) -> Response_Model[UserResponse]:
        response: Response_Model = Response_Model(status="success", message="User created successfully")
        input_user = dict(username=username)
        admin: User = self.repository.find_user(db, input_user, isPassword=False)
        if admin == None:
            response.status = "error"
            response.message = "User does not exist"
            return response

        skills = self.repository.find_skills(db, username)

        result: UserResponse = UserResponse(
            username=admin.username,
            firstname=admin.firstname,
            lastname=admin.lastname,
            status=admin.status,
            image_path=admin.image_path,
            create_date=admin.create_date,
            update_date=admin.update_date,
            skills=skills,
        )

        response.data = result
        return response