import uuid as uuid_lib
from datetime import date as dt_date, datetime, time as dt_time
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import (
    BigInteger, CheckConstraint, Date, DateTime, ForeignKey, String, Text, Time,
    UniqueConstraint, Uuid, func,
)
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class LearnerSpecialRequest(Base):
    __tablename__ = "learner_special_request"
    __table_args__ = (
        CheckConstraint(
            "status IN ('waiting', 'finding_coach', 'approved', 'rejected')",
            name="ck_learner_special_request_status",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    uuid: Mapped[UUID] = mapped_column(Uuid, unique=True, default=uuid_lib.uuid4)
    username: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("learner_profile.username", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    skill_name: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text, server_default="")
    status: Mapped[str] = mapped_column(String(20), server_default="waiting", index=True)
    create_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    update_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class CoachInterest(Base):
    __tablename__ = "coach_interest"
    __table_args__ = (UniqueConstraint("username", "learner_request_uuid", name="uq_coach_interest"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("coach_profile.username", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    learner_request_uuid: Mapped[UUID] = mapped_column(
        ForeignKey("learner_special_request.uuid", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    date: Mapped[dt_date] = mapped_column(Date)
    time: Mapped[dt_time] = mapped_column(Time)
    create_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    update_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class SpecialRequestCreate(BaseModel):
    username: str
    skill_name: str
    category: str
    description: str = ""


class CoachInterestCreate(BaseModel):
    username: str
    request_uuid: UUID
    date: str
    time: str


class SpecialRequestResponse(BaseModel):
    uuid: UUID
    skill_name: str
    category: str
    description: str
    status: str
    create_date: datetime


class InterestedCoachResponse(BaseModel):
    username: str
    firstname: str
    lastname: str
    image_path: Optional[str] = None
    date: str
    time: str


class AdminSpecialRequestResponse(SpecialRequestResponse):
    username: str
    firstname: str
    lastname: str
    image_path: Optional[str] = None
    interests: list[InterestedCoachResponse] = []


class CoachSpecialResponse(BaseModel):
    uuid: UUID
    skill_name: str
    category: str
    description: str
    create_date: datetime
    interest_count: int
    interested: bool
    interest_date: Optional[str] = None
    interest_time: Optional[str] = None