"""Tests for API routes."""
import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from src.extensions import db
from src.models.profile import Profile
from src.models.card import Card
from src.models.offerModel import OfferModel, PriceType, RewardType
from src.models.RedemptionModel import RedemptionModel


class TestProfileRoutes:
    """Test profile endpoints."""

    def test_get_profile_me_success(self, client, auth_headers, app):
        """Test GET /profile/me returns profile data."""
        with app.app_context():
            from uuid import uuid4
            from src.models.profile import Profile
            from src.extensions import db

            profile_id = uuid4()
            profile = Profile(id=profile_id, balance=500, rank="gold")
            db.session.add(profile)
            db.session.commit()

            from flask_jwt_extended import create_access_token
            token = create_access_token(identity=str(profile_id))
            headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/profile/me",
            headers=headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "balance" in data
        assert "rank" in data
        assert data["rank"] == "gold"

    def test_get_profile_me_no_auth(self, client, test_profile):
        """Test GET /profile/me without auth returns 401."""
        response = client.get("/api/v1/profile/me")

        assert response.status_code == 401

    def test_get_profile_me_nonexistent_profile(self, client, app, auth_headers):
        """Test GET /profile/me for non-existent profile returns 404."""
        # Create auth headers with non-existent profile ID
        from flask_jwt_extended import create_access_token
        fake_id = str(uuid4())
        with app.app_context():
            token = create_access_token(identity=fake_id)
            headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/profile/me",
            headers=headers
        )

        assert response.status_code == 404

    def test_get_card_success(self, client, app):
        """Test GET /profile/card returns card data."""
        with app.app_context():
            from uuid import uuid4
            from datetime import datetime, timedelta
            from src.models.profile import Profile
            from src.models.card import Card
            from src.extensions import db

            profile_id = uuid4()
            profile = Profile(id=profile_id, balance=500, rank="gold")
            card = Card(
                id=profile_id,
                nfc_id="TESTCARD123",
                active=True,
                disabled=False,
                expiry_date=datetime.now() + timedelta(days=30)
            )
            db.session.add_all([profile, card])
            db.session.commit()

            from flask_jwt_extended import create_access_token
            token = create_access_token(identity=str(profile_id))
            headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/profile/card",
            headers=headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "nfc_id" in data
        assert "active" in data
        assert "disabled" in data
        assert "expiry_date" in data
        assert data["nfc_id"] == "TESTCARD123"
        assert data["active"] is True

    def test_get_card_no_auth(self, client):
        """Test GET /profile/card without auth returns 401."""
        response = client.get("/api/v1/profile/card")

        assert response.status_code == 401

    def test_get_card_nonexistent_card(self, client, app, auth_headers):
        """Test GET /profile/card for non-existent card returns 404."""
        from flask_jwt_extended import create_access_token
        fake_id = str(uuid4())
        with app.app_context():
            token = create_access_token(identity=fake_id)
            headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/profile/card",
            headers=headers
        )

        assert response.status_code == 404


class TestOfferRoutes:
    """Test offers endpoints."""

    def test_get_offers_success(self, client, auth_headers, app):
        """Test GET /offers/ returns list of active offers."""
        with app.app_context():
            from datetime import datetime, timedelta
            from src.models.offerModel import OfferModel, PriceType, RewardType
            from src.extensions import db

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

        response = client.get(
            "/api/v1/offers/",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_get_offers_no_auth(self, client):
        """Test GET /offers/ without auth returns 401."""
        response = client.get("/api/v1/offers/")

        assert response.status_code == 401

    @pytest.fixture
    def test_redeem_offer_success(
        self, client, auth_headers, app, test_profile, test_card, test_offer
    ):
        """Test POST /offers/<id>/redemption successfully redeems offer."""
        with app.app_context():
            initial_balance = test_profile.balance

        response = client.post(
            f"/api/v1/offers/{test_offer.id}/redemption",
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["status"] == "completed"

        # Verify balance was deducted
        with app.app_context():
            profile = Profile.query.get(test_profile.id)
            assert profile.balance == initial_balance - test_offer.price

    def test_redeem_offer_no_auth(self, client, app):
        """Test redeeming offer without auth returns 401."""
        with app.app_context():
            from datetime import datetime, timedelta
            from src.models.offerModel import OfferModel, PriceType, RewardType
            from src.extensions import db

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
            offer_id = offer.id

        response = client.post(f"/api/v1/offers/{offer_id}/redemption")

        assert response.status_code == 401

    def test_redeem_offer_insufficient_funds(self, client, app):
        """Test redeeming offer with insufficient funds returns 402."""
        with app.app_context():
            from uuid import uuid4
            from datetime import datetime, timedelta
            from src.models.profile import Profile
            from src.models.card import Card
            from src.models.offerModel import OfferModel, PriceType, RewardType
            from src.extensions import db
            from flask_jwt_extended import create_access_token

            # Create profile with low balance
            profile_id = uuid4()
            profile = Profile(id=profile_id, balance=10, rank="bronze")
            card = Card(
                id=profile_id,
                nfc_id="TEST123",
                expiry_date=datetime.now() + timedelta(days=30)
            )
            offer = OfferModel(
                name="Expensive Offer",
                price=500,
                price_type=PriceType.Points,
                reward_type=RewardType.CardRenew,
                valid_until=datetime.now() + timedelta(days=30),
                is_active=True
            )
            db.session.add_all([profile, card, offer])
            db.session.commit()

            # Create auth token for this profile
            token = create_access_token(identity=str(profile_id))
            headers = {"Authorization": f"Bearer {token}"}
            offer_id = offer.id

        response = client.post(
            f"/api/v1/offers/{offer_id}/redemption",
            headers=headers
        )

        assert response.status_code == 402
        data = response.get_json()
        assert "error" in data

    def test_redeem_nonexistent_offer(self, client, app):
        """Test redeeming non-existent offer returns 500."""
        with app.app_context():
            from uuid import uuid4
            from src.models.profile import Profile
            from src.extensions import db
            from flask_jwt_extended import create_access_token

            profile_id = uuid4()
            profile = Profile(id=profile_id, balance=100, rank="bronze")
            db.session.add(profile)
            db.session.commit()

            token = create_access_token(identity=str(profile_id))
            headers = {"Authorization": f"Bearer {token}"}

        response = client.post(
            "/api/v1/offers/999/redemption",
            headers=headers
        )

        assert response.status_code == 500

    def test_get_redemptions_success(self, client, auth_headers, app):
        """Test GET /offers/redemptions returns user's redemptions."""
        with app.app_context():
            from uuid import uuid4
            from datetime import datetime, timedelta
            from src.models.profile import Profile
            from src.models.card import Card
            from src.models.offerModel import OfferModel, PriceType, RewardType
            from src.services.OfferService import OfferService
            from src.extensions import db
            from flask_jwt_extended import create_access_token

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

            # Redeem an offer
            OfferService.redeem_offer(offer.id, profile_id)

            # Create auth token for this profile
            token = create_access_token(identity=str(profile_id))
            headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/offers/redemptions",
            headers=headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_redemptions_no_auth(self, client):
        """Test GET /offers/redemptions without auth returns 401."""
        response = client.get("/api/v1/offers/redemptions")

        assert response.status_code == 401

    def test_get_redemptions_empty(self, client, app):
        """Test GET /offers/redemptions for user with no redemptions."""
        with app.app_context():
            from uuid import uuid4
            from src.models.profile import Profile
            from src.extensions import db
            from flask_jwt_extended import create_access_token

            profile_id = uuid4()
            profile = Profile(id=profile_id, balance=100, rank="bronze")
            db.session.add(profile)
            db.session.commit()

            token = create_access_token(identity=str(profile_id))
            headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/offers/redemptions",
            headers=headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        # Should be empty since profile hasn't redeemed anything
        assert len(data) == 0


class TestInternalRoutes:
    """Test internal endpoints."""

    def test_add_points_success(self, client, app):
        """Test PATCH /internal/<id>/points adds points."""
        with app.app_context():
            from uuid import uuid4
            from src.models.profile import Profile
            from src.extensions import db

            profile_id = uuid4()
            profile = Profile(id=profile_id, balance=100, rank="bronze")
            db.session.add(profile)
            db.session.commit()

            initial_balance = profile.balance

        response = client.patch(f"/internal/{profile_id}/points")

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] is True

        # Verify points were added
        with app.app_context():
            profile = Profile.query.get(profile_id)
            assert profile.balance == initial_balance + 67

    def test_add_points_invalid_uuid(self, client):
        """Test PATCH /internal/<id>/points with invalid UUID returns 400."""
        response = client.patch("/internal/not-a-uuid/points")

        assert response.status_code == 400

    def test_add_points_nonexistent_profile(self, client):
        """Test PATCH /internal/<id>/points for non-existent profile."""
        from uuid import uuid4
        fake_id = uuid4()
        response = client.patch(f"/internal/{fake_id}/points")

        # Should return 500 due to ProfileNotFound exception
        assert response.status_code == 500

    def test_create_profile_invalid_uuid(self, client):
        """Test POST /internal/profile with invalid UUID returns 422."""
        response = client.post(
            "/internal/profile",
            json={"uuid": "not-a-uuid"},
            content_type="application/json"
        )

        assert response.status_code == 422

    def test_create_profile_missing_uuid(self, client):
        """Test POST /internal/profile without uuid returns 422."""
        response = client.post(
            "/internal/profile",
            json={},
            content_type="application/json"
        )

        assert response.status_code == 422

    def test_create_profile_duplicate(self, client, app):
        """Test creating profile with existing UUID fails."""
        with app.app_context():
            from uuid import uuid4
            from src.models.profile import Profile
            from src.extensions import db

            profile_id = uuid4()
            profile = Profile(id=profile_id, balance=0, rank="bronze")
            db.session.add(profile)
            db.session.commit()

        response = client.post(
            "/internal/profile",
            json={"uuid": str(profile_id)},
            content_type="application/json"
        )

        # Should return 500 due to duplicate key
        assert response.status_code == 500
