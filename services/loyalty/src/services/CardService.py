from src.extensions import db
from src.models.card import Card
import uuid
from datetime import datetime


class CardService:
    def create_card(card_id: uuid.UUID) -> Card:
        card = Card(
            id=card_id,
            expiry_date=datetime.now(),
            active=False,
            nfc_id="0000000000000000"
        )
        db.session.add(card)
        db.session.commit()
        return card
