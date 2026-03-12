from __future__ import annotations

import argparse
import json
import sys
from urllib import error, request


DEFAULT_API_BASE = "http://127.0.0.1:8000/api/v1"


def post_json(url: str, payload: dict, headers: dict[str, str] | None = None) -> dict:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req_headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json",
    }
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


def ask_ai(api_base: str, token: str, question: str, system_prompt: str | None) -> dict:
    payload = {"question": question}
    if system_prompt:
        payload["system_prompt"] = system_prompt

    return post_json(
        f"{api_base}/learning/ai-chat",
        payload,
        headers={"Authorization": f"Bearer {token}"},
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test the Study Focus AI chat endpoint.")
    parser.add_argument("--api-base", default=DEFAULT_API_BASE)
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--question", default="who are you")
    parser.add_argument("--system-prompt", default="You are a helpful study assistant.")
    args = parser.parse_args()

    try:
        token = login(args.api_base.rstrip("/"), args.username, args.password)
        result = ask_ai(args.api_base.rstrip("/"), token, args.question, args.system_prompt)
    except Exception as exc:
        print(f"[AI TEST] FAILED: {exc}")
        return 1

    print("[AI TEST] OK")
    print(f"provider: {result.get('provider')}")
    print(f"model: {result.get('model')}")
    print("answer:")
    print(result.get("answer", ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())