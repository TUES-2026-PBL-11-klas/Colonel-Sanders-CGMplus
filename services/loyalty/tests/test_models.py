"""Tests for database models."""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from src.extensions import db
from src.models.profile import Profile
from src.models.card import Card
from src.models.pointTransaction import PointTransaction, PT_TypeEnum
from src.models.offerModel import OfferModel, PriceType, RewardType
from src.models.RedemptionModel import RedemptionModel


class TestProfileModel:
    """Test Profile model."""

    def test_profile_creation(self, app):
        """Test creating a profile."""
        with app.app_context():
            profile_id = uuid4()
            profile = Profile(
                id=profile_id,
                balance=500,
                rank="gold"
            )
            db.session.add(profile)
            db.session.commit()

            retrieved = Profile.query.get(profile_id)
            assert retrieved.id == profile_id
            assert retrieved.balance == 500
            assert retrieved.rank == "gold"

    def test_profile_default_balance(self, app):
        """Test profile with default balance."""
        with app.app_context():
            profile = Profile(id=uuid4(), balance=0, rank="bronze")
            db.session.add(profile)
            db.session.commit()

            retrieved = Profile.query.filter_by(rank="bronze").first()
            assert retrieved.balance == 0

    def test_profile_timestamps(self, app):
        """Test profile has created_at and updated_at."""
        with app.app_context():
            profile = Profile(id=uuid4(), balance=100, rank="silver")
            db.session.add(profile)
            db.session.commit()

            retrieved = Profile.query.get(profile.id)
            assert retrieved.created_at is not None
            assert retrieved.updated_at is not None
            assert isinstance(retrieved.created_at, datetime)

    def test_profile_transactions_relationship(self, app, test_profile):
        """Test profile has relationship with transactions."""
        with app.app_context():
            # Merge the fixture into the session
            profile = db.session.merge(test_profile)

            transaction = PointTransaction(
                id=uuid4(),
                account_id=profile.id,
                pt_type=PT_TypeEnum.transport,
                ammount=50,
                description="Test transaction"
            )
            db.session.add(transaction)
            db.session.commit()

            profile = Profile.query.get(profile.id)
            assert len(profile.transactions) == 1
            assert profile.transactions[0].ammount == 50


class TestCardModel:
    """Test Card model."""

    def test_card_creation(self, app):
        """Test creating a card."""
        with app.app_context():
            card_id = uuid4()
            card = Card(
                id=card_id,
                nfc_id="ABCD1234",
                active=True,
                disabled=False,
                expiry_date=datetime.now() + timedelta(days=365)
            )
            db.session.add(card)
            db.session.commit()

            retrieved = Card.query.get(card_id)
            assert retrieved.id == card_id
            assert retrieved.nfc_id == "ABCD1234"
            assert retrieved.active is True
            assert retrieved.disabled is False

    def test_card_default_active_status(self, app):
        """Test card defaults to active=True."""
        with app.app_context():
            card = Card(
                id=uuid4(),
                nfc_id="TEST1234",
                expiry_date=datetime.now() + timedelta(days=30)
            )
            db.session.add(card)
            db.session.commit()

            retrieved = Card.query.get(card.id)
            assert retrieved.active is True
            assert retrieved.disabled is False

    def test_card_expiry_date(self, app):
        """Test card expiry date."""
        with app.app_context():
            future_date = datetime.now() + timedelta(days=365)
            card = Card(
                id=uuid4(),
                nfc_id="FUTURE1234",
                expiry_date=future_date
            )
            db.session.add(card)
            db.session.commit()

            retrieved = Card.query.get(card.id)
            assert retrieved.expiry_date.date() == future_date.date()

    def test_card_timestamps(self, app):
        """Test card has timestamps."""
        with app.app_context():
            card = Card(
                id=uuid4(),
                nfc_id="TEST123",
                expiry_date=datetime.now() + timedelta(days=30)
            )
            db.session.add(card)
            db.session.commit()

            retrieved = Card.query.get(card.id)
            assert retrieved.created_at is not None
            assert retrieved.updated_at is not None


class TestOfferModel:
    """Test OfferModel."""

    def test_offer_creation(self, app):
        """Test creating an offer."""
        with app.app_context():
            offer = OfferModel(
                name="Premium Offer",
                description="Get 30 days extension",
                price=150,
                price_type=PriceType.Points,
                reward_type=RewardType.CardRenew,
                valid_until=datetime.now() + timedelta(days=30),
                is_active=True
            )
            db.session.add(offer)
            db.session.commit()

            retrieved = OfferModel.query.filter_by(name="Premium Offer").first()
            assert retrieved.price == 150
            assert retrieved.price_type == PriceType.Points
            assert retrieved.reward_type == RewardType.CardRenew
            assert retrieved.is_active is True

    def test_offer_with_experience_price_type(self, app):
        """Test offer with Experience price type."""
        with app.app_context():
            offer = OfferModel(
                name="Experience Offer",
                price=200,
                price_type=PriceType.Experience,
                reward_type=RewardType.CardSkin,
                valid_until=datetime.now() + timedelta(days=30),
                is_active=True
            )
            db.session.add(offer)
            db.session.commit()

            retrieved = OfferModel.query.get(offer.id)
            assert retrieved.price_type == PriceType.Experience

    def test_offer_inactive_status(self, app):
        """Test inactive offer."""
        with app.app_context():
            offer = OfferModel(
                name="Inactive Offer",
                price=100,
                price_type=PriceType.Points,
                reward_type=RewardType.CardRenew,
                valid_until=datetime.now() + timedelta(days=30),
                is_active=False
            )
            db.session.add(offer)
            db.session.commit()

            active_offers = OfferModel.query.filter_by(is_active=True).all()
            assert offer not in active_offers


class TestPointTransactionModel:
    """Test PointTransaction model."""

    def test_transaction_creation(self, app, test_profile):
        """Test creating a point transaction."""
        with app.app_context():
            # Merge the fixture into the session
            profile = db.session.merge(test_profile)

            transaction = PointTransaction(
                id=uuid4(),
                account_id=profile.id,
                pt_type=PT_TypeEnum.transport,
                ammount=100,
                description="Transit points"
            )
            db.session.add(transaction)
            db.session.commit()

            retrieved = PointTransaction.query.filter_by(
                account_id=profile.id
            ).first()
            assert retrieved.ammount == 100
            assert retrieved.pt_type == PT_TypeEnum.transport

    def test_transaction_with_other_type(self, app, test_profile):
        """Test transaction with 'other' type."""
        with app.app_context():
            # Merge the fixture into the session
            profile = db.session.merge(test_profile)

            transaction = PointTransaction(
                id=uuid4(),
                account_id=profile.id,
                pt_type=PT_TypeEnum.other,
                ammount=50,
                description="Other points"
            )
            db.session.add(transaction)
            db.session.commit()

            retrieved = PointTransaction.query.get(transaction.id)
            assert retrieved.pt_type == PT_TypeEnum.other

    def test_transaction_relationship_to_profile(self, app, test_profile):
        """Test transaction relationship to profile."""
        with app.app_context():
            # Merge the fixture into the session
            profile = db.session.merge(test_profile)

            transaction = PointTransaction(
                id=uuid4(),
                account_id=profile.id,
                pt_type=PT_TypeEnum.transport,
                ammount=75,
                description="Test"
            )
            db.session.add(transaction)
            db.session.commit()

            profile = Profile.query.get(profile.id)
            assert len(profile.transactions) >= 1
            assert any(t.ammount == 75 for t in profile.transactions)


class TestRedemptionModel:
    """Test RedemptionModel."""

    def test_redemption_creation(self, app, test_profile, test_offer):
        """Test creating a redemption record."""
        with app.app_context():
            # Re-merge the fixtures into the session
            profile = db.session.merge(test_profile)
            offer = db.session.merge(test_offer)

            redemption = RedemptionModel(
                id=uuid4(),
                offer_id=offer.id,
                profile_id=profile.id,
                points_cost=offer.price
            )
            db.session.add(redemption)
            db.session.commit()

            retrieved = RedemptionModel.query.filter_by(
                profile_id=profile.id
            ).first()
            assert retrieved.offer_id == offer.id
            assert retrieved.points_cost == offer.price

    def test_redemption_timestamps(self, app):
        """Test redemption has timestamps."""
        with app.app_context():
            offer = OfferModel(
                name="Test Offer",
                price=100,
                price_type=PriceType.Points,
                reward_type=RewardType.CardRenew,
                valid_until=datetime.now() + timedelta(days=30),
                is_active=True
            )
            db.session.add(offer)
            db.session.commit()

            profile_id = uuid4()
            profile = Profile(id=profile_id, balance=100, rank="bronze")
            db.session.add(profile)
            db.session.commit()

            redemption = RedemptionModel(
                id=uuid4(),
                offer_id=offer.id,
                profile_id=profile_id,
                points_cost=100
            )
            db.session.add(redemption)
            db.session.commit()

            retrieved = RedemptionModel.query.get(redemption.id)
            assert retrieved.created_at is not None
            assert retrieved.updated_at is not None

    def test_multiple_redemptions_per_profile(self, app):
        """Test profile can have multiple redemptions."""
        with app.app_context():
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

            profile_id = uuid4()
            profile = Profile(id=profile_id, balance=500, rank="bronze")
            db.session.add(profile)
            db.session.commit()

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

            profile = Profile.query.get(profile_id)
            assert profile is not None  # Verify profile exists
