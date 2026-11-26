import uuid as uuid_lib
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class LearnerSpecialRequest(Base):
    __tablename__ = "learner_special_request"
    __table_args__ = (
        CheckConstraint(
            "status IN ('waiting', 'approved', 'rejected')",
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


class SpecialRequestCreate(BaseModel):
    username: str
    skill_name: str
    category: str
    description: str = ""


class SpecialRequestResponse(BaseModel):
    uuid: UUID
    skill_name: str
    category: str
    description: str
    status: str
    create_date: datetime


class AdminSpecialRequestResponse(SpecialRequestResponse):
    username: str
    firstname: str
    lastname: str
    image_path: Optional[str] = None