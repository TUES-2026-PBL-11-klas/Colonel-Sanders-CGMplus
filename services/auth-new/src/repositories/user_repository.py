from sqlalchemy.orm import Session
from sqlalchemy import select
from src.models.user_model import User
from src.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: Session):
        super().__init__(User, session)

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self.session.scalar(stmt)

    def get_active(self, limit: int = 100, offset: int = 0) -> list[User]:
        stmt = (
            select(User)
            .where(User.is_active.is_(True))
            .limit(limit)
            .offset(offset)
        )
        return self.session.scalars(stmt).all()

    def get_inactive(self, limit: int = 100, offset: int = 0) -> list[User]:
        stmt = (
            select(User)
            .where(User.is_active.is_(False))
            .limit(limit)
            .offset(offset)
        )
        return self.session.scalars(stmt).all()
