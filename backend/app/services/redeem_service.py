"""Redeem order service."""

from __future__ import annotations

import json
import secrets
from datetime import datetime, timedelta

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.points import PointLedger
from app.db.models.redeem import RedeemOrder
from app.db.models.user import AppUser
from app.schemas.redeem import (
    RedeemOrderCancelRequest,
    RedeemOrderCreateRequest,
    RedeemOrderStatus,
    RedeemOrderVerifyRequest,
)


class RedeemService:
    """Business service for point redeem and verification flow."""

    VERIFY_TOKEN_PLACEHOLDERS = {"", "CHANGE_ME", "PLEASE_CHANGE_ME", "YOUR_VERIFY_TOKEN"}

    @staticmethod
    def create_order(db: Session, user: AppUser, payload: RedeemOrderCreateRequest) -> RedeemOrder:
        """Create a redeem order and deduct points immediately."""

        now = datetime.now()
        user_locked = db.scalar(select(AppUser).where(AppUser.user_id == user.user_id).with_for_update())
        if not user_locked:
            raise ValueError("Current user does not exist.")

        if int(user_locked.total_points) < payload.points_cost:
            raise ValueError("Insufficient points for redeem.")

        order = RedeemOrder(
            order_no=RedeemService._generate_order_no(),
            user_id=user_locked.user_id,
            school_id=user_locked.school_id,
            store_name=payload.store_name,
            points_cost=payload.points_cost,
            print_quota_pages=payload.print_quota_pages,
            coupon_token=RedeemService._generate_coupon_token(),
            qr_payload="",
            status=RedeemOrderStatus.PAID.value,
            points_txn_id=None,
            expire_at=now + timedelta(minutes=payload.expire_minutes),
            verified_at=None,
            verified_by=None,
        )

        db.add(order)
        db.flush()

        order.qr_payload = RedeemService._build_qr_payload(order.order_no, order.coupon_token)

        ledger = RedeemService._append_points_ledger(
            db=db,
            user=user_locked,
            change_points=-payload.points_cost,
            biz_type="PRINT_REDEEM",
            biz_id=order.redeem_order_id,
            note="Redeem print coupon.",
        )
        db.flush()

        order.points_txn_id = ledger.txn_id

        db.add(user_locked)
        db.add(order)
        db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def authorize_verifier(current_user: AppUser, payload: RedeemOrderVerifyRequest, merchant_token: str | None) -> None:
        """Require a configured merchant token and bind verifier ID to the login user."""

        expected_token = (settings.redeem_verify_token or "").strip()
        if expected_token in RedeemService.VERIFY_TOKEN_PLACEHOLDERS:
            raise RuntimeError("Redeem verification is not configured. Set REDEEM_VERIFY_TOKEN in backend/.env.")

        provided_token = (merchant_token or "").strip()
        if not provided_token:
            raise PermissionError("Merchant verify token is required.")

        if secrets.compare_digest(provided_token, expected_token) is False:
            raise PermissionError("Merchant verify token is invalid.")

        verifier_id = payload.verifier_id.strip()
        if verifier_id != current_user.username:
            raise PermissionError("verifier_id must match the current logged-in username.")

    @staticmethod
    def verify_order_by_token(
        db: Session,
        current_user: AppUser,
        payload: RedeemOrderVerifyRequest,
        merchant_token: str | None,
    ) -> RedeemOrder:
        """Verify redeem order using coupon token (simulate store scan)."""

        RedeemService.authorize_verifier(current_user=current_user, payload=payload, merchant_token=merchant_token)

        order = db.scalar(
            select(RedeemOrder).where(RedeemOrder.coupon_token == payload.coupon_token).with_for_update()
        )
        if not order:
            raise ValueError("Redeem order not found.")

        now = datetime.now()

        if order.status == RedeemOrderStatus.VERIFIED.value:
            raise ValueError("Redeem order is already verified.")

        if order.status == RedeemOrderStatus.CANCELLED.value:
            raise ValueError("Cancelled order cannot be verified.")

        if order.expire_at < now:
            order.status = RedeemOrderStatus.EXPIRED.value
            db.add(order)
            db.commit()
            db.refresh(order)
            raise ValueError("Redeem order is expired.")

        if order.status not in {RedeemOrderStatus.CREATED.value, RedeemOrderStatus.PAID.value}:
            raise ValueError("Current order status cannot be verified.")

        order.status = RedeemOrderStatus.VERIFIED.value
        order.verified_at = now
        order.verified_by = current_user.username

        db.add(order)
        db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def cancel_order(
        db: Session,
        user: AppUser,
        order_no: str,
        payload: RedeemOrderCancelRequest,
    ) -> RedeemOrder:
        """Cancel own redeem order and refund points when eligible."""

        order = db.scalar(
            select(RedeemOrder)
            .where(
                and_(
                    RedeemOrder.order_no == order_no,
                    RedeemOrder.user_id == user.user_id,
                )
            )
            .with_for_update()
        )
        if not order:
            raise ValueError("Redeem order not found.")

        if order.status == RedeemOrderStatus.VERIFIED.value:
            raise ValueError("Verified order cannot be cancelled.")

        if order.status == RedeemOrderStatus.CANCELLED.value:
            raise ValueError("Order is already cancelled.")

        now = datetime.now()
        if order.expire_at < now:
            order.status = RedeemOrderStatus.EXPIRED.value
            db.add(order)
            db.commit()
            db.refresh(order)
            raise ValueError("Order is expired and cannot be cancelled.")

        if order.status not in {RedeemOrderStatus.CREATED.value, RedeemOrderStatus.PAID.value}:
            raise ValueError("Current order status cannot be cancelled.")

        user_locked = db.scalar(select(AppUser).where(AppUser.user_id == user.user_id).with_for_update())
        if not user_locked:
            raise ValueError("Current user does not exist.")

        note = "Redeem order cancelled."
        if payload.reason:
            note = f"Redeem order cancelled: {payload.reason}"

        RedeemService._append_points_ledger(
            db=db,
            user=user_locked,
            change_points=order.points_cost,
            biz_type="ORDER_REFUND",
            biz_id=order.redeem_order_id,
            note=note,
        )

        order.status = RedeemOrderStatus.CANCELLED.value
        db.add(user_locked)
        db.add(order)
        db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def get_order(db: Session, user_id: int, order_no: str) -> RedeemOrder:
        """Get one own redeem order by order number."""

        order = db.scalar(
            select(RedeemOrder).where(
                and_(
                    RedeemOrder.order_no == order_no,
                    RedeemOrder.user_id == user_id,
                )
            )
        )
        if not order:
            raise ValueError("Redeem order not found.")
        return order

    @staticmethod
    def list_orders(
        db: Session,
        user_id: int,
        page: int,
        page_size: int,
        status: RedeemOrderStatus | None = None,
    ) -> tuple[int, list[RedeemOrder]]:
        """List own redeem orders with pagination."""

        query = select(RedeemOrder).where(RedeemOrder.user_id == user_id)
        if status is not None:
            query = query.where(RedeemOrder.status == status.value)

        total = int(db.scalar(select(func.count()).select_from(query.subquery())) or 0)
        rows = list(
            db.scalars(
                query.order_by(RedeemOrder.created_at.desc(), RedeemOrder.redeem_order_id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            ).all()
        )
        return total, rows

    @staticmethod
    def _build_qr_payload(order_no: str, coupon_token: str) -> str:
        payload = {
            "type": "print_coupon",
            "order_no": order_no,
            "coupon_token": coupon_token,
        }
        return json.dumps(payload, ensure_ascii=True, separators=(",", ":"))

    @staticmethod
    def _generate_order_no() -> str:
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        rnd = secrets.token_hex(3).upper()
        return f"RO{ts}{rnd}"

    @staticmethod
    def _generate_coupon_token() -> str:
        return secrets.token_hex(16)

    @staticmethod
    def _append_points_ledger(
        db: Session,
        user: AppUser,
        change_points: int,
        biz_type: str,
        biz_id: int,
        note: str,
    ) -> PointLedger:
        before = int(user.total_points)
        after = before + change_points
        if after < 0:
            raise ValueError("Point balance cannot be negative.")

        ledger = PointLedger(
            user_id=user.user_id,
            change_points=change_points,
            balance_before=before,
            balance_after=after,
            biz_type=biz_type,
            biz_id=biz_id,
            note=note,
        )

        user.total_points = after
        db.add(ledger)
        return ledger