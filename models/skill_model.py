import uuid as uuid_lib
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy import (
    BigInteger, CheckConstraint, Column, DateTime, ForeignKey, String, Table, UniqueConstraint, Uuid, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

coach_skill = Table(
    "coach_skill",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column(
        "username",
        String(50),
        ForeignKey("coach_profile.username", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column(
        "skill_name",
        String(100),
        ForeignKey("skill.skill_name", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column("status", String(20), nullable=False, server_default="inactive"),
    UniqueConstraint("username", "skill_name", name="uq_coach_skill"),
    CheckConstraint("status IN ('active', 'inactive')", name="ck_coach_skill_status"),
)


class SkillCategory(Base):
    __tablename__ = "skill_category"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    category_name: Mapped[str] = mapped_column(String(100), unique=True)
    create_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    update_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    skills: Mapped[set["Skill"]] = relationship(back_populates="category")


class Skill(Base):
    __tablename__ = "skill"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    skill_name: Mapped[str] = mapped_column(String(100), unique=True)
    category_name: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("skill_category.category_name", onupdate="CASCADE"),
        index=True,
    )
    create_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    update_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    category: Mapped["SkillCategory"] = relationship(back_populates="skills", lazy="joined")

    coaches: Mapped[set["CoachProfile"]] = relationship(
        secondary=coach_skill,
        back_populates="skills",
        passive_deletes=True,
    )


class Assessment(Base):

    __tablename__ = "assessment"

    __table_args__ = (
        UniqueConstraint("username", "assessment_skill", name="uq_assessment"),
        CheckConstraint("status IN ('pending', 'pass', 'fail')", name="ck_assessment_status"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    uuid: Mapped[UUID] = mapped_column(Uuid, unique=True, default=uuid_lib.uuid4)
    username: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("coach_profile.username", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    assessment_skill: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("skill.skill_name", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    total_attempt: Mapped[int] = mapped_column(BigInteger, server_default="0")
    status: Mapped[str] = mapped_column(String(20), server_default="pending")
    create_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    update_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class AssessmentAttempt(Base):

    __tablename__ = "assessment_attempt"

    __table_args__ = (
        UniqueConstraint("assessment_uuid", "round_attempt", name="uq_assessment_attempt"),
        CheckConstraint("status IN ('pass', 'fail')", name="ck_assessment_attempt_status"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    assessment_uuid: Mapped[UUID] = mapped_column(
        ForeignKey("assessment.uuid", ondelete="CASCADE", onupdate="CASCADE"), index=True
    )
    round_attempt: Mapped[int] = mapped_column(BigInteger)
    score: Mapped[int] = mapped_column(BigInteger)
    status: Mapped[str] = mapped_column(String(20))
    create_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    update_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class AttemptData(BaseModel):
    id: int
    assessment_uuid: UUID
    assessment_skill: str
    round_attempt: int
    score: int
    total_score: int
    status: str
    create_date: datetime
    update_date: datetime


class AssessmentResponse(BaseModel):
    id: int
    uuid: UUID
    assessment_skill: str
    assessment_skill_category: str
    status: str
    total_attempt: int
    attemps: list[AttemptData] = []


class CategoryRequest(BaseModel):
    category_name: str = Field(min_length=1, max_length=100)


class CategoryResponse(BaseModel):
    id: int
    category_name: str
    create_date: datetime


class SkillRequest(BaseModel):
    skill_name: str = Field(min_length=1, max_length=100)
    category_name: str


class SkillResponse(BaseModel):
    id: int
    skill_name: str
    category_name: str
    create_date: datetime