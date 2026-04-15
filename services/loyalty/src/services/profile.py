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

    @staticmethod
    def update_points(profile_id: uuid.UUID):
        # implement a way to calculate points prob idk :sob:
        points = 67

        profile = Profile.query.filter_by(id=profile_id).first()

        if profile is None:
            return False

        profile.balance += (profile.balance or 0) + points
        db.session.commit()

        return True
