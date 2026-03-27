from sqlalchemy.orm import Session
from sqlalchemy import select
from src.models.user_model import Role, User
from src.repositories.base_repository import BaseRepository


class RoleRepository(BaseRepository[Role]):
    def __init__(self, session: Session):
        super().__init__(Role, session)

    def get_by_name(self, role_name: str) -> Role | None:
        stmt = select(Role).where(Role.role == role_name)
        return self.session.scalar(stmt)

    def get_users(self, role_id: int, limit: int = 100, offset: int = 0) -> list[User]:
        stmt = (
            select(User)
            .where(User.role_id == role_id)
            .limit(limit)
            .offset(offset)
        )
        return self.session.scalars(stmt).all()
