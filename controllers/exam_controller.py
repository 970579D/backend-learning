from fastapi import APIRouter, Depends, File, UploadFile
from uuid import UUID
from sqlalchemy.orm import Session

from database import get_db
from models.exam_model import ExamSessionRequest, ExamSessionStatusRequest, ExamResultRequest, VerifyRequest
from models.user_model import Image
from services.exam_service import ExamService

router = APIRouter(prefix="/exam", tags=["Exam"])

exam_service = ExamService()

@router.get("/skill")
def skills(db: Session = Depends(get_db)):
    return exam_service.skills(db)

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

@router.post("/result")
def record_result(req: ExamResultRequest, db: Session = Depends(get_db)):
    return exam_service.record_result(db, req)