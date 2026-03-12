"""Redeem order endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models.user import AppUser
from app.db.session import get_db
from app.schemas.redeem import (
    RedeemOrderCancelRequest,
    RedeemOrderCreateRequest,
    RedeemOrderListOut,
    RedeemOrderOut,
    RedeemOrderStatus,
    RedeemOrderVerifyRequest,
)
from app.services.redeem_service import RedeemService

router = APIRouter(prefix="/redeem-orders", tags=["Redeem"])


@router.post("", response_model=RedeemOrderOut, status_code=status.HTTP_201_CREATED)
def create_redeem_order(
    payload: RedeemOrderCreateRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[AppUser, Depends(get_current_user)],
) -> RedeemOrderOut:
    """Create redeem order and deduct points."""

    try:
        order = RedeemService.create_order(db, current_user, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return RedeemOrderOut.model_validate(order)


@router.get("/my", response_model=RedeemOrderListOut)
def list_my_redeem_orders(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[AppUser, Depends(get_current_user)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    status_filter: Annotated[RedeemOrderStatus | None, Query(alias="status")] = None,
) -> RedeemOrderListOut:
    """List current user's redeem orders."""

    total, rows = RedeemService.list_orders(
        db=db,
        user_id=current_user.user_id,
        page=page,
        page_size=page_size,
        status=status_filter,
    )

    return RedeemOrderListOut(
        page=page,
        page_size=page_size,
        total=total,
        items=[RedeemOrderOut.model_validate(item) for item in rows],
    )


@router.get("/{order_no}", response_model=RedeemOrderOut)
def get_my_redeem_order(
    order_no: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[AppUser, Depends(get_current_user)],
) -> RedeemOrderOut:
    """Get one own redeem order by order number."""

    try:
        order = RedeemService.get_order(db, user_id=current_user.user_id, order_no=order_no)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    return RedeemOrderOut.model_validate(order)


@router.post("/verify", response_model=RedeemOrderOut)
def verify_redeem_order(
    payload: RedeemOrderVerifyRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[AppUser, Depends(get_current_user)],
    merchant_token: Annotated[str | None, Header(alias="X-Merchant-Token")] = None,
) -> RedeemOrderOut:
    """Verify redeem order using coupon token (store scan simulation)."""

    try:
        order = RedeemService.verify_order_by_token(
            db=db,
            current_user=current_user,
            payload=payload,
            merchant_token=merchant_token,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return RedeemOrderOut.model_validate(order)


@router.post("/{order_no}/cancel", response_model=RedeemOrderOut)
def cancel_my_redeem_order(
    order_no: str,
    payload: RedeemOrderCancelRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[AppUser, Depends(get_current_user)],
) -> RedeemOrderOut:
    """Cancel own redeem order and refund points."""

    try:
        order = RedeemService.cancel_order(db, current_user, order_no, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return RedeemOrderOut.model_validate(order)