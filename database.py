import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def ensure_database() -> None:
    """Create the database from DATABASE_URL if it does not exist yet (PostgreSQL)."""
    url = make_url(DATABASE_URL)
    db_name = url.database

    # connect to the default "postgres" database to run CREATE DATABASE
    admin_engine = create_engine(
        url.set(database="postgres"),
        isolation_level="AUTOCOMMIT",  # CREATE DATABASE can't run inside a transaction
    )
    try:
        with admin_engine.connect() as conn:
            exists = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": db_name},
            ).scalar()
            if not exists:
                conn.execute(text(f'CREATE DATABASE "{db_name}"'))
    finally:
        admin_engine.dispose()


def init_db() -> None:
    """Create the database (if missing), then all tables."""
    ensure_database()

    # import models here (not at the top) to avoid a circular import,
    # because the model files import Base from this file
    import models.user_model   # coach_profile, learner_profile
    import models.skill_model  # skill_category, skill, coach_skill

    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()