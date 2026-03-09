"""Dictionary output schemas."""

from pydantic import BaseModel, ConfigDict


class RegionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    region_id: int
    region_code: str
    region_name: str
    region_level: int
    parent_region_id: int | None


class SchoolOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    school_id: int
    school_code: str
    school_name: str
    region_id: int
    school_type: int


class CollegeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    college_id: int
    school_id: int
    college_code: str
    college_name: str
