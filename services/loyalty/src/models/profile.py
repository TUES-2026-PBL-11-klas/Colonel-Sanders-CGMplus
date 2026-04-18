from src.extensions import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, func
import uuid
from datetime import datetime


class Profile(db.Model):
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    balance: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    rank: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )

    transactions: Mapped[
        list["PointTransaction"]  # noqa: F821 #type: ignore
    ] = relationship(
        "PointTransaction", back_populates="profile"
    )
