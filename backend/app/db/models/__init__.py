"""Import ORM models so metadata is fully registered."""

from app.db.models.base import Base
from app.db.models.dicts import DictCollege, DictRegion, DictSchool
from app.db.models.feedback import FeedbackMessage
from app.db.models.focus import FocusSession
from app.db.models.points import PointLedger
from app.db.models.redeem import RedeemOrder
from app.db.models.user import AppUser

__all__ = [
    "Base",
    "DictRegion",
    "DictSchool",
    "DictCollege",
    "AppUser",
    "FeedbackMessage",
    "FocusSession",
    "PointLedger",
    "RedeemOrder",
]