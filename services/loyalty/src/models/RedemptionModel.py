from src.models.baseModel import BaseModel
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, ForeignKey
import uuid


class RedemptionModel(BaseModel):
    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        index=True,
        default=uuid.uuid4,
    )

    offer_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("offers.id"),
        nullable=False
    )

    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("profile.id"),
        nullable=False
    )

    points_cost: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
