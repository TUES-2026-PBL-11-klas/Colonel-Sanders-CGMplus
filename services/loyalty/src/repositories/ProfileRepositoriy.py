from sqlalchemy.orm import Session
from sqlalchemy import select
from src.models.profile import Profile as ProfileModel
from uuid import UUID


class ProfileRepository():
    def __init__(self, session: Session):
        self.model = ProfileModel
        self.session = session

    def get_by_uuid(self, profile_id: UUID) -> ProfileModel:
        return self.session.get(self.model, profile_id)
