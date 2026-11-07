from sqlalchemy import select
from sqlalchemy.orm import Session

from models.skill_model import Skill, SkillCategory


class SkillRepository:

    def list_categories(self, db: Session) -> list[SkillCategory]:
        return list(db.scalars(select(SkillCategory).order_by(SkillCategory.category_name)).all())

    def find_category(self, db: Session, category_name: str) -> SkillCategory | None:
        return db.scalar(select(SkillCategory).where(SkillCategory.category_name == category_name))

    def create_category(self, db: Session, category_name: str) -> SkillCategory:
        category = SkillCategory(category_name=category_name)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    def list_skills(self, db: Session) -> list[Skill]:
        return list(db.scalars(select(Skill).order_by(Skill.category_name, Skill.skill_name)).all())

    def find_skill(self, db: Session, skill_name: str) -> Skill | None:
        return db.scalar(select(Skill).where(Skill.skill_name == skill_name))

    def create_skill(self, db: Session, skill_name: str, category_name: str) -> Skill:
        skill = Skill(skill_name=skill_name, category_name=category_name)
        db.add(skill)
        db.commit()
        db.refresh(skill)
        return skill