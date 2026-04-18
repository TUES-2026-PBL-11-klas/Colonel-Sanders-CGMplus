from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Text, Enum, ForeignKey
from src.models.baseModel import BaseModel
import uuid
import enum


class PT_TypeEnum(enum.Enum):
    transport = "transport"
    other = "other"


class PointTransaction(BaseModel):
    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        index=True
    )

    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("profile.id"),
        nullable=False
    )

    pt_type: Mapped[PT_TypeEnum] = mapped_column(
        Enum(PT_TypeEnum),
        nullable=False
    )

    ammount: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    profile: Mapped["Profile"] = relationship(  # noqa: F821 # type: ignore
        "Profile",
        back_populates="transactions"
    )
