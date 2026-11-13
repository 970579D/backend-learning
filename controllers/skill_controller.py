from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.skill_model import CategoryRequest, SkillRequest
from services.skill_service import SkillService

router = APIRouter(prefix="/skill", tags=["Skill"])

skill_service = SkillService()

@router.get("/category")
def list_categories(db: Session = Depends(get_db)):
    return skill_service.list_categories(db)

@router.post("/category")
def create_category(req: CategoryRequest, db: Session = Depends(get_db)):
    return skill_service.create_category(db, req)

@router.get("")
def list_skills(db: Session = Depends(get_db)):
    return skill_service.list_skills(db)

@router.post("")
def create_skill(req: SkillRequest, db: Session = Depends(get_db)):
    return skill_service.create_skill(db, req)

@router.get("/coach")
def list_skill_coaches(skill_name: str, db: Session = Depends(get_db)):
    return skill_service.list_skill_coaches(db, skill_name)