"""Dictionary query service."""

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.db.models.dicts import DictCollege, DictRegion, DictSchool


class DictService:
    """Dictionary service."""

    @staticmethod
    def list_regions(db: Session, parent_region_id: int | None = None, level: int | None = None) -> list[DictRegion]:
        query = select(DictRegion).where(DictRegion.is_enabled == 1)
        if parent_region_id is not None:
            query = query.where(DictRegion.parent_region_id == parent_region_id)
        if level is not None:
            query = query.where(DictRegion.region_level == level)

        query = query.order_by(DictRegion.sort_no.asc(), DictRegion.region_id.asc())
        return list(db.scalars(query).all())

    @staticmethod
    def list_schools(db: Session, region_id: int | None = None) -> list[DictSchool]:
        query = select(DictSchool).where(DictSchool.is_enabled == 1)
        if region_id is not None:
            query = query.where(DictSchool.region_id == region_id)
        query = query.order_by(DictSchool.school_name.asc())
        return list(db.scalars(query).all())

    @staticmethod
    def list_colleges(db: Session, school_id: int) -> list[DictCollege]:
        query = select(DictCollege).where(
            and_(
                DictCollege.school_id == school_id,
                DictCollege.is_enabled == 1,
            )
        )
        query = query.order_by(DictCollege.college_name.asc())
        return list(db.scalars(query).all())
