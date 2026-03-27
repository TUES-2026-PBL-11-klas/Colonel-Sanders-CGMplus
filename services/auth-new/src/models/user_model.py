from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel
import uuid


class Role(BaseModel):
    __tablename__ = 'user_roles'

    id: Mapped[int] = mapped_column(primary_key=True)

    users: Mapped[list["User"]] = relationship(
        'User',
        backref='role',
        lazy=True
    )

    role: Mapped[str] = mapped_column(String(63), nullable=False)


class User(BaseModel):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))

    def __repr__(self):  # Representation in logs
        return f"<User id={self.id} email={self.email}"
