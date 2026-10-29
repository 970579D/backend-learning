from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import BigInteger, Column, String, DateTime, Uuid, text
from sqlalchemy.orm import Mapped

from database import Base

class Score(Base):
    __tablename__ = "score"

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

    activity: Mapped[str] = Column(
        String(50),
        nullable=True,
        unique=True,
    )

    round: Mapped[str] = Column(
        BigInteger,
        nullable=True,
        unique=True,
    )
    
    score: Mapped[str] = Column(
        BigInteger,
        nullable=True,
        unique=True,
    )
    
    create_date: Mapped[datetime] = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    last_update: Mapped[datetime] = Column(
        DateTime(timezone=True),
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP"),
    )

class ScoreRequest(BaseModel):
    username: str
    score: str