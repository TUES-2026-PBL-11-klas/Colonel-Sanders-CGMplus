from uuid import UUID
from src.repositories.ProfileRepositoriy import ProfileRepository
from src.models.pointTransaction import PointTransaction, PT_TypeEnum
from src.exceptions.ProfileExceptions import ProfileNotFound
from src.extensions import db

class PointService:
    @staticmethod
    def add_points(profile_id: UUID):
        profile = ProfileRepository(session=db.session).get_by_uuid(profile_id=profile_id)
        if profile is None:
            raise ProfileNotFound()

        points = 67  # calculate points

        pt = PointTransaction(
            account_id=profile_id,
            pt_type=PT_TypeEnum.transport,
            ammount=points,
            description=f"{points} earned by using the transportation",
        )

        profile.balance = (profile.balance or 0) + points

        db.session.add(pt)
        db.session.commit()

        return True
