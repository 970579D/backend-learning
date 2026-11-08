from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.exam_model import (
    BookingRequest, BookingResponse, CheckInRequest, ExamAssessmentResponse, ExamResultRequest,
    ExamResultResponse, ExamSession, ExamSessionRequest, ExamSessionResponse,
    ExamSessionStatusRequest, VerifyRequest,
)
from models.response_model import Response_Model
from repositories.exam_repository import ExamRepository

PASS_PERCENT = 50
CHECKIN_OPENS_BEFORE = timedelta(minutes=30)


class ExamService:

    def __init__(self):
        self.repository = ExamRepository()

    def pass_mark(self, total_score: int) -> int:
        return -(-total_score * PASS_PERCENT // 100)

    def to_session_response(
        self, session: ExamSession, booking_count: int = 0, booked: bool = False, passed: bool = False
    ) -> ExamSessionResponse:
        return ExamSessionResponse(
            uuid=session.uuid,
            exam_time=session.exam_time,
            skill=session.skill,
            total_score=session.total_score,
            pass_score=self.pass_mark(session.total_score),
            status=session.status,
            booking_count=booking_count,
            booked=booked,
            passed=passed,
        )

    def to_booking_response(self, booking, session, check_in) -> BookingResponse:
        return BookingResponse(
            uuid=booking.uuid,
            username=booking.username,
            session_uuid=booking.session_uuid,
            skill=session.skill,
            exam_time=session.exam_time,
            session_status=session.status,
            checked_in=check_in is not None,
            verified=bool(check_in and check_in.verify),
            assessed=booking.attempt_id is not None,
        )

    def create_session(self, db: Session, req: ExamSessionRequest) -> Response_Model[ExamSessionResponse]:
        response: Response_Model = Response_Model(status="success", message="Exam session created successfully")

        exam_time: datetime = req.exam_time if req.exam_time.tzinfo else req.exam_time.replace(tzinfo=timezone.utc)
        if exam_time <= datetime.now(timezone.utc):
            response.status = "error"
            response.message = "Exam time must be in the future"
            return response

        if not self.repository.skill_exists(db, req.skill):
            response.status = "error"
            response.message = "Skill does not exist"
            return response

        session: ExamSession = self.repository.create_session(db, exam_time, req.skill, req.total_score)

        response.data = self.to_session_response(session)
        return response

    def list_sessions(self, db: Session) -> Response_Model[list[ExamSessionResponse]]:
        response: Response_Model = Response_Model(status="success", message="OK")

        rows = self.repository.list_sessions(db)
        sessions: list[ExamSessionResponse] = []

        for session, booking_count in rows:
            sessions.append(self.to_session_response(session, booking_count=booking_count))

        response.data = sessions
        return response

    def set_session_status(
        self, db: Session, session_uuid: UUID, req: ExamSessionStatusRequest
    ) -> Response_Model[ExamSessionResponse]:
        response: Response_Model = Response_Model(status="success", message="Status updated successfully")

        session: ExamSession = self.repository.find_session(db, session_uuid)
        if session is None:
            response.status = "error"
            response.message = "Exam session does not exist"
            return response

        session = self.repository.set_session_status(db, session, req.status)

        response.data = self.to_session_response(session)
        return response

    def list_session_bookings(self, db: Session, session_uuid: UUID) -> Response_Model[list[BookingResponse]]:
        response: Response_Model = Response_Model(status="success", message="OK")

        rows = self.repository.list_bookings_by_session(db, session_uuid)
        bookings: list[BookingResponse] = []

        for booking, session, check_in in rows:
            bookings.append(self.to_booking_response(booking, session, check_in))

        response.data = bookings
        return response

    def list_open(self, db: Session, username: str) -> Response_Model[list[ExamSessionResponse]]:
        response: Response_Model = Response_Model(status="success", message="OK")

        rows = self.repository.list_open_sessions(db, username)
        passed_skills: set[str] = self.repository.list_passed_skills(db, username)
        sessions: list[ExamSessionResponse] = []

        for session, booking_uuid in rows:
            sessions.append(
                self.to_session_response(
                    session,
                    booked=booking_uuid is not None,
                    passed=session.skill in passed_skills,
                )
            )

        response.data = sessions
        return response

    def list_my_bookings(self, db: Session, username: str) -> Response_Model[list[BookingResponse]]:
        response: Response_Model = Response_Model(status="success", message="OK")

        rows = self.repository.list_bookings_by_user(db, username)
        bookings: list[BookingResponse] = []

        for booking, session, check_in in rows:
            bookings.append(self.to_booking_response(booking, session, check_in))

        response.data = bookings
        return response

    def book(self, db: Session, req: BookingRequest) -> Response_Model[BookingResponse]:
        response: Response_Model = Response_Model(status="success", message="Booking created successfully")

        coach = self.repository.find_coach(db, req.username)
        if coach is None:
            response.status = "error"
            response.message = "User does not exist"
            return response

        session: ExamSession = self.repository.find_session(db, req.session_uuid)
        if session is None:
            response.status = "error"
            response.message = "Exam session does not exist"
            return response

        if session.status != "open" or session.exam_time <= datetime.now(timezone.utc):
            response.status = "error"
            response.message = "This exam session is not open for booking"
            return response

        assessment = self.repository.find_assessment(db, req.username, session.skill)
        if assessment is not None and assessment.status == "pass":
            response.status = "error"
            response.message = "You have already passed this skill"
            return response

        try:
            booking = self.repository.create_booking(db, req.username, req.session_uuid)
        except IntegrityError:
            db.rollback()
            response.status = "error"
            response.message = "You have already booked this session"
            return response

        response.data = self.to_booking_response(booking, session, None)
        return response

    def check_in(self, db: Session, req: CheckInRequest) -> Response_Model[BookingResponse]:
        response: Response_Model = Response_Model(
            status="success", message="Checked in, wait for the admin to verify you"
        )

        row = self.repository.find_booking_row(db, req.booking_uuid)
        if row is None or row[0].username != req.username:
            response.status = "error"
            response.message = "Booking does not exist"
            return response

        booking, session, existing_check_in = row
        if existing_check_in is not None:
            response.status = "error"
            response.message = "You have already checked in"
            return response

        if session.status == "finished":
            response.status = "error"
            response.message = "This exam session is finished"
            return response

        # if datetime.now(timezone.utc) < session.exam_time - CHECKIN_OPENS_BEFORE:
        #     response.status = "error"
        #     response.message = "Check-in opens 30 minutes before the exam"
        #     return response

        check_in = self.repository.create_check_in(db, booking.uuid)

        response.data = self.to_booking_response(booking, session, check_in)
        return response

    def verify(self, db: Session, booking_uuid: UUID, req: VerifyRequest) -> Response_Model[BookingResponse]:
        response: Response_Model = Response_Model(status="success", message="Verification updated successfully")

        row = self.repository.find_booking_row(db, booking_uuid)
        if row is None:
            response.status = "error"
            response.message = "Booking does not exist"
            return response

        booking, session, check_in = row
        if check_in is None:
            response.status = "error"
            response.message = "This coach has not checked in yet"
            return response

        if booking.attempt_id is not None and not req.verify:
            response.status = "error"
            response.message = "The result is already saved, verification cannot be removed"
            return response

        check_in = self.repository.set_verify(db, check_in, req.verify)

        response.data = self.to_booking_response(booking, session, check_in)
        return response

    def list_assessments(self, db: Session) -> Response_Model[list[ExamAssessmentResponse]]:
        response: Response_Model = Response_Model(status="success", message="OK")

        rows = self.repository.list_attended(db)
        items: list[ExamAssessmentResponse] = []

        for booking, session, attempt in rows:
            items.append(
                ExamAssessmentResponse(
                    booking_uuid=booking.uuid,
                    username=booking.username,
                    skill=session.skill,
                    exam_time=session.exam_time,
                    total_score=session.total_score,
                    pass_score=self.pass_mark(session.total_score),
                    assessed=attempt is not None,
                    round_attempt=attempt.round_attempt if attempt else None,
                    score=attempt.score if attempt else None,
                    result=attempt.status if attempt else None,
                )
            )

        response.data = items
        return response

    def record_result(self, db: Session, req: ExamResultRequest) -> Response_Model[ExamResultResponse]:
        response: Response_Model = Response_Model(status="success", message="Result saved successfully")

        row = self.repository.find_booking_row(db, req.booking_uuid)
        if row is None:
            response.status = "error"
            response.message = "Booking does not exist"
            return response

        booking, session, check_in = row
        if check_in is None or not check_in.verify:
            response.status = "error"
            response.message = "This coach is not verified for this exam"
            return response

        if req.score > session.total_score:
            response.status = "error"
            response.message = f"Score cannot be more than {session.total_score}"
            return response

        status: str = "pass" if req.score >= self.pass_mark(session.total_score) else "fail"
        attempt = self.repository.add_attempt(
            db, booking.uuid, booking.username, session.skill, req.score, status
        )
        if attempt is None:
            response.status = "error"
            response.message = "The result for this booking is already saved"
            return response

        result: ExamResultResponse = ExamResultResponse(
            username=booking.username,
            skill=session.skill,
            round_attempt=attempt.round_attempt,
            score=attempt.score,
            total_score=session.total_score,
            status=attempt.status,
        )

        response.data = result
        return response