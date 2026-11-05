from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.user_model import Image
from services.coach_service import CoachService

router = APIRouter(prefix="/coach", tags=["Coach"])

coach_service = CoachService()

@router.get("/{username}")
def find_user(username: str, db: Session = Depends(get_db)):
    return coach_service.find_user(db, username)

@router.post("/")
def create(user: dict, db: Session = Depends(get_db)):
    return coach_service.create(db, user)

@router.put("/image")
def update_coach_image(req: Image, db: Session = Depends(get_db)):
    return coach_service.update_image(db, req)

@router.get("/assessment/{username}")
def find_coach_assessment(username: str, db: Session = Depends(get_db)):
    return coach_service.find_coach_assessment(db, username)