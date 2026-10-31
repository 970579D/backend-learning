import uuid as uuid_lib
from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    BigInteger, Column, DateTime, ForeignKey, String, Table, UniqueConstraint, Uuid, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

coach_skill = Table(
    "coach_skill",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("uuid", Uuid, unique=True, nullable=False, default=uuid_lib.uuid4),
    Column(
        "coach_uuid",
        String(50),
        ForeignKey("coach_profile.username", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column(
        "skill_uuid",
        Uuid,
        ForeignKey("skill.uuid", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    UniqueConstraint("coach_uuid", "skill_uuid", name="uq_coach_skill"),
)


class SkillCategory(Base):
    __tablename__ = "skill_category"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    uuid: Mapped[UUID] = mapped_column(Uuid, unique=True, default=uuid_lib.uuid4)
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
    uuid: Mapped[UUID] = mapped_column(Uuid, unique=True, default=uuid_lib.uuid4)
    skill_name: Mapped[str] = mapped_column(String(100))
    category_uuid: Mapped[UUID] = mapped_column(
        ForeignKey("skill_category.uuid"), index=True
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