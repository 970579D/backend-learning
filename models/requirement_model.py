from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field
from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base
from models.user_model import UserRequest


class LearnerRequirement(Base):
    __tablename__ = "learner_requirement"
    __table_args__ = (
        CheckConstraint(
            "level IN ('junior_elementary', 'senior_elementary', 'junior_high', 'senior_high', 'university', 'working')",
            name="ck_learner_requirement_level",
        ),
        CheckConstraint(
            "learning_for IN ('exam_preparation', 'skill_development', 'project_based')",
            name="ck_learner_requirement_learning_for",
        ),
        CheckConstraint(
            "day IN ('weekdays', 'weekend', 'everyday')",
            name="ck_learner_requirement_day",
        ),
        CheckConstraint(
            "time IN ('morning', 'afternoon', 'evening', 'night', 'anytime')",
            name="ck_learner_requirement_time",
        ),
        CheckConstraint(
            "priority IN ('normal', 'quick', 'urgent')",
            name="ck_learner_requirement_priority",
        ),
        CheckConstraint(
            "learning_mode IN ('online', 'personal')",
            name="ck_learner_requirement_mode",
        ),
        CheckConstraint(
            "place_to_learn IN ('wherever', 'public', 'learner_home', 'class')",
            name="ck_learner_requirement_place",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("learner_profile.username", ondelete="CASCADE", onupdate="CASCADE"),
        unique=True,
    )
    level: Mapped[str] = mapped_column(String(30))
    learning_for: Mapped[str] = mapped_column(String(30))
    day: Mapped[str] = mapped_column(String(20))
    time: Mapped[str] = mapped_column(String(20))
    priority: Mapped[str] = mapped_column(String(20), server_default="normal")
    learning_mode: Mapped[str] = mapped_column(String(20))
    place_to_learn: Mapped[str] = mapped_column(String(20))
    province: Mapped[str] = mapped_column(String(100))
    create_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    update_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class RequirementData(BaseModel):
    level: Literal["junior_elementary", "senior_elementary", "junior_high", "senior_high", "university", "working"]
    learning_for: Literal["exam_preparation", "skill_development", "project_based"]
    day: Literal["weekdays", "weekend", "everyday"]
    time: Literal["morning", "afternoon", "evening", "night", "anytime"]
    priority: Literal["normal", "quick", "urgent"]
    learning_mode: Literal["online", "personal"]
    place_to_learn: Literal["wherever", "public", "learner_home", "class"]
    province: str = Field(min_length=1, max_length=100)


class LearnerRegisterRequest(UserRequest):
    phone: str
    requirement: RequirementData