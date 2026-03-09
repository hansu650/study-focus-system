"""User service."""

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.db.models.user import AppUser
from app.schemas.user import UserUpdateRequest


class UserService:
    """User profile service."""

    @staticmethod
    def get_me(user: AppUser) -> AppUser:
        """Return current user profile."""

        return user

    @staticmethod
    def update_me(db: Session, user: AppUser, payload: UserUpdateRequest) -> AppUser:
        """Update editable profile fields with uniqueness checks."""

        update_data = payload.model_dump(exclude_unset=True)

        new_email = update_data.get("email")
        if new_email and new_email != user.email:
            conflict_email = db.scalar(
                select(AppUser).where(
                    and_(
                        AppUser.email == new_email,
                        AppUser.user_id != user.user_id,
                    )
                )
            )
            if conflict_email:
                raise ValueError("Email is already used.")

        new_phone = update_data.get("phone")
        if new_phone and new_phone != user.phone:
            conflict_phone = db.scalar(
                select(AppUser).where(
                    and_(
                        AppUser.phone == new_phone,
                        AppUser.user_id != user.user_id,
                    )
                )
            )
            if conflict_phone:
                raise ValueError("Phone number is already used.")

        for key, value in update_data.items():
            setattr(user, key, value)

        db.add(user)
        db.commit()
        db.refresh(user)
        return user
