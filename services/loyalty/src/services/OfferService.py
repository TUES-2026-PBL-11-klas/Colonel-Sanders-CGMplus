from src.repositories.offerRepository import OfferRepository
from src.repositories.ProfileRepositority import ProfileRepository
from src.extensions import db
from src.models.RedemptionModel import RedemptionModel
from src.models.offerModel import PriceType
from src.exceptions.OfferExceptions import InsufficientFunds
from src.models.card import Card as CardModel
from uuid import UUID
from datetime import timedelta
from src.exceptions.OfferExceptions import InvalidOffer
from src.exceptions.ProfileExceptions import (
    ProfileNotFound,
    CardNotFound
)


class OfferService:
    @staticmethod
    def redeem_offer(offer_id: int, profile_id: UUID):
        offer = OfferRepository(db.session).get_by_id(offer_id)
        if offer is None:
            raise InvalidOffer(f"Offer with id {offer_id} not found")

        profile = ProfileRepository(
            db.session
        ).get_by_uuid(profile_id=profile_id)
        if profile is None:
            raise ProfileNotFound(f"Profile with id {profile_id} not found")

        if offer.price_type == PriceType.Points:
            if profile.balance < offer.price:
                raise InsufficientFunds()

            card = db.session.get(CardModel, profile_id)
            if card is None:
                raise CardNotFound(f"Card for profile {profile_id} not found")

            rdm = RedemptionModel(
                offer_id=offer_id,
                profile_id=profile_id,
                points_cost=offer.price
            )
            db.session.add(rdm)
            profile.balance = profile.balance - offer.price
            card.expiry_date += timedelta(days=30)
            db.session.commit()

        return True
