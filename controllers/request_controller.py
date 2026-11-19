from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.request_model import CoachResponseCreate, LearnerRequestCreate
from services.request_service import RequestService

router = APIRouter(prefix="/request", tags=["Request"])

request_service = RequestService()


@router.post("")
def create_request(req: LearnerRequestCreate, db: Session = Depends(get_db)):
    return request_service.create_request(db, req)

@router.get("/learner/{username}")
def find_learner_requests(username: str, db: Session = Depends(get_db)):
    return request_service.find_learner_requests(db, username)

@router.get("/coach/{username}")
def find_request(username: str, db: Session = Depends(get_db)):
    return request_service.find_request(db, username)

@router.post("/response")
def create_response(req: CoachResponseCreate, db: Session = Depends(get_db)):
    return request_service.create_response(db, req)