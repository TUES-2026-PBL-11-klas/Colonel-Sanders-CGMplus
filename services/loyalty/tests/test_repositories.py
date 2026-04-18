"""Tests for repository layer."""
import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from src.repositories.offerRepository import OfferRepository
from src.repositories.ProfileRepositority import ProfileRepository
from src.repositories.RedemptionRepository import RedemptionRepository
from src.extensions import db
from src.models.profile import Profile
from src.models.pointTransaction import PointTransaction
from src.models.offerModel import OfferModel, PriceType, RewardType
from src.models.RedemptionModel import RedemptionModel


class TestOfferRepository:
    """Test OfferRepository."""

    def test_get_by_id(self, app, test_offer):
        """Test getting offer by ID."""
        with app.app_context():
            # Merge the fixture into the session
            offer_data = db.session.merge(test_offer)
            offer_id = offer_data.id
            offer_name = offer_data.name

            repo = OfferRepository(db.session)
            offer = repo.get_by_id(offer_id)

            assert offer is not None
            assert offer.id == offer_id
            assert offer.name == offer_name

    def test_get_by_id_nonexistent(self, app):
        """Test getting non-existent offer returns None."""
        with app.app_context():
            repo = OfferRepository(db.session)
            offer = repo.get_by_id(999)

            assert offer is None

    def test_get_active(self, app):
        """Test getting active offers."""
        with app.app_context():
            # Create active and inactive offers
            active1 = OfferModel(
                name="Active 1",
                price=100,
                price_type=PriceType.Points,
                reward_type=RewardType.CardRenew,
                valid_until=datetime.now() + timedelta(days=30),
                is_active=True
            )
            active2 = OfferModel(
                name="Active 2",
                price=200,
                price_type=PriceType.Points,
                reward_type=RewardType.CardSkin,
                valid_until=datetime.now() + timedelta(days=30),
                is_active=True
            )
            inactive = OfferModel(
                name="Inactive",
                price=150,
                price_type=PriceType.Points,
                reward_type=RewardType.CardRenew,
                valid_until=datetime.now() + timedelta(days=30),
                is_active=False
            )
            db.session.add_all([active1, active2, inactive])
            db.session.commit()

            repo = OfferRepository(db.session)
            active_offers = repo.get_active()

            assert len(active_offers) >= 2
            assert all(offer.is_active for offer in active_offers)
            assert inactive not in active_offers

    def test_get_active_with_limit(self, app):
        """Test getting active offers with limit."""
        with app.app_context():
            # Create 5 active offers
            for i in range(5):
                offer = OfferModel(
                    name=f"Offer {i}",
                    price=100 + i * 10,
                    price_type=PriceType.Points,
                    reward_type=RewardType.CardRenew,
                    valid_until=datetime.now() + timedelta(days=30),
                    is_active=True
                )
                db.session.add(offer)
            db.session.commit()

            repo = OfferRepository(db.session)
            offers = repo.get_active(limit=2)

            assert len(offers) <= 2

    def test_get_active_with_offset(self, app):
        """Test getting active offers with offset."""
        with app.app_context():
            # Create offers
            for i in range(5):
                offer = OfferModel(
                    name=f"Offer {i}",
                    price=100,
                    price_type=PriceType.Points,
                    reward_type=RewardType.CardRenew,
                    valid_until=datetime.now() + timedelta(days=30),
                    is_active=True
                )
                db.session.add(offer)
            db.session.commit()

            repo = OfferRepository(db.session)
            first_batch = repo.get_active(limit=2, offset=0)
            second_batch = repo.get_active(limit=2, offset=2)

            assert len(first_batch) >= 2
            assert len(second_batch) >= 2
            # IDs should be different
            first_ids = {o.id for o in first_batch}
            second_ids = {o.id for o in second_batch}
            assert first_ids != second_ids


class TestProfileRepository:
    """Test ProfileRepository."""

    def test_get_by_uuid(self, app, test_profile):
        """Test getting profile by UUID."""
        with app.app_context():
            # Merge the fixture into the session
            profile_data = db.session.merge(test_profile)
            profile_id = profile_data.id
            profile_balance = profile_data.balance

            repo = ProfileRepository(db.session)
            profile = repo.get_by_uuid(profile_id)

            assert profile is not None
            assert profile.id == profile_id
            assert profile.balance == profile_balance

    def test_get_by_uuid_nonexistent(self, app):
        """Test getting non-existent profile returns None."""
        with app.app_context():
            repo = ProfileRepository(db.session)
            profile = repo.get_by_uuid(uuid4())

            assert profile is None

    def test_get_by_uuid_multiple_profiles(self, app):
        """Test retrieving specific profile among multiple."""
        with app.app_context():
            profile1_id = uuid4()
            profile2_id = uuid4()

            profile1 = Profile(id=profile1_id, balance=100, rank="bronze")
            profile2 = Profile(id=profile2_id, balance=200, rank="silver")
            db.session.add_all([profile1, profile2])
            db.session.commit()

            repo = ProfileRepository(db.session)
            retrieved1 = repo.get_by_uuid(profile1_id)
            retrieved2 = repo.get_by_uuid(profile2_id)

            assert retrieved1.balance == 100
            assert retrieved2.balance == 200


class TestRedemptionRepository:
    """Test RedemptionRepository."""

    def test_get_by_profile_id(self, app, test_profile):
        """Test getting redemptions by profile ID."""
        with app.app_context():
            # Merge the fixture into the session
            profile_data = db.session.merge(test_profile)
            profile_id = profile_data.id

            # Create offers
            offer1 = OfferModel(
                name="Offer 1",
                price=100,
                price_type=PriceType.Points,
                reward_type=RewardType.CardRenew,
                valid_until=datetime.now() + timedelta(days=30),
                is_active=True
            )
            offer2 = OfferModel(
                name="Offer 2",
                price=200,
                price_type=PriceType.Points,
                reward_type=RewardType.CardSkin,
                valid_until=datetime.now() + timedelta(days=30),
                is_active=True
            )
            db.session.add_all([offer1, offer2])
            db.session.commit()

            # Create redemptions
            redemption1 = RedemptionModel(
                id=uuid4(),
                offer_id=offer1.id,
                profile_id=profile_id,
                points_cost=100
            )
            redemption2 = RedemptionModel(
                id=uuid4(),
                offer_id=offer2.id,
                profile_id=profile_id,
                points_cost=200
            )
            db.session.add_all([redemption1, redemption2])
            db.session.commit()

            repo = RedemptionRepository(db.session)
            redemptions = repo.get_by_profile_id(profile_id)

            assert len(redemptions) == 2
            assert all(r.profile_id == profile_id for r in redemptions)

    def test_get_by_profile_id_empty(self, app):
        """Test getting redemptions for profile with no redemptions."""
        with app.app_context():
            profile = Profile(id=uuid4(), balance=100, rank="bronze")
            db.session.add(profile)
            db.session.commit()

            repo = RedemptionRepository(db.session)
            redemptions = repo.get_by_profile_id(profile.id)

            assert len(redemptions) == 0

    def test_get_by_profile_id_multiple_profiles(self, app):
        """Test redemptions are properly filtered by profile."""
        with app.app_context():
            profile1_id = uuid4()
            profile2_id = uuid4()

            profile1 = Profile(id=profile1_id, balance=100, rank="bronze")
            profile2 = Profile(id=profile2_id, balance=200, rank="silver")
            db.session.add_all([profile1, profile2])

            offer = OfferModel(
                name="Offer",
                price=100,
                price_type=PriceType.Points,
                reward_type=RewardType.CardRenew,
                valid_until=datetime.now() + timedelta(days=30),
                is_active=True
            )
            db.session.add(offer)
            db.session.commit()

            # Create redemptions for both profiles
            redemption1 = RedemptionModel(
                id=uuid4(),
                offer_id=offer.id,
                profile_id=profile1_id,
                points_cost=100
            )
            redemption2 = RedemptionModel(
                id=uuid4(),
                offer_id=offer.id,
                profile_id=profile2_id,
                points_cost=100
            )
            db.session.add_all([redemption1, redemption2])
            db.session.commit()

            repo = RedemptionRepository(db.session)
            profile1_redemptions = repo.get_by_profile_id(profile1_id)
            profile2_redemptions = repo.get_by_profile_id(profile2_id)

            assert len(profile1_redemptions) == 1
            assert len(profile2_redemptions) == 1
            assert profile1_redemptions[0].profile_id == profile1_id
            assert profile2_redemptions[0].profile_id == profile2_id
