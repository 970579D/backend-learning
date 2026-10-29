from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from services.coach_service import CoachService

router = APIRouter(prefix="/coach", tags=["Coach"])

coach_service = CoachService()

@router.get("/{username}")
def find_user(username: str, db: Session = Depends(get_db)):
    return coach_service.find_user(db, username)

@router.post("/")
def create(user: dict, db: Session = Depends(get_db)):
    return coach_service.create(db, user)