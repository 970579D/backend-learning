from datetime import datetime
from typing import Literal

from pydantic import BaseModel
from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base
from models.user_model import UserRequest


class CoachDetail(Base):
    __tablename__ = "coach_detail"
    __table_args__ = (
        CheckConstraint("cost >= 0", name="ck_coach_detail_cost"),
        CheckConstraint(
            "place_to_coach IN ('wherever', 'public', 'learner_home', 'class')",
            name="ck_coach_detail_place",
        ),
        CheckConstraint(
            "coaching_mode IN ('online', 'personal')",
            name="ck_coach_detail_mode",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("coach_profile.username", ondelete="CASCADE", onupdate="CASCADE"),
        unique=True,
    )
    about_coach: Mapped[str] = mapped_column(Text)
    course_description: Mapped[str] = mapped_column(Text)
    cost: Mapped[int] = mapped_column(BigInteger)
    place_to_coach: Mapped[str] = mapped_column(String(20))
    coaching_mode: Mapped[str] = mapped_column(String(20))
    create_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    update_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class CoachDetailData(BaseModel):
    about_coach: str
    course_description: str
    cost: int
    place_to_coach: Literal["wherever", "public", "learner_home", "class"]
    coaching_mode: Literal["online", "personal"]


class CoachRegisterRequest(UserRequest):
    detail: CoachDetailData