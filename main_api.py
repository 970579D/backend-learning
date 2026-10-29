# main_api.py

from fastapi import FastAPI
from controllers.coach_controller import router as coach_router
from controllers.learner_controller import router as learner_router
from controllers.login_controller import router as login_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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

@app.get("/")
def home():
    return {"message": "Hello, FastAPI!"}