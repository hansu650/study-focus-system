"""Point ledger query service."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.points import PointLedger


class PointService:
    """Read-only service for point balance and ledger browsing."""

    @staticmethod
    def list_ledger(
        db: Session,
        user_id: int,
        page: int,
        page_size: int,
        biz_type: str | None = None,
    ) -> tuple[int, list[PointLedger]]:
        """Return paginated point ledger records for one user."""

        query = select(PointLedger).where(PointLedger.user_id == user_id)
        if biz_type:
            query = query.where(PointLedger.biz_type == biz_type)

        total = int(db.scalar(select(func.count()).select_from(query.subquery())) or 0)
        rows = list(
            db.scalars(
                query.order_by(PointLedger.occurred_at.desc(), PointLedger.txn_id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            ).all()
        )
        return total, rows
