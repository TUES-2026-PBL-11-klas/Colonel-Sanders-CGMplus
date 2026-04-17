from src.models.baseModel import BaseModel
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, Text, Boolean, Enum
from datetime import datetime
import enum


class PriceType(enum.Enum):
    Points = "points"
    Experience = "experience"


class RewardType(enum.Enum):
    CardRenew = "cardrenew"
    CardSkin = "cardskin"


class OfferModel(BaseModel):
    __tablename__ = "offers"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=True
    )

    price: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    price_type: Mapped[PriceType] = mapped_column(
        Enum(PriceType),
        nullable=False
    )

    reward_type: Mapped[RewardType] = mapped_column(
        Enum(RewardType),
        nullable=False
    )

    valid_until: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )
