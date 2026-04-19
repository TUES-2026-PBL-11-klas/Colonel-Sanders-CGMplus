"""Integration tests for the loyalty service."""
import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from src.extensions import db
from src.models.profile import Profile
from src.models.card import Card
from src.models.offerModel import OfferModel, PriceType, RewardType
from src.models.pointTransaction import PT_TypeEnum
from src.services.ProfileService import ProfileService
from src.services.CardService import CardService
from src.services.OfferService import OfferService
from src.services.PointService import PointService
from src.repositories.offerRepository import OfferRepository
from src.repositories.ProfileRepositority import ProfileRepository
from src.repositories.RedemptionRepository import RedemptionRepository


class TestUserJourney:
    """Test complete user journey through the service."""

    def test_create_user_and_earn_points(self, app):
        """Test creating a user and earning points."""
        with app.app_context():
            user_id = uuid4()

            # Create profile
            profile = ProfileService.create_profile(user_id)
            assert profile.balance == 0

            # Create card
            card = CardService.create_card(user_id)
            assert card.nfc_id == "0000000000000000"

            # Add points
            PointService.add_points(user_id)

            # Verify balance increased
            profile = Profile.query.get(user_id)
            assert profile.balance == 67

    def test_redeem_offer_workflow(self, app):
        """Test complete redemption workflow."""
        with app.app_context():
            user_id = uuid4()

            # Setup user
            ProfileService.create_profile(user_id)
            CardService.create_card(user_id)
            PointService.add_points(user_id)

            # Create offer
            offer = OfferModel(
                name="Card Renewal",
                price=50,
                price_type=PriceType.Points,
                reward_type=RewardType.CardRenew,
                valid_until=datetime.now() + timedelta(days=30),
                is_active=True
            )
            db.session.add(offer)
            db.session.commit()

            # Redeem offer
            initial_balance = Profile.query.get(user_id).balance
            initial_expiry = Card.query.get(user_id).expiry_date

            OfferService.redeem_offer(offer.id, user_id)

            # Verify state changes
            profile = Profile.query.get(user_id)
            card = Card.query.get(user_id)

            assert profile.balance == initial_balance - 50
            assert card.expiry_date > initial_expiry

    def test_multiple_users_independent(self, app):
        """Test that multiple users are independent."""
        with app.app_context():
            user1_id = uuid4()
            user2_id = uuid4()

            # Create both users
            ProfileService.create_profile(user1_id)
            CardService.create_card(user1_id)

            ProfileService.create_profile(user2_id)
            CardService.create_card(user2_id)

            # Add points to user1 only
            PointService.add_points(user1_id)
            PointService.add_points(user1_id)

            # Verify independence
            user1 = Profile.query.get(user1_id)
            user2 = Profile.query.get(user2_id)

            assert user1.balance == 134  # 67 * 2
            assert user2.balance == 0

    def test_offer_listing_and_filtering(self, app):
        """Test retrieving and filtering offers."""
        with app.app_context():
            # Create offers
            active_offer = OfferModel(
                name="Active",
                price=100,
                price_type=PriceType.Points,
                reward_type=RewardType.CardRenew,
                valid_until=datetime.now() + timedelta(days=30),
                is_active=True
            )
            inactive_offer = OfferModel(
                name="Inactive",
                price=200,
                price_type=PriceType.Points,
                reward_type=RewardType.CardSkin,
                valid_until=datetime.now() + timedelta(days=30),
                is_active=False
            )
            db.session.add_all([active_offer, inactive_offer])
            db.session.commit()

            # Get active offers
            repo = OfferRepository(db.session)
            active_offers = repo.get_active()

            assert len(active_offers) >= 1
            assert all(o.is_active for o in active_offers)

    def test_redemption_history(self, app):
        """Test tracking redemption history."""
        with app.app_context():
            user_id = uuid4()

            # Setup user with balance
            profile = Profile(id=user_id, balance=500, rank="bronze")
            card = Card(
                id=user_id,
                nfc_id="TEST123",
                expiry_date=datetime.now() + timedelta(days=30)
            )
            db.session.add_all([profile, card])
            db.session.commit()

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
                price=150,
                price_type=PriceType.Points,
                reward_type=RewardType.CardSkin,
                valid_until=datetime.now() + timedelta(days=30),
                is_active=True
            )
            db.session.add_all([offer1, offer2])
            db.session.commit()

            # Redeem offers
            OfferService.redeem_offer(offer1.id, user_id)
            OfferService.redeem_offer(offer2.id, user_id)

            # Check history
            repo = RedemptionRepository(db.session)
            redemptions = repo.get_by_profile_id(user_id)

            assert len(redemptions) == 2
            assert sum(r.points_cost for r in redemptions) == 250

    def test_profile_ranking(self, app):
        """Test profile ranking based on activity."""
        with app.app_context():
            user_id = uuid4()

            # Create profile
            profile = ProfileService.create_profile(user_id)
            assert profile.rank == "bronze"  # Default rank

            # Verify rank is stored
            retrieved = Profile.query.get(user_id)
            assert retrieved.rank == "bronze"

    def test_point_transaction_tracking(self, app):
        """Test point transaction records are created."""
        with app.app_context():
            user_id = uuid4()
            profile = ProfileService.create_profile(user_id)

            # Add points multiple times
            PointService.add_points(user_id)
            PointService.add_points(user_id)
            PointService.add_points(user_id)

            # Verify all transactions recorded
            profile = Profile.query.get(user_id)
            assert len(profile.transactions) == 3
            assert all(t.ammount == 67 for t in profile.transactions)

    def test_card_expiry_extension(self, app):
        """Test card expiry date extends on redemption."""
        with app.app_context():
            user_id = uuid4()

            # Setup
            profile = Profile(id=user_id, balance=500, rank="bronze")
            expiry_date = datetime.now()
            card = Card(
                id=user_id,
                nfc_id="TEST123",
                expiry_date=expiry_date
            )
            db.session.add_all([profile, card])
            db.session.commit()

            # Create and redeem offer
            offer = OfferModel(
                name="Extension",
                price=100,
                price_type=PriceType.Points,
                reward_type=RewardType.CardRenew,
                valid_until=datetime.now() + timedelta(days=30),
                is_active=True
            )
            db.session.add(offer)
            db.session.commit()

            OfferService.redeem_offer(offer.id, user_id)

            # Verify expiry extended by 30 days
            card = Card.query.get(user_id)
            expected_expiry = expiry_date + timedelta(days=30)
            assert card.expiry_date.date() == expected_expiry.date()


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_redemption_boundary_balance(self, app):
        """Test redemption with exact balance."""
        with app.app_context():
            user_id = uuid4()

            # Create user with exact balance
            profile = Profile(id=user_id, balance=100, rank="bronze")
            card = Card(
                id=user_id,
                nfc_id="TEST123",
                expiry_date=datetime.now() + timedelta(days=30)
            )
            db.session.add_all([profile, card])

            # Create exact offer
            offer = OfferModel(
                name="Exact Offer",
                price=100,
                price_type=PriceType.Points,
                reward_type=RewardType.CardRenew,
                valid_until=datetime.now() + timedelta(days=30),
                is_active=True
            )
            db.session.add(offer)
            db.session.commit()

            # Redeem with exact balance
            OfferService.redeem_offer(offer.id, user_id)

            # Verify balance is exactly 0
            profile = Profile.query.get(user_id)
            assert profile.balance == 0

    def test_consecutive_point_additions(self, app):
        """Test adding points multiple times consecutively."""
        with app.app_context():
            user_id = uuid4()
            profile = ProfileService.create_profile(user_id)

            # Add points 10 times
            for _ in range(10):
                PointService.add_points(user_id)

            # Verify final balance
            profile = Profile.query.get(user_id)
            assert profile.balance == 67 * 10

    def test_zero_balance_operations(self, app):
        """Test operations with zero balance."""
        with app.app_context():
            user_id = uuid4()
            profile = ProfileService.create_profile(user_id)
            assert profile.balance == 0

            # Verify can't redeem without balance
            offer = OfferModel(
                name="Offer",
                price=1,
                price_type=PriceType.Points,
                reward_type=RewardType.CardRenew,
                valid_until=datetime.now() + timedelta(days=30),
                is_active=True
            )
            card = Card(
                id=user_id,
                nfc_id="TEST123",
                expiry_date=datetime.now()
            )
            db.session.add_all([offer, card])
            db.session.commit()

            from src.exceptions.OfferExceptions import InsufficientFunds
            with pytest.raises(InsufficientFunds):
                OfferService.redeem_offer(offer.id, user_id)
