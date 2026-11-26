from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.request_model import LearnerRequestCreate
from models.special_request_model import SpecialRequestCreate
from services.request_service import RequestService

router = APIRouter(prefix="/request", tags=["Request"])

request_service = RequestService()


@router.post("")
def create_request(req: LearnerRequestCreate, db: Session = Depends(get_db)):
    return request_service.create_request(db, req)

@router.get("/learner/{username}")
def find_learner_requests(username: str, db: Session = Depends(get_db)):
    return request_service.find_learner_requests(db, username)

@router.get("/learner/{username}/match")
def find_learner_match(username: str, db: Session = Depends(get_db)):
    return request_service.find_learner_match(db, username)

@router.get("/learner/{username}/phone/{coach_username}")
def find_coach_phone(username: str, coach_username: str, db: Session = Depends(get_db)):
    return request_service.find_coach_phone(db, username, coach_username)

@router.get("/coach/{username}")
def find_request(username: str, db: Session = Depends(get_db)):
    return request_service.find_request(db, username)

@router.get("/coach/{username}/phone/{request_uuid}")
def find_learner_phone(username: str, request_uuid: UUID, db: Session = Depends(get_db)):
    return request_service.find_learner_phone(db, username, request_uuid)

@router.post("/special")
def create_special_request(req: SpecialRequestCreate, db: Session = Depends(get_db)):
    return request_service.create_special_request(db, req)

@router.get("/special")
def find_all_special(db: Session = Depends(get_db)):
    return request_service.find_all_special(db)

@router.get("/special/learner/{username}")
def find_special_by_learner(username: str, db: Session = Depends(get_db)):
    return request_service.find_special_by_learner(db, username)