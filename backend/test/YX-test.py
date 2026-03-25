from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from typing import Any
from urllib import error, parse, request

DEFAULT_API_BASE = "http://127.0.0.1:8000/api/v1"
DEFAULT_PASSWORD = "StudyFocus123!"
DEFAULT_EXISTING_USERNAME = "hubu_mjc_se_101"


class SmokeTestError(RuntimeError):
    """Raised when one smoke-test step fails."""


def request_json(
    method: str,
    url: str,
    payload: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req_headers = {"Accept": "application/json"}
    if payload is not None:
        req_headers["Content-Type"] = "application/json; charset=utf-8"
    if headers:
        req_headers.update(headers)

    req = request.Request(url, data=body, headers=req_headers, method=method.upper())
    try:
        with request.urlopen(req, timeout=30) as response:
            text = response.read().decode("utf-8")
            return json.loads(text) if text else {}
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SmokeTestError(f"HTTP {exc.code} {method.upper()} {url}: {detail}") from exc
    except error.URLError as exc:
        raise SmokeTestError(f"Request failed for {method.upper()} {url}: {exc.reason}") from exc


def get_json(url: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
    return request_json("GET", url, payload=None, headers=headers)


def post_json(url: str, payload: dict[str, Any] | None, headers: dict[str, str] | None = None) -> dict[str, Any]:
    return request_json("POST", url, payload=payload, headers=headers)


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise SmokeTestError(message)


def build_register_payload(username: str, password: str, region_id: int, school_id: int, college_id: int) -> dict[str, Any]:
    suffix = datetime.now().strftime("%m%d%H%M%S")
    return {
        "username": username,
        "password": password,
        "nickname": f"smoke-{suffix}",
        "email": f"{username}@example.com",
        "phone": f"139{suffix[-8:]}",
        "student_no": f"SMK{suffix}",
        "grade_year": 2026,
        "major_name": "Software Engineering",
        "region_id": region_id,
        "school_id": school_id,
        "college_id": college_id,
    }


def register_user(api_base: str, username: str, password: str, region_id: int, school_id: int, college_id: int) -> dict[str, Any]:
    payload = build_register_payload(username, password, region_id, school_id, college_id)
    return post_json(f"{api_base}/auth/register", payload)


def login(api_base: str, username: str, password: str) -> str:
    result = post_json(
        f"{api_base}/auth/login",
        {
            "username": username,
            "password": password,
        },
    )
    token = str(result.get("access_token") or "").strip()
    assert_true(bool(token), "Login succeeded but access_token is missing.")
    return token


def create_feedback(api_base: str, token: str, username: str) -> dict[str, Any]:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return post_json(
        f"{api_base}/feedback",
        {
            "category": "GENERAL",
            "title": f"Smoke feedback from {username}",
            "content": f"Automated smoke test feedback created at {stamp}.",
            "contact_email": f"{username}@example.com",
        },
        headers=auth_headers(token),
    )


def create_focus_session(api_base: str, token: str) -> dict[str, Any]:
    return post_json(
        f"{api_base}/focus-sessions/start",
        {
            "planned_minutes": 1,
            "lock_mode": "NONE",
            "blocked_apps": [],
            "blocked_sites": [],
            "remark": "smoke core flow",
        },
        headers=auth_headers(token),
    )


def interrupt_session(api_base: str, token: str, session_id: int) -> dict[str, Any]:
    return post_json(
        f"{api_base}/focus-sessions/{session_id}/interrupt",
        {"remark": "smoke interrupt"},
        headers=auth_headers(token),
    )


def resume_session(api_base: str, token: str, session_id: int) -> dict[str, Any]:
    return post_json(
        f"{api_base}/focus-sessions/{session_id}/resume",
        None,
        headers=auth_headers(token),
    )


def abandon_session(api_base: str, token: str, session_id: int) -> dict[str, Any]:
    return post_json(
        f"{api_base}/focus-sessions/{session_id}/abandon",
        {"remark": "smoke cleanup"},
        headers=auth_headers(token),
    )


def list_sessions(api_base: str, token: str, status_filter: str | None = None) -> dict[str, Any]:
    params = {"page": 1, "page_size": 20}
    if status_filter:
        params["status"] = status_filter
    url = f"{api_base}/focus-sessions?{parse.urlencode(params)}"
    return get_json(url, headers=auth_headers(token))


def main() -> int:
    parser = argparse.ArgumentParser(description="Study Focus core-flow smoke test.")
    parser.add_argument("--api-base", default=DEFAULT_API_BASE)
    parser.add_argument("--username", default="")
    parser.add_argument("--password", default=DEFAULT_PASSWORD)
    parser.add_argument("--register-first", action="store_true", help="Register a fresh user before login.")
    parser.add_argument("--use-seeded-demo", action="store_true", help="Login with seeded demo account if no username is supplied.")
    parser.add_argument("--region-id", type=int, default=1)
    parser.add_argument("--school-id", type=int, default=1)
    parser.add_argument("--college-id", type=int, default=1)
    parser.add_argument("--interrupt-wait-seconds", type=int, default=2)
    args = parser.parse_args()

    api_base = args.api_base.rstrip("/")
    username = args.username.strip()
    session_id: int | None = None
    token = ""

    if not username and args.register_first:
        username = f"smoke_user_{datetime.now().strftime('%m%d%H%M%S')}"
    elif not username and args.use_seeded_demo:
        username = DEFAULT_EXISTING_USERNAME
    elif not username:
        username = f"smoke_user_{datetime.now().strftime('%m%d%H%M%S')}"
        args.register_first = True

    print(f"[STEP 1] Health check -> {api_base.replace('/api/v1', '')}/health")
    health = get_json(f"{api_base.removesuffix('/api/v1')}/health")
    assert_true(health.get("status") == "ok", "Health endpoint did not return status=ok.")
    print("  PASS health")

    try:
        if args.register_first:
            print(f"[STEP 2] Register user -> {username}")
            registered = register_user(
                api_base=api_base,
                username=username,
                password=args.password,
                region_id=args.region_id,
                school_id=args.school_id,
                college_id=args.college_id,
            )
            assert_true(registered.get("username") == username, "Register response username mismatch.")
            print(f"  PASS register user_id={registered.get('user_id')}")
        else:
            print(f"[STEP 2] Skip register, use existing account -> {username}")

        print("[STEP 3] Login")
        token = login(api_base, username, args.password)
        print("  PASS login")

        print("[STEP 4] Read current profile")
        me = get_json(f"{api_base}/users/me", headers=auth_headers(token))
        assert_true(me.get("username") == username, "Current profile username mismatch.")
        print(f"  PASS profile nickname={me.get('nickname')}")

        print("[STEP 5] Read point balance")
        balance = get_json(f"{api_base}/points/balance", headers=auth_headers(token))
        assert_true(int(balance.get("user_id") or 0) > 0, "Point balance user_id is invalid.")
        print(
            f"  PASS points total_points={balance.get('total_points')} total_focus_minutes={balance.get('total_focus_minutes')}"
        )

        print("[STEP 6] Fetch daily question")
        question = get_json(f"{api_base}/learning/daily-question", headers=auth_headers(token))
        options = question.get("options") or []
        assert_true(bool(question.get("question_date")), "Daily question date is missing.")
        assert_true(len(options) >= 2, "Daily question options are unexpectedly empty.")
        print(f"  PASS daily question subject={question.get('subject')} options={len(options)}")

        print("[STEP 7] Create focus session")
        started = create_focus_session(api_base, token)
        session_id = int(started.get("session_id") or 0)
        assert_true(session_id > 0, "Focus session id is missing.")
        assert_true(started.get("status") == "RUNNING", "New focus session is not RUNNING.")
        print(f"  PASS focus start session_id={session_id}")

        print(f"[STEP 8] Wait {args.interrupt_wait_seconds}s and interrupt")
        time.sleep(max(0, args.interrupt_wait_seconds))
        paused = interrupt_session(api_base, token, session_id)
        assert_true(paused.get("status") == "INTERRUPTED", "Interrupted session status is not INTERRUPTED.")
        print(f"  PASS focus interrupt actual_minutes={paused.get('actual_minutes')}")

        print("[STEP 9] Resume focus session")
        resumed = resume_session(api_base, token, session_id)
        assert_true(resumed.get("status") == "RUNNING", "Resumed session status is not RUNNING.")
        print("  PASS focus resume")

        print("[STEP 10] List focus sessions")
        sessions = list_sessions(api_base, token)
        items = sessions.get("items") or []
        assert_true(any(int(item.get("session_id") or 0) == session_id for item in items), "Created session not found in session list.")
        print(f"  PASS session list total={sessions.get('total')}")

        print("[STEP 11] Abandon test session for cleanup")
        abandoned = abandon_session(api_base, token, session_id)
        assert_true(abandoned.get("status") == "ABANDONED", "Cleanup abandon did not set status=ABANDONED.")
        print("  PASS focus cleanup")
        session_id = None

        print("[STEP 12] Create feedback")
        feedback = create_feedback(api_base, token, username)
        assert_true(feedback.get("status") == "NEW", "Feedback status is not NEW.")
        print(f"  PASS feedback feedback_id={feedback.get('feedback_id')}")

        print("[STEP 13] Read my feedback list")
        feedbacks = get_json(f"{api_base}/feedback/my?page=1&page_size=10", headers=auth_headers(token))
        feedback_items = feedbacks.get("items") or []
        assert_true(any(int(item.get("feedback_id") or 0) == int(feedback.get("feedback_id") or 0) for item in feedback_items), "Created feedback not found in feedback list.")
        print(f"  PASS feedback list total={feedbacks.get('total')}")

        print("[STEP 14] Read focus leaderboard")
        leaderboard = get_json(
            f"{api_base}/leaderboards/focus?period=day&scope=school&limit=10",
            headers=auth_headers(token),
        )
        assert_true(isinstance(leaderboard.get("items"), list), "Leaderboard items is not a list.")
        print(f"  PASS leaderboard items={len(leaderboard.get('items') or [])}")

        print("\n[SMOKE TEST] ALL CORE STEPS PASSED")
        print(f"username={username}")
        print(f"api_base={api_base}")
        return 0
    except SmokeTestError as exc:
        print(f"\n[SMOKE TEST] FAILED: {exc}")
        return 1
    finally:
        if token and session_id:
            try:
                abandon_session(api_base, token, session_id)
                print(f"[CLEANUP] Abandoned session_id={session_id}")
            except Exception as cleanup_exc:  # noqa: BLE001
                print(f"[CLEANUP] Could not abandon session_id={session_id}: {cleanup_exc}")


if __name__ == "__main__":
    sys.exit(main())
