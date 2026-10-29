from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import BigInteger, Column, String, DateTime, text
from sqlalchemy.orm import Mapped

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

class Coach(User):
    __tablename__ = "coach_profile"


class Learner(User):
    __tablename__ = "learner_profile"

class UserRequest(BaseModel):
    username: str
    password: str
