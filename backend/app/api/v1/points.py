"""Point endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models.user import AppUser
from app.db.session import get_db
from app.schemas.points import PointBalanceOut, PointLedgerListOut, PointLedgerOut
from app.services.point_service import PointService

router = APIRouter(prefix="/points", tags=["Points"])


@router.get("/balance", response_model=PointBalanceOut)
def get_point_balance(current_user: Annotated[AppUser, Depends(get_current_user)]) -> PointBalanceOut:
    """Get current point and focus totals."""

    return PointBalanceOut(
        user_id=current_user.user_id,
        total_points=int(current_user.total_points),
        total_focus_minutes=int(current_user.total_focus_minutes),
    )


@router.get("/ledger", response_model=PointLedgerListOut)
def list_point_ledger(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[AppUser, Depends(get_current_user)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    biz_type: Annotated[str | None, Query(description="Optional business type filter")] = None,
) -> PointLedgerListOut:
    """List current user's point ledger records."""

    total, rows = PointService.list_ledger(
        db=db,
        user_id=current_user.user_id,
        page=page,
        page_size=page_size,
        biz_type=biz_type,
    )

    return PointLedgerListOut(
        page=page,
        page_size=page_size,
        total=total,
        items=[PointLedgerOut.model_validate(item) for item in rows],
    )
