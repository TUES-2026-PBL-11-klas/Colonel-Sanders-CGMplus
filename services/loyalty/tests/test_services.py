"""Tests for service layer."""
import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from src.services.ProfileService import ProfileService
from src.services.CardService import CardService
from src.services.PointService import PointService
from src.services.OfferService import OfferService
from src.extensions import db
from src.models.profile import Profile
from src.models.card import Card
from src.models.pointTransaction import PointTransaction, PT_TypeEnum
from src.models.offerModel import OfferModel, PriceType, RewardType
from src.models.RedemptionModel import RedemptionModel
from src.exceptions.ProfileExceptions import ProfileNotFound, CardNotFound
from src.exceptions.OfferExceptions import InsufficientFunds, InvalidOffer


class TestProfileService:
    """Test ProfileService."""

    def test_create_profile(self, app):
        """Test creating a profile."""
        with app.app_context():
            profile_id = uuid4()
            profile = ProfileService.create_profile(profile_id)

            assert profile.id == profile_id
            assert profile.balance == 0
            assert profile.rank == "bronze"

            # Verify it's in the database
            db_profile = Profile.query.get(profile_id)
            assert db_profile is not None
            assert db_profile.balance == 0

    def test_create_profile_with_unique_ids(self, app):
        """Test creating multiple profiles with unique IDs."""
        with app.app_context():
            profile1_id = uuid4()
            profile2_id = uuid4()

            profile1 = ProfileService.create_profile(profile1_id)
            profile2 = ProfileService.create_profile(profile2_id)

            assert profile1.id != profile2.id
            assert Profile.query.count() == 2


class TestCardService:
    """Test CardService."""

    def test_create_card(self, app):
        """Test creating a card."""
        with app.app_context():
            card_id = uuid4()
            card = CardService.create_card(card_id)

            assert card.id == card_id
            assert card.nfc_id == "0000000000000000"
            assert card.active is False
            assert card.disabled is False

            # Verify in database
            db_card = Card.query.get(card_id)
            assert db_card is not None

    def test_card_created_at_current_time(self, app):
        """Test card expiry_date is set to current time."""
        with app.app_context():
            before_creation = datetime.now()
            card = CardService.create_card(uuid4())
            after_creation = datetime.now()

            assert before_creation <= card.expiry_date <= after_creation

    def test_multiple_cards(self, app):
        """Test creating multiple cards."""
        with app.app_context():
            card1 = CardService.create_card(uuid4())
            card2 = CardService.create_card(uuid4())

            assert card1.id != card2.id
            assert Card.query.count() == 2


class TestPointService:
    """Test PointService."""

    def test_add_points_success(self, app):
        """Test adding points to profile."""
        with app.app_context():
            profile_id = uuid4()
            profile = Profile(id=profile_id, balance=100, rank="bronze")
            db.session.add(profile)
            db.session.commit()

            initial_balance = profile.balance
            result = PointService.add_points(profile_id)

            assert result is True

            # Verify profile balance increased
            profile = Profile.query.get(profile_id)
            assert profile.balance == initial_balance + 67

    def test_add_points_creates_transaction(self, app):
        """Test that adding points creates a transaction record."""
        with app.app_context():
            profile_id = uuid4()
            profile = Profile(id=profile_id, balance=100, rank="bronze")
            db.session.add(profile)
            db.session.commit()

            PointService.add_points(profile_id)

            transaction = PointTransaction.query.filter_by(
                account_id=profile_id
            ).first()
            assert transaction is not None
            assert transaction.ammount == 67
            assert transaction.pt_type == PT_TypeEnum.transport

    def test_add_points_transaction_description(self, app):
        """Test transaction has correct description."""
        with app.app_context():
            profile_id = uuid4()
            profile = Profile(id=profile_id, balance=100, rank="bronze")
            db.session.add(profile)
            db.session.commit()

            PointService.add_points(profile_id)

            transaction = PointTransaction.query.filter_by(
                account_id=profile_id
            ).first()
            assert "67 earned by using the transportation" in transaction.description

    def test_add_points_nonexistent_profile(self, app):
        """Test adding points to non-existent profile raises error."""
        with app.app_context():
            fake_id = uuid4()
            with pytest.raises(ProfileNotFound):
                PointService.add_points(fake_id)

    def test_add_points_multiple_times(self, app):
        """Test adding points multiple times."""
        with app.app_context():
            profile_id = uuid4()
            profile = Profile(id=profile_id, balance=100, rank="bronze")
            db.session.add(profile)
            db.session.commit()

            initial_balance = profile.balance

            PointService.add_points(profile_id)
            PointService.add_points(profile_id)
            PointService.add_points(profile_id)

            profile = Profile.query.get(profile_id)
            assert profile.balance == initial_balance + (67 * 3)
            assert PointTransaction.query.filter_by(
                account_id=profile_id
            ).count() == 3


class TestOfferService:
    """Test OfferService."""

    def test_redeem_offer_success(self, app):
        """Test successfully redeeming an offer."""
        with app.app_context():
            # Setup
            profile_id = uuid4()
            profile = Profile(id=profile_id, balance=500, rank="bronze")
            card = Card(
                id=profile_id,
                nfc_id="TEST123",
                expiry_date=datetime.now()
            )
            offer = OfferModel(
                name="Test Offer",
                price=100,
                price_type=PriceType.Points,
                reward_type=RewardType.CardRenew,
                valid_until=datetime.now() + timedelta(days=30),
                is_active=True
            )
            db.session.add_all([profile, card, offer])
            db.session.commit()

            initial_balance = profile.balance
            initial_expiry = card.expiry_date

            result = OfferService.redeem_offer(offer.id, profile_id)

            assert result is True

            # Verify balance decreased
            profile = Profile.query.get(profile_id)
            assert profile.balance == initial_balance - offer.price

            # Verify card expiry extended
            card = Card.query.get(profile_id)
            expected_expiry = initial_expiry + timedelta(days=30)
            assert card.expiry_date.date() == expected_expiry.date()

    def test_redeem_offer_creates_redemption_record(self, app):
        """Test that redemption creates a record."""
        with app.app_context():
            profile_id = uuid4()
            profile = Profile(id=profile_id, balance=500, rank="bronze")
            card = Card(
                id=profile_id,
                nfc_id="TEST123",
                expiry_date=datetime.now() + timedelta(days=30)
            )
            offer = OfferModel(
                name="Test Offer",
                price=100,
                price_type=PriceType.Points,
                reward_type=RewardType.CardRenew,
                valid_until=datetime.now() + timedelta(days=30),
                is_active=True
            )
            db.session.add_all([profile, card, offer])
            db.session.commit()

            OfferService.redeem_offer(offer.id, profile_id)

            redemption = RedemptionModel.query.filter_by(
                profile_id=profile_id
            ).first()
            assert redemption is not None
            assert redemption.offer_id == offer.id
            assert redemption.points_cost == offer.price

    def test_redeem_nonexistent_offer(self, app):
        """Test redeeming non-existent offer raises error."""
        with app.app_context():
            profile_id = uuid4()
            with pytest.raises(InvalidOffer):
                OfferService.redeem_offer(999, profile_id)

    def test_redeem_offer_nonexistent_profile(self, app):
        """Test redeeming offer for non-existent profile raises error."""
        with app.app_context():
            offer = OfferModel(
                name="Test",
                price=100,
                price_type=PriceType.Points,
                reward_type=RewardType.CardRenew,
                valid_until=datetime.now() + timedelta(days=30),
                is_active=True
            )
            db.session.add(offer)
            db.session.commit()

            fake_id = uuid4()
            with pytest.raises(ProfileNotFound):
                OfferService.redeem_offer(offer.id, fake_id)

    def test_redeem_offer_insufficient_funds(self, app):
        """Test redeeming offer with insufficient funds raises error."""
        with app.app_context():
            # Create profile with low balance
            profile_id = uuid4()
            profile = Profile(id=profile_id, balance=50, rank="bronze")
            card = Card(
                id=profile_id,
                nfc_id="TEST123",
                expiry_date=datetime.now() + timedelta(days=30)
            )
            offer = OfferModel(
                name="Expensive Offer",
                price=100,
                price_type=PriceType.Points,
                reward_type=RewardType.CardRenew,
                valid_until=datetime.now() + timedelta(days=30),
                is_active=True
            )
            db.session.add_all([profile, card, offer])
            db.session.commit()

            # Offer costs 100 points
            with pytest.raises(InsufficientFunds):
                OfferService.redeem_offer(offer.id, profile_id)

    def test_redeem_offer_no_card(self, app):
        """Test redeeming offer when profile has no card."""
        with app.app_context():
            # Create profile without card
            profile_id = uuid4()
            profile = Profile(id=profile_id, balance=500, rank="gold")
            offer = OfferModel(
                name="Test",
                price=100,
                price_type=PriceType.Points,
                reward_type=RewardType.CardRenew,
                valid_until=datetime.now() + timedelta(days=30),
                is_active=True
            )
            db.session.add_all([profile, offer])
            db.session.commit()

            with pytest.raises(CardNotFound):
                OfferService.redeem_offer(offer.id, profile_id)

    def test_redeem_offer_multiple_times(self, app):
        """Test redeeming same offer multiple times."""
        with app.app_context():
            profile_id = uuid4()
            profile = Profile(id=profile_id, balance=500, rank="bronze")
            card = Card(
                id=profile_id,
                nfc_id="TEST123",
                expiry_date=datetime.now() + timedelta(days=30)
            )
            offer = OfferModel(
                name="Test Offer",
                price=100,
                price_type=PriceType.Points,
                reward_type=RewardType.CardRenew,
                valid_until=datetime.now() + timedelta(days=30),
                is_active=True
            )
            db.session.add_all([profile, card, offer])
            db.session.commit()

            OfferService.redeem_offer(offer.id, profile_id)

            # Refresh and redeem again
            db.session.refresh(profile)
            OfferService.redeem_offer(offer.id, profile_id)

            profile = Profile.query.get(profile_id)
            assert profile.balance == 500 - (offer.price * 2)

            redemptions = RedemptionModel.query.filter_by(
                profile_id=profile_id
            ).all()
            assert len(redemptions) == 2

    def test_redeem_experience_offer(self, app):
        """Test redeeming an experience-type offer."""
        with app.app_context():
            profile_id = uuid4()
            profile = Profile(id=profile_id, balance=500, rank="bronze")
            card = Card(
                id=profile_id,
                nfc_id="TEST123",
                expiry_date=datetime.now() + timedelta(days=30)
            )
            # Create experience offer
            offer = OfferModel(
                name="Experience Offer",
                price=100,
                price_type=PriceType.Experience,
                reward_type=RewardType.CardSkin,
                valid_until=datetime.now() + timedelta(days=30),
                is_active=True
            )
            db.session.add_all([profile, card, offer])
            db.session.commit()

            initial_balance = profile.balance

            # Should succeed (no special handling for Experience type shown)
            result = OfferService.redeem_offer(offer.id, profile_id)
            assert result is True
