from src.repositories.offerRepository import OfferRepository
from src.repositories.ProfileRepositoriy import ProfileRepository
from src.extensions import db
from src.models.RedemptionModel import RedemptionModel
from src.models.offerModel import PriceType
from src.exceptions.OfferExceptions import InsufficientFunds
from src.models.card import Card as CardModel
from uuid import UUID
from datetime import timedelta


class OfferService:
    @staticmethod
    def redeem_offer(offer_id: int, profile_id: UUID):
        offer = OfferRepository(db.session).get_by_id(offer_id)
        profile = ProfileRepository(db.session).get_by_uuid(profile_id=profile_id)

        if offer.price_type == PriceType.Points:
            if profile.balance < offer.price:
                raise InsufficientFunds()
            else:
                rdm = RedemptionModel(
                    offer_id=offer_id,
                    profile_id=profile_id,
                    points_cost=offer.price
                )
                db.session.add(rdm)

                profile.balance = profile.balance - offer.price
                card = db.session.get(CardModel, profile_id)
                card.expiry_date += timedelta(days=30)

                db.session.commit()
        return True
