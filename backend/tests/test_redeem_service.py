from datetime import datetime, timedelta
import unittest
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.models.base import Base
from app.db.models.redeem import RedeemOrder
from app.db.models.user import AppUser
from app.schemas.redeem import RedeemOrderVerifyRequest
from app.services.redeem_service import RedeemService


class RedeemServiceSecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(
            self.engine,
            tables=[AppUser.__table__, RedeemOrder.__table__],
        )
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.db = self.SessionLocal()

        self.user = AppUser(
            user_id=1,
            username="store-owner-001",
            password_hash="x" * 60,
            nickname="Store Owner",
            region_id=1,
            school_id=1,
            college_id=1,
            total_points=0,
            total_focus_minutes=0,
            status=1,
        )
        self.db.add(self.user)

        self.order = RedeemOrder(
            redeem_order_id=1,
            order_no="RO202603110001",
            user_id=99,
            school_id=1,
            store_name="Campus Print Shop A",
            points_cost=10,
            print_quota_pages=5,
            coupon_token="coupon-token-001",
            qr_payload="{}",
            status="PAID",
            points_txn_id=None,
            expire_at=datetime.now() + timedelta(minutes=30),
            verified_at=None,
            verified_by=None,
        )
        self.db.add(self.order)
        self.db.commit()
        self.db.refresh(self.user)
        self.db.refresh(self.order)

    def tearDown(self) -> None:
        self.db.close()
        self.engine.dispose()

    def test_authorize_verifier_requires_configured_token(self) -> None:
        with patch.object(settings, "redeem_verify_token", "CHANGE_ME"):
            with self.assertRaises(RuntimeError) as ctx:
                RedeemService.authorize_verifier(
                    current_user=self.user,
                    payload=RedeemOrderVerifyRequest(
                        coupon_token="coupon-token-001",
                        verifier_id="store-owner-001",
                    ),
                    merchant_token="merchant-secret",
                )

        self.assertIn("not configured", str(ctx.exception))

    def test_authorize_verifier_rejects_invalid_token(self) -> None:
        with patch.object(settings, "redeem_verify_token", "merchant-secret"):
            with self.assertRaises(PermissionError) as ctx:
                RedeemService.authorize_verifier(
                    current_user=self.user,
                    payload=RedeemOrderVerifyRequest(
                        coupon_token="coupon-token-001",
                        verifier_id="store-owner-001",
                    ),
                    merchant_token="wrong-token",
                )

        self.assertIn("invalid", str(ctx.exception))

    def test_authorize_verifier_rejects_mismatched_verifier_id(self) -> None:
        with patch.object(settings, "redeem_verify_token", "merchant-secret"):
            with self.assertRaises(PermissionError) as ctx:
                RedeemService.authorize_verifier(
                    current_user=self.user,
                    payload=RedeemOrderVerifyRequest(
                        coupon_token="coupon-token-001",
                        verifier_id="other-user",
                    ),
                    merchant_token="merchant-secret",
                )

        self.assertIn("current logged-in username", str(ctx.exception))

    def test_verify_order_by_token_marks_verified_by_current_user(self) -> None:
        with patch.object(settings, "redeem_verify_token", "merchant-secret"):
            order = RedeemService.verify_order_by_token(
                db=self.db,
                current_user=self.user,
                payload=RedeemOrderVerifyRequest(
                    coupon_token="coupon-token-001",
                    verifier_id="store-owner-001",
                ),
                merchant_token="merchant-secret",
            )

        self.assertEqual(order.status, "VERIFIED")
        self.assertEqual(order.verified_by, "store-owner-001")
        self.assertIsNotNone(order.verified_at)


if __name__ == "__main__":
    unittest.main()