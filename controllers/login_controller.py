from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from services.login_service import LoginService

router = APIRouter(prefix="/login", tags=["Login"])

login_service = LoginService()

@router.get("/")
def find_login(username: str, db: Session = Depends(get_db)):
    return login_service.find_login(db, username)

@router.post("/coach")
def create_login_coach(user: dict, db: Session = Depends(get_db)):
    return login_service.create_login_coach(db, user)
    
@router.post("/learner")
def create_login_leaner(user: dict, db: Session = Depends(get_db)):
    return login_service.create_login_learner(db, user)

@router.post("/admin")
def create_login_admin(user: dict, db: Session = Depends(get_db)):
    return login_service.create_login_admin(db, user)

@router.put("/logout/coach")
def logout_coach(logout: dict, db: Session = Depends(get_db)):
    return login_service.logout_coach(db, logout)

@router.put("/logout/learner")
def logout_learner(logout: dict, db: Session = Depends(get_db)):
    return login_service.logout_learner(db, logout)

@router.put("/logout/admin")
def logout_admin(logout: dict, db: Session = Depends(get_db)):
    return login_service.logout_admin(db, logout)