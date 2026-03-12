from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from urllib import error, request


DEFAULT_API_BASE = "http://127.0.0.1:8000/api/v1"


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def post_json(url: str, payload: dict | None, headers: dict[str, str] | None = None) -> dict:
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req_headers = {"Accept": "application/json"}
    if payload is not None:
        req_headers["Content-Type"] = "application/json; charset=utf-8"
    if headers:
        req_headers.update(headers)

    req = request.Request(url, data=body, headers=req_headers, method="POST")
    try:
        with request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"Request failed: {exc.reason}") from exc


def login(api_base: str, username: str, password: str) -> str:
    result = post_json(
        f"{api_base}/auth/login",
        {
            "username": username,
            "password": password,
        },
    )
    token = str(result.get("access_token") or "").strip()
    if not token:
        raise RuntimeError("Login succeeded but access_token is missing.")
    return token


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def session_elapsed_seconds(session: dict) -> float:
    start_at = parse_dt(session.get("start_at"))
    end_at = parse_dt(session.get("end_at")) or datetime.now(start_at.tzinfo) if start_at else None
    if not start_at or not end_at:
        return float(int(session.get("actual_minutes") or 0) * 60)
    planned_seconds = int(session.get("planned_minutes") or 0) * 60
    elapsed = max(0.0, (end_at - start_at).total_seconds())
    return min(elapsed, float(planned_seconds))


def format_seconds(total_seconds: float) -> str:
    total = max(0, int(total_seconds))
    hours = total // 3600
    minutes = (total % 3600) // 60
    seconds = total % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def abandon_if_needed(api_base: str, token: str, session_id: int) -> None:
    try:
        post_json(
            f"{api_base}/focus-sessions/{session_id}/abandon",
            {"remark": "smoke test cleanup"},
            headers=auth_headers(token),
        )
    except Exception:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test interrupt/resume exact remaining time.")
    parser.add_argument("--api-base", default=DEFAULT_API_BASE)
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--planned-minutes", type=int, default=25)
    parser.add_argument("--wait-seconds", type=int, default=12)
    parser.add_argument("--keep-session", action="store_true")
    args = parser.parse_args()

    api_base = args.api_base.rstrip("/")
    session_id = None

    try:
        token = login(api_base, args.username, args.password)
        started = post_json(
            f"{api_base}/focus-sessions/start",
            {
                "planned_minutes": args.planned_minutes,
                "lock_mode": "NONE",
                "blocked_apps": [],
                "blocked_sites": [],
                "remark": "smoke focus resume test",
            },
            headers=auth_headers(token),
        )
        session_id = int(started["session_id"])
        print(f"[FOCUS TEST] started session_id={session_id}")
        print(f"[FOCUS TEST] waiting {args.wait_seconds}s before interrupt...")
        time.sleep(args.wait_seconds)

        paused = post_json(
            f"{api_base}/focus-sessions/{session_id}/interrupt",
            {"remark": "smoke interrupt"},
            headers=auth_headers(token),
        )
        paused_elapsed = session_elapsed_seconds(paused)
        paused_remaining = args.planned_minutes * 60 - paused_elapsed
        print(f"[FOCUS TEST] paused elapsed={format_seconds(paused_elapsed)} remaining={format_seconds(paused_remaining)}")

        resumed = post_json(
            f"{api_base}/focus-sessions/{session_id}/resume",
            None,
            headers=auth_headers(token),
        )
        resumed_elapsed = session_elapsed_seconds(resumed)
        resumed_remaining = args.planned_minutes * 60 - resumed_elapsed
        diff_seconds = abs(resumed_remaining - paused_remaining)
        print(f"[FOCUS TEST] resumed elapsed={format_seconds(resumed_elapsed)} remaining={format_seconds(resumed_remaining)}")
        print(f"[FOCUS TEST] remaining-time delta={diff_seconds:.2f}s")

        if diff_seconds > 2.5:
            raise RuntimeError("Resume did not keep the saved remaining time accurately enough.")

        print("[FOCUS TEST] OK")
        return 0
    except Exception as exc:
        print(f"[FOCUS TEST] FAILED: {exc}")
        return 1
    finally:
        if session_id and not args.keep_session:
            try:
                token  # noqa: B018
            except UnboundLocalError:
                token = None
            if token:
                abandon_if_needed(api_base, token, session_id)


if __name__ == "__main__":
    sys.exit(main())