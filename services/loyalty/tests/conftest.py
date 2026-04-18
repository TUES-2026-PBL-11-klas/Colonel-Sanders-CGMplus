"""Shared fixtures and configuration for tests."""
import pytest
import os
from datetime import datetime, timedelta
from uuid import uuid4
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token

# Set environment variables before importing app
os.environ["JWT_SECRET"] = "test-secret-key-do-not-use-in-production"
os.environ["DB_URL"] = "sqlite:///:memory:"

from src.app import create_app
from src.extensions import db
from src.models.profile import Profile
from src.models.card import Card
from src.models.pointTransaction import PointTransaction, PT_TypeEnum
from src.models.offerModel import OfferModel, PriceType, RewardType
from src.models.RedemptionModel import RedemptionModel


@pytest.fixture(scope="function")
def app():
    """Create and configure test app."""
    app = create_app()
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "test-secret-key"

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def auth_headers(app):
    """Generate JWT authorization headers."""
    with app.app_context():
        access_token = create_access_token(identity="test-user")
        return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def test_profile(app):
    """Create a test profile."""
    with app.app_context():
        profile_id = uuid4()
        profile = Profile(
            id=profile_id,
            balance=1000,
            rank="bronze"
        )
        db.session.add(profile)
        db.session.commit()
        db.session.expunge(profile)
    return profile


@pytest.fixture
def test_card(app, test_profile):
    """Create a test card."""
    with app.app_context():
        # Merge the test_profile into the session
        profile = db.session.merge(test_profile)

        card = Card(
            id=profile.id,
            nfc_id="1234567890ABCDEF",
            active=True,
            disabled=False,
            expiry_date=datetime.now() + timedelta(days=365)
        )
        db.session.add(card)
        db.session.commit()
        db.session.expunge(card)
    return card


@pytest.fixture
def test_offer(app):
    """Create a test offer."""
    with app.app_context():
        offer = OfferModel(
            name="30 Days Extension",
            description="Extend your card validity by 30 days",
            price=100,
            price_type=PriceType.Points,
            reward_type=RewardType.CardRenew,
            valid_until=datetime.now() + timedelta(days=30),
            is_active=True
        )
        db.session.add(offer)
        db.session.commit()
        db.session.expunge(offer)
    return offer


@pytest.fixture
def test_point_transaction(app, test_profile):
    """Create a test point transaction."""
    with app.app_context():
        transaction = PointTransaction(
            id=uuid4(),
            account_id=test_profile.id,
            pt_type=PT_TypeEnum.transport,
            ammount=67,
            description="67 earned by using the transportation"
        )
        db.session.add(transaction)
        db.session.commit()
        db.session.expunge(transaction)
    return transaction


@pytest.fixture
def test_redemption(app, test_profile, test_offer):
    """Create a test redemption."""
    with app.app_context():
        redemption = RedemptionModel(
            id=uuid4(),
            offer_id=test_offer.id,
            profile_id=test_profile.id,
            points_cost=test_offer.price
        )
        db.session.add(redemption)
        db.session.commit()
        db.session.expunge(redemption)
    return redemption
