from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from models.exam_model import CheckIn, ExamBooking, ExamSession
from models.skill_model import Assessment, AssessmentAttempt, Skill, coach_skill
from models.user_model import CoachProfile


class ExamRepository:

    def skill_exists(self, db: Session, skill: str) -> bool:
        return db.scalar(select(Skill.id).where(Skill.skill_name == skill)) is not None

    def find_coach(self, db: Session, username: str):
        return db.scalar(select(CoachProfile).where(CoachProfile.username == username))

    def find_session(self, db: Session, session_uuid: UUID):
        return db.scalar(select(ExamSession).where(ExamSession.uuid == session_uuid))

    def find_assessment(self, db: Session, username: str, skill: str):
        return db.scalar(
            select(Assessment).where(
                Assessment.username == username, Assessment.assessment_skill == skill
            )
        )

    def list_passed_skills(self, db: Session, username: str) -> set[str]:
        return set(
            db.scalars(
                select(Assessment.assessment_skill).where(
                    Assessment.username == username, Assessment.status == "pass"
                )
            ).all()
        )

    def create_session(self, db: Session, exam_time, skill: str, total_score: int, pass_percent: int) -> ExamSession:
        session = ExamSession(
            exam_time=exam_time, skill=skill, total_score=total_score, pass_percent=pass_percent
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def set_session_status(self, db: Session, session: ExamSession, status: str) -> ExamSession:
        session.status = status
        db.commit()
        db.refresh(session)
        return session

    def list_sessions(self, db: Session):
        return db.execute(
            select(ExamSession, func.count(ExamBooking.id))
            .outerjoin(ExamBooking, ExamBooking.session_uuid == ExamSession.uuid)
            .group_by(ExamSession.id)
            .order_by(ExamSession.exam_time.desc())
        ).all()

    def list_open_sessions(self, db: Session, username: str):
        return db.execute(
            select(ExamSession, ExamBooking.uuid)
            .outerjoin(
                ExamBooking,
                and_(ExamBooking.session_uuid == ExamSession.uuid, ExamBooking.username == username),
            )
            .where(
                ExamSession.status == "open",
                ExamSession.exam_time > func.now(),
                ExamBooking.uuid.is_(None),
            )
            .order_by(ExamSession.exam_time)
        ).all()

    def _booking_rows(self, db: Session, *conditions):
        return db.execute(
            select(ExamBooking, ExamSession, CheckIn)
            .join(ExamSession, ExamSession.uuid == ExamBooking.session_uuid)
            .outerjoin(CheckIn, CheckIn.exam_booking_uuid == ExamBooking.uuid)
            .where(*conditions)
            .order_by(ExamSession.exam_time.desc(), ExamBooking.username)
        ).all()

    def list_bookings_by_user(self, db: Session, username: str):
        return self._booking_rows(db, ExamBooking.username == username)

    def list_bookings_by_session(self, db: Session, session_uuid: UUID):
        return self._booking_rows(db, ExamBooking.session_uuid == session_uuid)

    def find_booking_row(self, db: Session, booking_uuid: UUID):
        rows = self._booking_rows(db, ExamBooking.uuid == booking_uuid)
        return rows[0] if rows else None

    def list_attended(self, db: Session):
        return db.execute(
            select(ExamBooking, ExamSession, AssessmentAttempt)
            .join(ExamSession, ExamSession.uuid == ExamBooking.session_uuid)
            .join(CheckIn, CheckIn.exam_booking_uuid == ExamBooking.uuid)
            .outerjoin(AssessmentAttempt, AssessmentAttempt.id == ExamBooking.attempt_id)
            .where(CheckIn.verify.is_(True))
            .order_by(ExamSession.exam_time.desc(), ExamBooking.username)
        ).all()

    def create_booking(self, db: Session, username: str, session_uuid: UUID) -> ExamBooking:
        booking = ExamBooking(username=username, session_uuid=session_uuid)
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return booking

    def create_check_in(self, db: Session, booking_uuid: UUID) -> CheckIn:
        check_in = CheckIn(exam_booking_uuid=booking_uuid)
        db.add(check_in)
        db.commit()
        db.refresh(check_in)
        return check_in

    def set_verify(self, db: Session, check_in: CheckIn, verify: bool) -> CheckIn:
        check_in.verify = verify
        db.commit()
        db.refresh(check_in)
        return check_in

    def add_attempt(
        self, db: Session, booking_uuid: UUID, username: str, skill: str, score: int, status: str
    ) -> AssessmentAttempt | None:
        booking = db.scalar(
            select(ExamBooking)
            .where(ExamBooking.uuid == booking_uuid)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        if booking is None or booking.attempt_id is not None:
            db.rollback()
            return None

        assessment = db.scalar(
            select(Assessment)
            .where(Assessment.username == username, Assessment.assessment_skill == skill)
            .with_for_update()
        )
        if assessment is None:
            assessment = Assessment(
                username=username, assessment_skill=skill, total_attempt=0, status="pending"
            )
            db.add(assessment)
            db.flush()

        assessment.total_attempt += 1
        attempt = AssessmentAttempt(
            assessment_uuid=assessment.uuid,
            round_attempt=assessment.total_attempt,
            score=score,
            status=status,
        )
        db.add(attempt)
        db.flush()
        booking.attempt_id = attempt.id

        if status == "pass":
            assessment.status = "pass"
            db.execute(
                pg_insert(coach_skill)
                .values(username=username, skill_name=skill, status="active")
                .on_conflict_do_update(constraint="uq_coach_skill", set_={"status": "active"})
            )
        elif assessment.status != "pass":
            assessment.status = "fail"

        db.commit()
        db.refresh(attempt)
        return attempt