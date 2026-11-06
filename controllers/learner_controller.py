from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from database import get_db
from services.learner_service import LearnerService
from models.user_model import Image

router = APIRouter(prefix="/learner", tags=["Learner"])

learner_service = LearnerService()

@router.get("/{username}")
def find_user(username: str, db: Session = Depends(get_db)):
    return learner_service.find_user(db, username)

@router.post("/")
def create(user: dict, db: Session = Depends(get_db)):
    return learner_service.create(db, user)

@router.put("/image/{username}")
def update_coach_image(username: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    return learner_service.update_image(db, username, file)

@router.delete("/image/{username}")
def delete_coach_image(username: str, db: Session = Depends(get_db)):
    return learner_service.delete_image(db, username)