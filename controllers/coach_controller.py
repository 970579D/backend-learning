from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from database import get_db
from models.user_model import NameRequest
from services.coach_service import CoachService

router = APIRouter(prefix="/coach", tags=["Coach"])

coach_service = CoachService()

@router.get("/{username}")
def find_user(username: str, db: Session = Depends(get_db)):
    return coach_service.find_user(db, username)

@router.post("/")
def create(user: dict, db: Session = Depends(get_db)):
    return coach_service.create(db, user)

@router.put("/image/{username}")
def update_coach_image(username: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    return coach_service.update_image(db, username, file)

@router.delete("/image/{username}")
def delete_coach_image(username: str, db: Session = Depends(get_db)):
    return coach_service.delete_image(db, username)

@router.get("/assessment/{username}")
def find_coach_assessment(username: str, db: Session = Depends(get_db)):
    return coach_service.find_coach_assessment(db, username)

@router.put("/name/{username}")
def update_coach_name(username: str, req: NameRequest, db: Session = Depends(get_db)):
    return coach_service.update_name(db, username, req)