from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import BigInteger, Column, String, DateTime, text
from sqlalchemy.orm import Mapped, relationship

from models.skill_model import coach_skill

from database import Base

class User(Base):
    __abstract__ = True

    id: Mapped[int] = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    username: Mapped[str] = Column(
        String(50),
        nullable=False,
        unique=True,
    )

    password: Mapped[str] = Column(
        String(255),
        nullable=False,
    )

    firstname: Mapped[str] = Column(
        String(50),
        nullable=False,
    )

    lastname: Mapped[str] = Column(
        String(50),
        nullable=False,
    )

    create_date: Mapped[datetime] = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    last_update: Mapped[datetime] = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

class CoachProfile(User):
    __tablename__ = "coach_profile"

    status: Mapped[str] = Column(String(20), nullable=False, server_default=text("'active'"))

    skills: Mapped[set["Skill"]] = relationship(
        secondary="coach_skill",
        back_populates="coaches",
        lazy="selectin",
        passive_deletes=True,
    )


class Learner(User):
    __tablename__ = "learner_profile"

class UserRequest(BaseModel):
    username: str
    password: str
    firstname: str
    lastname: str
