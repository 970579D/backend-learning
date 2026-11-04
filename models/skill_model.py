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
    Column(
        "coach_username",
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
    UniqueConstraint("coach_username", "skill_name", name="uq_coach_skill"),
)


class SkillCategory(Base):
    __tablename__ = "skill_category"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    category_name: Mapped[str] = mapped_column(String(100), unique=True)   # the key
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
    skill_name: Mapped[str] = mapped_column(String(100), unique=True)      # the key
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