"""Tests for exceptions."""
import pytest
from src.exceptions.OfferExceptions import InsufficientFunds, InvalidOffer
from src.exceptions.ProfileExceptions import ProfileNotFound, CardNotFound


class TestOfferExceptions:
    """Test offer-related exceptions."""

    def test_insufficient_funds_exception(self):
        """Test InsufficientFunds exception can be raised."""
        with pytest.raises(InsufficientFunds):
            raise InsufficientFunds()

    def test_insufficient_funds_with_message(self):
        """Test InsufficientFunds exception with message."""
        message = "Not enough points to redeem this offer"
        with pytest.raises(InsufficientFunds) as exc:
            raise InsufficientFunds(message)

        assert str(exc.value) == message

    def test_invalid_offer_exception(self):
        """Test InvalidOffer exception can be raised."""
        with pytest.raises(InvalidOffer):
            raise InvalidOffer()

    def test_invalid_offer_with_message(self):
        """Test InvalidOffer exception with message."""
        message = "Offer with id 999 not found"
        with pytest.raises(InvalidOffer) as exc:
            raise InvalidOffer(message)

        assert str(exc.value) == message

    def test_offer_exceptions_are_exceptions(self):
        """Test that offer exceptions inherit from Exception."""
        assert issubclass(InsufficientFunds, Exception)
        assert issubclass(InvalidOffer, Exception)

    def test_catch_insufficient_funds(self):
        """Test catching InsufficientFunds exception."""
        caught = False
        try:
            raise InsufficientFunds("Test message")
        except InsufficientFunds as e:
            caught = True
            assert "Test message" in str(e)

        assert caught is True

    def test_catch_invalid_offer(self):
        """Test catching InvalidOffer exception."""
        caught = False
        try:
            raise InvalidOffer("Test offer not found")
        except InvalidOffer as e:
            caught = True
            assert "not found" in str(e)

        assert caught is True

    def test_multiple_exception_types(self):
        """Test handling multiple exception types."""
        exceptions_to_test = [
            (InsufficientFunds, "funds"),
            (InvalidOffer, "offer")
        ]

        for exc_class, keyword in exceptions_to_test:
            caught = False
            try:
                raise exc_class(keyword)
            except exc_class:
                caught = True

            assert caught is True


class TestProfileExceptions:
    """Test profile-related exceptions."""

    def test_profile_not_found_exception(self):
        """Test ProfileNotFound exception can be raised."""
        with pytest.raises(ProfileNotFound):
            raise ProfileNotFound()

    def test_profile_not_found_with_message(self):
        """Test ProfileNotFound exception with message."""
        message = "Profile with id abc123 not found"
        with pytest.raises(ProfileNotFound) as exc:
            raise ProfileNotFound(message)

        assert str(exc.value) == message

    def test_card_not_found_exception(self):
        """Test CardNotFound exception can be raised."""
        with pytest.raises(CardNotFound):
            raise CardNotFound()

    def test_card_not_found_with_message(self):
        """Test CardNotFound exception with message."""
        message = "Card for profile xyz789 not found"
        with pytest.raises(CardNotFound) as exc:
            raise CardNotFound(message)

        assert str(exc.value) == message

    def test_profile_exceptions_are_exceptions(self):
        """Test that profile exceptions inherit from Exception."""
        assert issubclass(ProfileNotFound, Exception)
        assert issubclass(CardNotFound, Exception)

    def test_catch_profile_not_found(self):
        """Test catching ProfileNotFound exception."""
        caught = False
        try:
            raise ProfileNotFound("Profile missing")
        except ProfileNotFound as e:
            caught = True
            assert "Profile" in str(e)

        assert caught is True

    def test_catch_card_not_found(self):
        """Test catching CardNotFound exception."""
        caught = False
        try:
            raise CardNotFound("Card missing")
        except CardNotFound as e:
            caught = True
            assert "Card" in str(e)

        assert caught is True

    def test_multiple_profile_exceptions(self):
        """Test handling multiple profile exception types."""
        exceptions_to_test = [
            (ProfileNotFound, "profile"),
            (CardNotFound, "card")
        ]

        for exc_class, keyword in exceptions_to_test:
            caught = False
            try:
                raise exc_class(keyword)
            except exc_class:
                caught = True

            assert caught is True


class TestExceptionInheritance:
    """Test exception inheritance and relationships."""

    def test_all_exceptions_inherit_from_exception(self):
        """Test that all custom exceptions inherit from Exception."""
        exceptions = [
            InsufficientFunds,
            InvalidOffer,
            ProfileNotFound,
            CardNotFound
        ]

        for exc_class in exceptions:
            assert issubclass(exc_class, Exception)

    def test_exceptions_can_be_caught_as_exception(self):
        """Test that custom exceptions can be caught as generic Exception."""
        for exc_class in [
            InsufficientFunds,
            InvalidOffer,
            ProfileNotFound,
            CardNotFound
        ]:
            caught = False
            try:
                raise exc_class("test")
            except Exception as e:
                caught = True
                assert isinstance(e, exc_class)

            assert caught is True

    def test_exception_string_representation(self):
        """Test string representation of exceptions."""
        test_cases = [
            (InsufficientFunds, "Insufficient Funds"),
            (InvalidOffer, "Invalid Offer"),
            (ProfileNotFound, "Profile Not Found"),
            (CardNotFound, "Card Not Found")
        ]

        for exc_class, _ in test_cases:
            exc = exc_class("Test message")
            assert "Test message" in str(exc)
