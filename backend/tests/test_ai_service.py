import json
import unittest
from unittest.mock import patch

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
                payload={"question": "你是谁"},
                headers={"Authorization": "Bearer demo-key"},
            )

        self.assertEqual(body["choices"][0]["message"]["content"], "ok")
        self.assertEqual(len(_FakeConnection.instances), 1)
        sent = _FakeConnection.instances[0]
        self.assertEqual(sent.method, "POST")
        self.assertEqual(sent.path, "/v1/chat/completions")
        self.assertIn("application/json; charset=utf-8", sent.headers["Content-Type"])
        self.assertIn("你是谁", sent.body.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()