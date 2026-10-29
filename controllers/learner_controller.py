from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from services.learner_service import LearnerService

router = APIRouter(prefix="/learner", tags=["Learner"])

learner_service = LearnerService()

@router.get("/{username}")
def find_user(username: str, db: Session = Depends(get_db)):
    return learner_service.find_user(db, username)

@router.post("/")
def create(user: dict, db: Session = Depends(get_db)):
    return learner_service.create(db, user)