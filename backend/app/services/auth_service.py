"""Authentication service.

Contains register/login core logic and validation.
"""

from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.db.models.dicts import DictCollege, DictRegion, DictSchool
from app.db.models.user import AppUser
from app.schemas.auth import LoginRequest, RegisterRequest


class AuthService:
    """Authentication business service."""

    @staticmethod
    def _check_org_binding(db: Session, region_id: int, school_id: int, college_id: int) -> None:
        """Validate region/school/college ownership chain."""

        region = db.scalar(
            select(DictRegion).where(and_(DictRegion.region_id == region_id, DictRegion.is_enabled == 1))
        )
        if not region:
            raise ValueError("Region does not exist or is disabled.")

        school = db.scalar(
            select(DictSchool).where(
                and_(
                    DictSchool.school_id == school_id,
                    DictSchool.region_id == region_id,
                    DictSchool.is_enabled == 1,
                )
            )
        )
        if not school:
            raise ValueError("School does not exist or does not belong to the selected region.")

        college = db.scalar(
            select(DictCollege).where(
                and_(
                    DictCollege.college_id == college_id,
                    DictCollege.school_id == school_id,
                    DictCollege.is_enabled == 1,
                )
            )
        )
        if not college:
            raise ValueError("College does not exist or does not belong to the selected school.")

    @staticmethod
    def register(db: Session, payload: RegisterRequest) -> AppUser:
        """Register a new user."""

        existing_user = db.scalar(select(AppUser).where(AppUser.username == payload.username))
        if existing_user:
            raise ValueError("Username already exists.")

        if payload.email:
            existing_email = db.scalar(select(AppUser).where(AppUser.email == payload.email))
            if existing_email:
                raise ValueError("Email is already used.")

        if payload.phone:
            existing_phone = db.scalar(select(AppUser).where(AppUser.phone == payload.phone))
            if existing_phone:
                raise ValueError("Phone number is already used.")

        if payload.student_no:
            same_school_student = db.scalar(
                select(AppUser).where(
                    and_(
                        AppUser.school_id == payload.school_id,
                        AppUser.student_no == payload.student_no,
                    )
                )
            )
            if same_school_student:
                raise ValueError("Student number already exists in this school.")

        AuthService._check_org_binding(db, payload.region_id, payload.school_id, payload.college_id)

        user = AppUser(
            username=payload.username,
            password_hash=hash_password(payload.password),
            nickname=payload.nickname,
            email=payload.email,
            phone=payload.phone,
            student_no=payload.student_no,
            grade_year=payload.grade_year,
            major_name=payload.major_name,
            region_id=payload.region_id,
            school_id=payload.school_id,
            college_id=payload.college_id,
            last_login_at=None,
        )

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def login(db: Session, payload: LoginRequest) -> AppUser:
        """Login and return user object."""

        user = db.scalar(
            select(AppUser).where(
                and_(
                    AppUser.username == payload.username,
                    AppUser.status == 1,
                    AppUser.deleted_at.is_(None),
                )
            )
        )

        if not user:
            raise ValueError("Invalid username or password.")

        if not verify_password(payload.password, user.password_hash):
            raise ValueError("Invalid username or password.")

        user.last_login_at = datetime.now()
        db.commit()
        db.refresh(user)
        return user
