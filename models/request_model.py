import uuid as uuid_lib
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class LearnerRequest(Base):
    __tablename__ = "learner_request"
    __table_args__ = (UniqueConstraint("username", "skill", name="uq_learner_request"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    uuid: Mapped[UUID] = mapped_column(Uuid, unique=True, default=uuid_lib.uuid4)
    username: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("learner_profile.username", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    skill: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("skill.skill_name", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    description: Mapped[str] = mapped_column(Text, server_default="")
    create_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    update_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class CoachResponse(Base):
    __tablename__ = "coach_response"
    __table_args__ = (UniqueConstraint("username", "request_uuid", name="uq_coach_response"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    uuid: Mapped[UUID] = mapped_column(Uuid, unique=True, default=uuid_lib.uuid4)
    username: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("coach_profile.username", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    request_uuid: Mapped[UUID] = mapped_column(
        ForeignKey("learner_request.uuid", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    create_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    update_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class LearnerRequestCreate(BaseModel):
    username: str
    skill: str
    description: str = ""


class CoachResponseCreate(BaseModel):
    username: str
    request_uuid: UUID


class RequirementResponse(BaseModel):
    level: str
    learning_for: str
    day: str
    time: str
    priority: str
    learning_mode: str
    place_to_learn: str
    province: str


class LearnerInfo(BaseModel):
    username: str
    firstname: str
    lastname: str
    image_path: Optional[str] = None


class ResponderResponse(BaseModel):
    uuid: UUID
    username: str
    firstname: str
    lastname: str
    image_path: Optional[str] = None
    create_date: datetime


class LearnerRequestResponse(BaseModel):
    uuid: UUID
    skill: str
    description: str
    create_date: datetime
    responses: list[ResponderResponse] = []


class MatchRequestResponse(BaseModel):
    uuid: UUID
    skill: str
    description: str
    create_date: datetime
    learner: LearnerInfo
    requirement: Optional[RequirementResponse] = None
    response_count: int
    responded: bool


class CoachResponseResult(BaseModel):
    uuid: UUID
    request_uuid: UUID
    skill: str
    create_date: datetime