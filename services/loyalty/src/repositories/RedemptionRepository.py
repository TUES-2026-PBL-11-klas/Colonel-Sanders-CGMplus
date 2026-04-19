from sqlalchemy.orm import Session
from sqlalchemy import select
from src.models.RedemptionModel import RedemptionModel
from uuid import UUID


class RedemptionRepository:
    def __init__(self, session: Session):
        self.model = RedemptionModel
        self.session = session

    def get_by_profile_id(self, profile_id: UUID) -> list[RedemptionModel]:
        stmt = select(self.model).where(self.model.profile_id == profile_id)
        result = self.session.execute(stmt)
        return result.scalars().all()
