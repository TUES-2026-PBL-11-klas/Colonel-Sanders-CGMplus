from sqlalchemy.orm import Session
from sqlalchemy import select
from src.models.offerModel import OfferModel


class OfferRepository():
    def __init__(self, session: Session):
        self.model = OfferModel
        self.session = session

    def get_by_id(self, offer_id: int) -> OfferModel:
        return self.session.get(self.model, offer_id)

    def get_active(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[OfferModel]:
        stmt = (
            select(self.model)
            .where(self.model.is_active.is_(True))
            .limit(limit)
            .offset(offset)  # i dont really think this is needed
        )
        return self.session.scalars(stmt).all()
