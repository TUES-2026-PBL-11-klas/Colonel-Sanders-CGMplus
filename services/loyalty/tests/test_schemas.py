"""Tests for schemas."""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from marshmallow import ValidationError
from src.schemas.profileSchema import ProfileSchema, CardSchema
from src.schemas.offersSchema import OfferSchema
from src.schemas.RedemptionSchema import RedemptionSchema
from src.schemas.internalSchema import CreateProfileSchema


class TestProfileSchema:
    """Test ProfileSchema validation."""

    def test_profile_schema_valid(self):
        """Test valid profile data."""
        schema = ProfileSchema()
        data = {"balance": 100, "rank": "gold"}
        result = schema.load(data)

        assert result["balance"] == 100
        assert result["rank"] == "gold"

    def test_profile_schema_missing_points(self):
        """Test missing required balance field."""
        schema = ProfileSchema()
        data = {"rank": "gold"}

        with pytest.raises(ValidationError) as exc:
            schema.load(data)

        assert "balance" in exc.value.messages

    def test_profile_schema_missing_rank(self):
        """Test missing required rank field."""
        schema = ProfileSchema()
        data = {"balance": 100}

        with pytest.raises(ValidationError) as exc:
            schema.load(data)

        assert "rank" in exc.value.messages

    def test_profile_schema_invalid_points_type(self):
        """Test invalid balance type."""
        schema = ProfileSchema()
        data = {"balance": "not an int", "rank": "gold"}

        with pytest.raises(ValidationError) as exc:
            schema.load(data)

        assert "balance" in exc.value.messages

    def test_profile_schema_dump(self):
        """Test dumping profile data."""
        schema = ProfileSchema()
        data = {"balance": 250, "rank": "silver"}
        result = schema.dump(data)

        assert result["balance"] == 250
        assert result["rank"] == "silver"


class TestCardSchema:
    """Test CardSchema validation."""

    def test_card_schema_valid(self):
        """Test valid card data."""
        schema = CardSchema()
        expiry = datetime.now() + timedelta(days=30)
        data = {
            "nfc_id": "1234567890ABCDEF",
            "active": True,
            "disabled": False,
            "expiry_date": expiry.isoformat()
        }
        result = schema.load(data)

        assert result["nfc_id"] == "1234567890ABCDEF"
        assert result["active"] is True
        assert result["disabled"] is False

    def test_card_schema_partial(self):
        """Test card schema with optional fields."""
        schema = CardSchema()
        data = {"nfc_id": "TEST123"}
        result = schema.load(data)

        assert result["nfc_id"] == "TEST123"

    def test_card_schema_empty(self):
        """Test empty card schema."""
        schema = CardSchema()
        data = {}
        result = schema.load(data)

        assert result == {}

    def test_card_schema_invalid_active(self):
        """Test invalid active field type."""
        schema = CardSchema()
        data = {"active": "not a bool"}

        with pytest.raises(ValidationError) as exc:
            schema.load(data)

    def test_card_schema_dump(self):
        """Test dumping card data."""
        schema = CardSchema()
        expiry = datetime.now()
        data = {
            "nfc_id": "ABC123",
            "active": False,
            "disabled": True,
            "expiry_date": expiry
        }
        result = schema.dump(data)

        assert result["nfc_id"] == "ABC123"
        assert result["active"] is False


class TestOfferSchema:
    """Test OfferSchema validation."""

    def test_offer_schema_valid(self):
        """Test valid offer data."""
        schema = OfferSchema()
        data = {
            "id": 1,
            "name": "Premium Offer",
            "description": "30 days extension",
            "price": 100
        }
        result = schema.load(data)

        assert result["id"] == 1
        assert result["name"] == "Premium Offer"
        assert result["price"] == 100

    def test_offer_schema_missing_id(self):
        """Test missing required id field."""
        schema = OfferSchema()
        data = {
            "name": "Offer",
            "price": 100
        }

        with pytest.raises(ValidationError) as exc:
            schema.load(data)

        assert "id" in exc.value.messages

    def test_offer_schema_missing_name(self):
        """Test missing required name field."""
        schema = OfferSchema()
        data = {
            "id": 1,
            "price": 100
        }

        with pytest.raises(ValidationError) as exc:
            schema.load(data)

        assert "name" in exc.value.messages

    def test_offer_schema_missing_price(self):
        """Test missing required price field."""
        schema = OfferSchema()
        data = {
            "id": 1,
            "name": "Offer"
        }

        with pytest.raises(ValidationError) as exc:
            schema.load(data)

        assert "price" in exc.value.messages

    def test_offer_schema_optional_description(self):
        """Test offer without description."""
        schema = OfferSchema()
        data = {
            "id": 1,
            "name": "Offer",
            "price": 100
        }
        result = schema.load(data)

        assert "description" not in result or result.get("description") is None

    def test_offer_schema_invalid_price_type(self):
        """Test invalid price type."""
        schema = OfferSchema()
        data = {
            "id": 1,
            "name": "Offer",
            "price": "not an int"
        }

        with pytest.raises(ValidationError) as exc:
            schema.load(data)

    def test_offer_schema_dump(self):
        """Test dumping offer data."""
        schema = OfferSchema()
        data = {
            "id": 5,
            "name": "Test Offer",
            "description": "Test",
            "price": 250
        }
        result = schema.dump(data)

        assert result["id"] == 5
        assert result["name"] == "Test Offer"
        assert result["price"] == 250


class TestRedemptionSchema:
    """Test RedemptionSchema validation."""

    def test_redemption_schema_valid(self):
        """Test valid redemption data."""
        schema = RedemptionSchema()
        profile_id = uuid4()
        data = {
            "offer_id": 1,
            "profile_id": str(profile_id),
            "points_cost": 100
        }
        result = schema.load(data)

        assert "offer_id" in result
        assert "profile_id" in result
        assert result["points_cost"] == 100

    def test_redemption_schema_missing_offer_id(self):
        """Test missing offer_id field."""
        schema = RedemptionSchema()
        profile_id = uuid4()
        data = {
            "profile_id": str(profile_id),
            "points_cost": 100
        }

        with pytest.raises(ValidationError) as exc:
            schema.load(data)

        assert "offer_id" in exc.value.messages

    def test_redemption_schema_missing_profile_id(self):
        """Test missing profile_id field."""
        schema = RedemptionSchema()
        data = {
            "offer_id": 1,
            "points_cost": 100
        }

        with pytest.raises(ValidationError) as exc:
            schema.load(data)

        assert "profile_id" in exc.value.messages

    def test_redemption_schema_invalid_offer_id(self):
        """Test invalid offer_id type."""
        schema = RedemptionSchema()
        profile_id = uuid4()
        data = {
            "offer_id": "not an int",
            "profile_id": str(profile_id),
            "points_cost": 100
        }

        with pytest.raises(ValidationError) as exc:
            schema.load(data)


class TestCreateProfileSchema:
    """Test CreateProfileSchema validation."""

    def test_create_profile_schema_valid(self):
        """Test valid create profile data."""
        schema = CreateProfileSchema()
        profile_id = uuid4()
        data = {"uuid": profile_id}
        result = schema.load(data)

        assert "uuid" in result
        assert result["uuid"] == profile_id

    def test_create_profile_schema_valid_string_uuid(self):
        """Test valid string UUID."""
        schema = CreateProfileSchema()
        profile_id_str = str(uuid4())
        data = {"uuid": profile_id_str}
        result = schema.load(data)

        assert "uuid" in result

    def test_create_profile_schema_missing_uuid(self):
        """Test missing uuid field."""
        schema = CreateProfileSchema()
        data = {}

        with pytest.raises(ValidationError) as exc:
            schema.load(data)

        assert "uuid" in exc.value.messages

    def test_create_profile_schema_invalid_uuid(self):
        """Test invalid UUID format."""
        schema = CreateProfileSchema()
        data = {"uuid": "not-a-uuid"}

        with pytest.raises(ValidationError) as exc:
            schema.load(data)

        assert "uuid" in exc.value.messages

    def test_create_profile_schema_dump(self):
        """Test dumping create profile data."""
        schema = CreateProfileSchema()
        profile_id = uuid4()
        data = {"uuid": profile_id}
        result = schema.dump(data)

        assert str(result["uuid"]) == str(profile_id)
