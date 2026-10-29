# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session

# from database import get_db
# from services.user_service import UserService

# router = APIRouter(prefix="/users", tags=["Users"])

# user_service = UserService()

# @router.get("/")
# def get_all_users(db: Session = Depends(get_db)):
#     return user_service.get_all_users(db)

# @router.get("/{username}")
# def find_user(username: str, db: Session = Depends(get_db)):
#     return user_service.find_user(db, username)

# @router.post("/")
# def create(user: dict, db: Session = Depends(get_db)):
#     return user_service.create(db, user)