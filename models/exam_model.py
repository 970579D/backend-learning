import uuid as uuid_lib
from datetime import datetime
from typing import Literal
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
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    uuid: Mapped[UUID] = mapped_column(Uuid, unique=True, default=uuid_lib.uuid4)
    exam_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    skill: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("skill.skill_name", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
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
    score: int = Field(ge=0, le=100)


class ExamSessionResponse(BaseModel):
    uuid: UUID
    exam_time: datetime
    skill: str
    status: str
    booking_count: int = 0
    booked: bool = False


class BookingResponse(BaseModel):
    uuid: UUID
    username: str
    session_uuid: UUID
    skill: str
    exam_time: datetime
    session_status: str
    checked_in: bool
    verified: bool


class ExamResultResponse(BaseModel):
    username: str
    skill: str
    round_attempt: int
    score: int
    status: str