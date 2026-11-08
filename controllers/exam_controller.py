from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.exam_model import (
    BookingRequest, CheckInRequest, ExamResultRequest, ExamSessionRequest,
    ExamSessionStatusRequest, VerifyRequest,
)
from services.exam_service import ExamService

router = APIRouter(prefix="/exam", tags=["Exam"])

exam_service = ExamService()


@router.post("/session")
def create_session(req: ExamSessionRequest, db: Session = Depends(get_db)):
    return exam_service.create_session(db, req)

@router.get("/session")
def list_sessions(db: Session = Depends(get_db)):
    return exam_service.list_sessions(db)

@router.put("/session/{session_uuid}/status")
def set_session_status(session_uuid: UUID, req: ExamSessionStatusRequest, db: Session = Depends(get_db)):
    return exam_service.set_session_status(db, session_uuid, req)

@router.get("/session/{session_uuid}/booking")
def list_session_bookings(session_uuid: UUID, db: Session = Depends(get_db)):
    return exam_service.list_session_bookings(db, session_uuid)

@router.put("/check-in/{booking_uuid}/verify")
def verify(booking_uuid: UUID, req: VerifyRequest, db: Session = Depends(get_db)):
    return exam_service.verify(db, booking_uuid, req)

@router.get("/assessment")
def list_assessments(db: Session = Depends(get_db)):
    return exam_service.list_assessments(db)

@router.post("/result")
def record_result(req: ExamResultRequest, db: Session = Depends(get_db)):
    return exam_service.record_result(db, req)

@router.get("/open/{username}")
def list_open(username: str, db: Session = Depends(get_db)):
    return exam_service.list_open(db, username)

@router.get("/booking/{username}")
def list_my_bookings(username: str, db: Session = Depends(get_db)):
    return exam_service.list_my_bookings(db, username)

@router.post("/booking")
def book(req: BookingRequest, db: Session = Depends(get_db)):
    return exam_service.book(db, req)

@router.post("/check-in")
def check_in(req: CheckInRequest, db: Session = Depends(get_db)):
    return exam_service.check_in(db, req)