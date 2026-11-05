# main_api.py

from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import init_db
from controllers.coach_controller import router as coach_router
from controllers.learner_controller import router as learner_router
from controllers.login_controller import router as login_router
from pathlib import Path
from fastapi.staticfiles import StaticFiles

Path("uploads/avatars").mkdir(parents=True, exist_ok=True)   # must exist before mounting

from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(coach_router)
app.include_router(learner_router)
app.include_router(login_router)
