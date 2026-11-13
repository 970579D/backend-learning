from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.response_model import Response_Model
from models.skill_model import (
    CategoryRequest, CategoryResponse, Skill, SkillCategory, SkillCoachResponse, SkillRequest, SkillResponse,
)
from repositories.skill_repository import SkillRepository

class SkillService:

    def __init__(self):
        self.repository = SkillRepository()

    def to_category_response(self, category: SkillCategory) -> CategoryResponse:
        return CategoryResponse(
            id=category.id,
            category_name=category.category_name,
            create_date=category.create_date,
        )

    def to_skill_response(self, skill: Skill) -> SkillResponse:
        return SkillResponse(
            id=skill.id,
            skill_name=skill.skill_name,
            category_name=skill.category_name,
            create_date=skill.create_date,
        )

    def list_categories(self, db: Session) -> Response_Model[list[CategoryResponse]]:
        response: Response_Model = Response_Model(status="success", message="OK")

        categories: list[CategoryResponse] = []
        for category in self.repository.list_categories(db):
            categories.append(self.to_category_response(category))

        response.data = categories
        return response

    def create_category(self, db: Session, req: CategoryRequest) -> Response_Model[CategoryResponse]:
        response: Response_Model = Response_Model(status="success", message="Category created successfully")

        name: str = req.category_name.strip()
        if not name:
            response.status = "error"
            response.message = "Category name is required"
            return response

        if self.repository.find_category(db, name):
            response.status = "error"
            response.message = "Category already exists"
            return response

        try:
            category = self.repository.create_category(db, name)
        except IntegrityError:
            db.rollback()
            response.status = "error"
            response.message = "Category already exists"
            return response

        response.data = self.to_category_response(category)
        return response

    def list_skills(self, db: Session) -> Response_Model[list[SkillResponse]]:
        response: Response_Model = Response_Model(status="success", message="OK")

        skills: list[SkillResponse] = []
        for skill in self.repository.list_skills(db):
            skills.append(self.to_skill_response(skill))

        response.data = skills
        return response

    def create_skill(self, db: Session, req: SkillRequest) -> Response_Model[SkillResponse]:
        response: Response_Model = Response_Model(status="success", message="Skill created successfully")

        name: str = req.skill_name.strip()
        if not name:
            response.status = "error"
            response.message = "Skill name is required"
            return response

        if self.repository.find_category(db, req.category_name) is None:
            response.status = "error"
            response.message = "Category does not exist"
            return response

        if self.repository.find_skill(db, name):
            response.status = "error"
            response.message = "Skill already exists"
            return response

        try:
            skill = self.repository.create_skill(db, name, req.category_name)
        except IntegrityError:
            db.rollback()
            response.status = "error"
            response.message = "Skill already exists"
            return response

        response.data = self.to_skill_response(skill)
        return response

    def list_skill_coaches(self, db: Session, skill_name: str) -> Response_Model[list[SkillCoachResponse]]:
        response: Response_Model = Response_Model(status="success", message="OK")

        if self.repository.find_skill(db, skill_name) is None:
            response.status = "error"
            response.message = "Skill does not exist"
            return response

        rows = self.repository.find_skill_assessments(db, skill_name)
        if not rows:
            response.data = []
            return response

        attempts = self.repository.find_attempts_with_total(db, [a.uuid for a, _ in rows])

        best: dict[UUID, tuple[int, int]] = {}
        for attempt, total in attempts:
            total_score: int = total or 100
            current = best.get(attempt.assessment_uuid)
            if current is None or attempt.score * current[1] > current[0] * total_score:
                best[attempt.assessment_uuid] = (attempt.score, total_score)

        coaches: list[SkillCoachResponse] = []
        for assessment, coach in rows:
            score, total_score = best.get(assessment.uuid, (0, 100))
            coaches.append(
                SkillCoachResponse(
                    username=coach.username,
                    firstname=coach.firstname,
                    lastname=coach.lastname,
                    image_path=coach.image_path,
                    status=assessment.status,
                    best_score=score,
                    best_total_score=total_score,
                    best_percent=round(score * 100 / total_score),
                    total_attempt=assessment.total_attempt,
                )
            )

        coaches.sort(key=lambda c: (c.status != "pass", -c.best_percent, -c.best_score, c.username))

        response.data = coaches
        return response