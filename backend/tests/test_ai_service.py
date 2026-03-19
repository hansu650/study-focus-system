import json
import unittest
from unittest.mock import patch

from app.core.config import settings
from app.services.ai_service import AIService


class _FakeResponse:
    def __init__(self, status: int, body: dict) -> None:
        self.status = status
        self._body = json.dumps(body, ensure_ascii=False).encode("utf-8")

    def read(self) -> bytes:
        return self._body


class _FakeConnection:
    instances: list["_FakeConnection"] = []

    def __init__(self, host: str, port=None, timeout: int = 30) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self.method = None
        self.path = None
        self.body = None
        self.headers = None
        _FakeConnection.instances.append(self)

    def request(self, method: str, path: str, body: bytes, headers: dict[str, str]) -> None:
        self.method = method
        self.path = path
        self.body = body
        self.headers = headers

    def getresponse(self):
        return _FakeResponse(200, {"choices": [{"message": {"content": "ok"}}]})

    def close(self) -> None:
        return None


class AIServiceTransportTests(unittest.TestCase):
    def tearDown(self) -> None:
        _FakeConnection.instances.clear()

    def test_post_json_sends_utf8_body_for_chinese_question(self) -> None:
        with patch("app.services.ai_service.HTTPSConnection", _FakeConnection):
            body = AIService._post_json(
                endpoint="https://example.com/v1/chat/completions",
                payload={"question": "你是谁？"},
                headers={"Authorization": "Bearer demo-key"},
            )

        self.assertEqual(body["choices"][0]["message"]["content"], "ok")
        self.assertEqual(len(_FakeConnection.instances), 1)
        sent = _FakeConnection.instances[0]
        self.assertEqual(sent.method, "POST")
        self.assertEqual(sent.path, "/v1/chat/completions")
        self.assertIn("application/json; charset=utf-8", sent.headers["Content-Type"])
        self.assertIn("你是谁？", sent.body.decode("utf-8"))

    def test_extract_openai_answer_supports_choice_text_payload(self) -> None:
        body = {"choices": [{"text": "legacy completion text"}]}
        self.assertEqual(AIService._extract_openai_answer(body), "legacy completion text")

    def test_chat_openai_falls_back_to_responses_when_primary_answer_is_empty(self) -> None:
        calls: list[str] = []

        def fake_post(endpoint: str, payload: dict, headers: dict[str, str]) -> dict:
            calls.append(endpoint)
            if endpoint.endswith("/chat/completions"):
                return {"choices": [{"message": {"content": ""}}]}
            return {"output_text": "fallback answer"}

        with patch.object(settings, "ai_api_base", "https://example.com/v1"):
            with patch.object(settings, "ai_api_key", "demo-key"):
                with patch.object(settings, "ai_model", "gpt-4o-mini"):
                    with patch.object(AIService, "_post_json", side_effect=fake_post):
                        answer = AIService._chat_openai("hello", "You are helpful.")

        self.assertEqual(answer, "fallback answer")
        self.assertEqual(
            calls,
            [
                "https://example.com/v1/chat/completions",
                "https://example.com/v1/responses",
            ],
        )


if __name__ == "__main__":
    unittest.main()
