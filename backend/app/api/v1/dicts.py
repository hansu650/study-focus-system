"""Dictionary endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.dicts import CollegeOut, RegionOut, SchoolOut
from app.services.dict_service import DictService

router = APIRouter(prefix="/dicts", tags=["Dicts"])


@router.get("/regions", response_model=list[RegionOut])
def get_regions(
    db: Annotated[Session, Depends(get_db)],
    parent_region_id: Annotated[int | None, Query(description="Parent region id")] = None,
    level: Annotated[int | None, Query(description="Region level")] = None,
) -> list[RegionOut]:
    """List regions."""

    regions = DictService.list_regions(db, parent_region_id=parent_region_id, level=level)
    return [RegionOut.model_validate(item) for item in regions]


@router.get("/schools", response_model=list[SchoolOut])
def get_schools(
    db: Annotated[Session, Depends(get_db)],
    region_id: Annotated[int | None, Query(description="Region id")] = None,
) -> list[SchoolOut]:
    """List schools."""

    schools = DictService.list_schools(db, region_id=region_id)
    return [SchoolOut.model_validate(item) for item in schools]


@router.get("/colleges", response_model=list[CollegeOut])
def get_colleges(
    db: Annotated[Session, Depends(get_db)],
    school_id: Annotated[int, Query(description="School id")],
) -> list[CollegeOut]:
    """List colleges by school id."""

    colleges = DictService.list_colleges(db, school_id=school_id)
    return [CollegeOut.model_validate(item) for item in colleges]
