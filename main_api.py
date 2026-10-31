# main_api.py

from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import init_db
from controllers.coach_controller import router as coach_router
from controllers.learner_controller import router as learner_router
from controllers.login_controller import router as login_router

from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # runs once at startup: create the database (if missing) and all tables
    init_db()
    yield
    # code after yield runs at shutdown (nothing to clean up here)


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(coach_router)
app.include_router(learner_router)
app.include_router(login_router)