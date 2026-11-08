import uuid as uuid_lib
from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, DateTime, ForeignKey, String,
    UniqueConstraint, Uuid, func, text,
)
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class ExamSession(Base):
    __tablename__ = "exam_session"

    __table_args__ = (
        CheckConstraint("status IN ('open', 'closed', 'finished')", name="ck_exam_session_status"),
        CheckConstraint("total_score > 0", name="ck_exam_session_total_score"),
        CheckConstraint("pass_percent BETWEEN 1 AND 100", name="ck_exam_session_pass_percent"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    uuid: Mapped[UUID] = mapped_column(Uuid, unique=True, default=uuid_lib.uuid4)
    exam_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    skill: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("skill.skill_name", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    total_score: Mapped[int] = mapped_column(BigInteger, server_default="100")
    pass_percent: Mapped[int] = mapped_column(BigInteger, server_default="50")
    status: Mapped[str] = mapped_column(String(20), server_default="open")
    create_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    update_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ExamBooking(Base):
    __tablename__ = "exam_booking"
    __table_args__ = (UniqueConstraint("username", "session_uuid", name="uq_exam_booking"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    uuid: Mapped[UUID] = mapped_column(Uuid, unique=True, default=uuid_lib.uuid4)
    username: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("coach_profile.username", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    session_uuid: Mapped[UUID] = mapped_column(
        ForeignKey("exam_session.uuid", ondelete="CASCADE", onupdate="CASCADE"), index=True
    )
    attempt_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("assessment_attempt.id", ondelete="SET NULL", onupdate="CASCADE"),
        unique=True,
        nullable=True,
    )
    create_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    update_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class CheckIn(Base):
    __tablename__ = "check_in"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    uuid: Mapped[UUID] = mapped_column(Uuid, unique=True, default=uuid_lib.uuid4)
    verify: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
    exam_booking_uuid: Mapped[UUID] = mapped_column(
        ForeignKey("exam_booking.uuid", ondelete="CASCADE", onupdate="CASCADE"),
        unique=True,
    )
    create_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    update_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ExamSessionRequest(BaseModel):
    exam_time: datetime
    skill: str
    total_score: int = Field(default=100, gt=0, le=1000)
    pass_percent: int = Field(default=50, ge=1, le=100)


class ExamSessionStatusRequest(BaseModel):
    status: Literal["open", "closed", "finished"]


class BookingRequest(BaseModel):
    username: str
    session_uuid: UUID


class CheckInRequest(BaseModel):
    username: str
    booking_uuid: UUID


class VerifyRequest(BaseModel):
    verify: bool = True


class ExamResultRequest(BaseModel):
    booking_uuid: UUID
    score: int = Field(ge=0)


class ExamSessionResponse(BaseModel):
    uuid: UUID
    exam_time: datetime
    skill: str
    total_score: int
    pass_percent: int
    pass_score: int
    status: str
    booking_count: int = 0
    booked: bool = False
    passed: bool = False


class BookingResponse(BaseModel):
    uuid: UUID
    username: str
    session_uuid: UUID
    skill: str
    exam_time: datetime
    session_status: str
    checked_in: bool
    verified: bool
    assessed: bool = False


class ExamAssessmentResponse(BaseModel):
    booking_uuid: UUID
    username: str
    skill: str
    exam_time: datetime
    total_score: int
    pass_score: int
    assessed: bool
    round_attempt: Optional[int] = None
    score: Optional[int] = None
    result: Optional[str] = None


class ExamResultResponse(BaseModel):
    username: str
    skill: str
    round_attempt: int
    score: int
    total_score: int
    status: str