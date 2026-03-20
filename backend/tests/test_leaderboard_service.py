from datetime import date, datetime, timedelta
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models.base import Base
from app.db.models.dicts import DictCollege, DictRegion, DictSchool
from app.db.models.focus import FocusSession
from app.db.models.points import PointLedger
from app.db.models.user import AppUser
from app.schemas.leaderboard import LeaderboardPeriod, LeaderboardScope
from app.services.leaderboard_service import LeaderboardService


class LeaderboardServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(
            self.engine,
            tables=[
                DictRegion.__table__,
                DictSchool.__table__,
                DictCollege.__table__,
                AppUser.__table__,
                FocusSession.__table__,
                PointLedger.__table__,
            ],
        )
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.db = self.SessionLocal()

        self.db.add(DictRegion(region_id=1, region_code="HB", region_name="Hubei", region_level=1, parent_region_id=None, sort_no=1, is_enabled=1))
        self.db.add_all(
            [
                DictSchool(school_id=1, school_code="HUBU", school_name="Hubei University", region_id=1, school_type=1, is_enabled=1),
                DictSchool(school_id=2, school_code="WUST", school_name="Wuhan University of Science and Technology", region_id=1, school_type=1, is_enabled=1),
            ]
        )
        self.db.add_all(
            [
                DictCollege(college_id=1, school_id=1, college_code="HUBU-CS", college_name="School of Computer Science", is_enabled=1),
                DictCollege(college_id=2, school_id=1, college_code="HUBU-ECON", college_name="School of Economics", is_enabled=1),
                DictCollege(college_id=3, school_id=2, college_code="WUST-CS", college_name="School of Computer Science and Technology", is_enabled=1),
            ]
        )

        self.current_user = AppUser(
            user_id=1,
            username="demo_hubu_cs",
            password_hash="x" * 60,
            nickname="HUBU CS",
            major_name="Software Engineering",
            region_id=1,
            school_id=1,
            college_id=1,
            total_points=25,
            total_focus_minutes=30,
            status=1,
        )
        other_same_school = AppUser(
            user_id=2,
            username="demo_hubu_econ",
            password_hash="x" * 60,
            nickname="HUBU ECON",
            major_name="Accounting",
            region_id=1,
            school_id=1,
            college_id=2,
            total_points=20,
            total_focus_minutes=20,
            status=1,
        )
        other_school = AppUser(
            user_id=3,
            username="demo_wust_cs",
            password_hash="x" * 60,
            nickname="WUST CS",
            major_name="Computer Science",
            region_id=1,
            school_id=2,
            college_id=3,
            total_points=30,
            total_focus_minutes=30,
            status=1,
        )
        quiz_only_user = AppUser(
            user_id=4,
            username="demo_quiz_only",
            password_hash="x" * 60,
            nickname="Quiz Only",
            major_name="English",
            region_id=1,
            school_id=1,
            college_id=1,
            total_points=5,
            total_focus_minutes=0,
            status=1,
        )
        self.db.add_all([self.current_user, other_same_school, other_school, quiz_only_user])
        self.db.flush()

        now = datetime.now()
        self.db.add_all(
            [
                FocusSession(session_id=1, user_id=1, focus_date=date.today(), planned_minutes=25, actual_minutes=25, start_at=now - timedelta(minutes=26), end_at=now - timedelta(minutes=1), status="COMPLETED", lock_mode="NONE", blocked_apps_json=None, blocked_sites_json=None, interrupt_count=0, awarded_points=25, settle_status=1, remark=None),
                FocusSession(session_id=2, user_id=2, focus_date=date.today(), planned_minutes=20, actual_minutes=20, start_at=now - timedelta(minutes=21), end_at=now - timedelta(minutes=1), status="COMPLETED", lock_mode="NONE", blocked_apps_json=None, blocked_sites_json=None, interrupt_count=0, awarded_points=20, settle_status=1, remark=None),
                FocusSession(session_id=3, user_id=3, focus_date=date.today(), planned_minutes=30, actual_minutes=30, start_at=now - timedelta(minutes=31), end_at=now - timedelta(minutes=1), status="COMPLETED", lock_mode="NONE", blocked_apps_json=None, blocked_sites_json=None, interrupt_count=0, awarded_points=30, settle_status=1, remark=None),
            ]
        )
        self.db.add_all(
            [
                PointLedger(txn_id=1, user_id=1, change_points=25, balance_before=0, balance_after=25, biz_type="FOCUS_REWARD", biz_id=1, note="Focus session completed."),
                PointLedger(txn_id=2, user_id=2, change_points=20, balance_before=0, balance_after=20, biz_type="FOCUS_REWARD", biz_id=2, note="Focus session completed."),
                PointLedger(txn_id=3, user_id=3, change_points=30, balance_before=0, balance_after=30, biz_type="FOCUS_REWARD", biz_id=3, note="Focus session completed."),
                PointLedger(txn_id=4, user_id=4, change_points=5, balance_before=0, balance_after=5, biz_type="QUESTION_REWARD", biz_id=20260318, note="Daily question answered correctly."),
            ]
        )
        self.db.commit()

    def tearDown(self) -> None:
        self.db.close()
        self.engine.dispose()

    def test_school_scope_can_target_selected_school(self) -> None:
        result = LeaderboardService.get_focus_leaderboard(
            db=self.db,
            current_user=self.current_user,
            period=LeaderboardPeriod.DAY,
            scope=LeaderboardScope.SCHOOL,
            target_date=date.today(),
            school_id=2,
            college_id=None,
            limit=10,
        )

        self.assertEqual(result.selected_school_name, "Wuhan University of Science and Technology")
        self.assertEqual(len(result.items), 1)
        self.assertEqual(result.items[0].school_name, "Wuhan University of Science and Technology")

    def test_college_scope_can_target_selected_college(self) -> None:
        result = LeaderboardService.get_focus_leaderboard(
            db=self.db,
            current_user=self.current_user,
            period=LeaderboardPeriod.DAY,
            scope=LeaderboardScope.COLLEGE,
            target_date=date.today(),
            school_id=1,
            college_id=2,
            limit=10,
        )

        self.assertEqual(result.selected_college_name, "School of Economics")
        self.assertEqual(len(result.items), 1)
        self.assertEqual(result.items[0].nickname, "HUBU ECON")

    def test_global_scope_includes_question_reward_only_user(self) -> None:
        result = LeaderboardService.get_focus_leaderboard(
            db=self.db,
            current_user=self.current_user,
            period=LeaderboardPeriod.DAY,
            scope=LeaderboardScope.GLOBAL,
            target_date=date.today(),
            school_id=None,
            college_id=None,
            limit=10,
        )

        self.assertEqual(result.scope, LeaderboardScope.GLOBAL)
        self.assertIsNone(result.selected_school_id)
        self.assertEqual(len(result.items), 4)
        self.assertEqual(result.items[0].school_name, "Wuhan University of Science and Technology")
        quiz_only = next(item for item in result.items if item.username == "demo_quiz_only")
        self.assertEqual(quiz_only.total_points, 5)
        self.assertEqual(quiz_only.total_focus_minutes, 0)


if __name__ == "__main__":
    unittest.main()
