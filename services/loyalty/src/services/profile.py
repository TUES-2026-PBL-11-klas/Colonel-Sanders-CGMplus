from src.extensions import db
from src.models.profile import Profile
import uuid

class ProfileService:
    @staticmethod
    def create_profile(profile_id: uuid.UUID) -> Profile:
        profile = Profile(
            id=profile_id,
            balance=0,
            rank="bronze"
        )
        db.session.add(profile)
        db.session.commit()
        return profile
