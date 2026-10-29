from datetime import datetime

from sqlalchemy import (
    BigInteger,
    String,
    DateTime,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Login(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )

    session: Mapped[str] = mapped_column(
        Uuid,
        nullable=False,
        unique=True,
    )

    login_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    logout_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class CoachLogin(Login):
    __tablename__ = "coach_login"


class LearnerLogin(Login):
    __tablename__ = "learner_login"