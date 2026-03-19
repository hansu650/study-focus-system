"""AI provider adapter.

Supports OpenAI-compatible and Anthropic-compatible providers.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from http.client import HTTPConnection, HTTPException, HTTPSConnection
from json import JSONDecodeError
from urllib.parse import urlparse

from app.core.config import settings


@dataclass
class AIChatResult:
    """Unified AI chat response."""

    answer: str
    provider: str
    model: str


class AIService:
    """AI service wrapper."""

    PLACEHOLDER_KEYS = {"", "YOUR_API_KEY", "CHANGE_ME", "PLEASE_CHANGE_ME"}
    OPENAI_PROVIDERS = {"openai_compatible", "openai", "openai-compatible"}
    ANTHROPIC_PROVIDERS = {
        "anthropic_compatible",
        "anthropic",
        "anthropic-compatible",
        "anthropic_messages",
    }

    @staticmethod
    def is_enabled() -> bool:
        """Return whether AI config is available."""

        api_key = (settings.resolved_ai_api_key or "").strip()
        return bool(settings.ai_api_base and api_key and api_key not in AIService.PLACEHOLDER_KEYS and settings.ai_model)

    @staticmethod
    def chat(question: str, system_prompt: str = "You are a helpful study assistant.") -> AIChatResult:
        """Route chat request to configured provider format."""

        if not AIService.is_enabled():
            raise ValueError("AI is not configured. Set AI_API_BASE / AI_API_KEY / AI_MODEL.")

        provider = (settings.ai_provider or "openai_compatible").strip().lower()
        if provider in AIService.OPENAI_PROVIDERS:
            answer = AIService._chat_openai(question=question, system_prompt=system_prompt)
        elif provider in AIService.ANTHROPIC_PROVIDERS:
            answer = AIService._chat_anthropic(question=question, system_prompt=system_prompt)
        else:
            raise ValueError("Unsupported AI_PROVIDER. Use openai_compatible or anthropic_compatible.")

        return AIChatResult(answer=answer, provider=settings.ai_provider, model=settings.ai_model)

    @staticmethod
    def _chat_openai(question: str, system_prompt: str) -> str:
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {settings.resolved_ai_api_key}",
        }
        errors: list[str] = []

        attempts = [
            (
                AIService._build_openai_endpoint(settings.ai_api_base),
                {
                    "model": settings.ai_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": question},
                    ],
                    "temperature": 0.4,
                },
            ),
            (
                AIService._build_openai_responses_endpoint(settings.ai_api_base),
                {
                    "model": settings.ai_model,
                    "instructions": system_prompt,
                    "input": question,
                    "temperature": 0.4,
                },
            ),
        ]

        for endpoint, payload in attempts:
            try:
                body = AIService._post_json(
                    endpoint=endpoint,
                    payload=payload,
                    headers=headers,
                )
            except RuntimeError as exc:
                errors.append(str(exc))
                continue

            answer = AIService._extract_openai_answer(body)
            if answer:
                return answer

            provider_error = AIService._extract_provider_error(body)
            if provider_error:
                errors.append(provider_error)
            else:
                errors.append(f"AI provider returned no readable answer from {endpoint}.")

        detail = "; ".join(dict.fromkeys(errors))
        if detail:
            raise RuntimeError(detail)
        raise RuntimeError("AI provider returned no readable answer after chat/completions and responses fallback.")

    @staticmethod
    def _chat_anthropic(question: str, system_prompt: str) -> str:
        payload = {
            "model": settings.ai_model,
            "max_tokens": 1024,
            "temperature": 0.4,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": question},
            ],
        }

        endpoint = AIService._build_anthropic_endpoint(settings.ai_api_base)
        body = AIService._post_json(
            endpoint=endpoint,
            payload=payload,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "x-api-key": settings.resolved_ai_api_key,
                "anthropic-version": "2023-06-01",
                "Authorization": f"Bearer {settings.resolved_ai_api_key}",
            },
        )

        answer = AIService._extract_anthropic_answer(body)
        if not answer:
            raise RuntimeError("AI provider returned empty answer.")
        return answer

    @staticmethod
    def _post_json(endpoint: str, payload: dict, headers: dict[str, str]) -> dict:
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        connection, path = AIService._build_connection(endpoint)
        request_headers = AIService._prepare_headers(headers, len(body))

        try:
            connection.request("POST", path, body=body, headers=request_headers)
            response = connection.getresponse()
            raw = response.read().decode("utf-8", errors="replace")
        except UnicodeEncodeError as exc:
            raise RuntimeError(
                "AI request encoding failed. Please verify the provider URL and API key format, then retry."
            ) from exc
        except OSError as exc:
            raise RuntimeError(f"Failed to reach AI provider: {exc}") from exc
        except HTTPException as exc:
            raise RuntimeError(f"AI provider connection failed: {exc}") from exc
        finally:
            connection.close()

        if response.status >= 400:
            detail = raw.strip()
            if detail:
                raise RuntimeError(f"AI provider returned HTTP {response.status}: {detail[:400]}")
            raise RuntimeError(f"AI provider returned HTTP {response.status}.")

        if not raw.strip():
            return {}

        try:
            return json.loads(raw)
        except JSONDecodeError as exc:
            raise RuntimeError(f"AI provider returned non-JSON response: {raw[:200]}") from exc

    @staticmethod
    def _build_connection(endpoint: str) -> tuple[HTTPConnection | HTTPSConnection, str]:
        parsed = urlparse(endpoint)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise RuntimeError("AI_API_BASE must be a valid http(s) URL.")

        path = parsed.path or "/"
        if parsed.query:
            path = f"{path}?{parsed.query}"

        port = parsed.port
        if parsed.scheme == "https":
            return HTTPSConnection(parsed.hostname, port=port, timeout=30), path
        return HTTPConnection(parsed.hostname, port=port, timeout=30), path

    @staticmethod
    def _prepare_headers(headers: dict[str, str], body_length: int) -> dict[str, str]:
        cleaned: dict[str, str] = {
            str(key): str(value).strip()
            for key, value in headers.items()
            if value is not None and str(value).strip()
        }
        cleaned.setdefault("Content-Type", "application/json; charset=utf-8")
        cleaned.setdefault("Accept", "application/json")
        cleaned["Content-Length"] = str(body_length)
        return cleaned

    @staticmethod
    def _extract_openai_answer(body: dict) -> str:
        choices = body.get("choices") or []
        if choices:
            for choice in choices:
                if not isinstance(choice, dict):
                    continue

                message_answer = AIService._extract_message_answer(choice.get("message"))
                if message_answer:
                    return message_answer

                delta_answer = AIService._extract_message_answer(choice.get("delta"))
                if delta_answer:
                    return delta_answer

                content_answer = AIService._extract_content_answer(choice.get("content"))
                if content_answer:
                    return content_answer

                for key in ("text", "output_text", "answer"):
                    value = choice.get(key)
                    if isinstance(value, str) and value.strip():
                        return value.strip()

        for key in ("output_text", "answer", "text", "completion"):
            value = body.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

        message_answer = AIService._extract_message_answer(body.get("message"))
        if message_answer:
            return message_answer

        content_answer = AIService._extract_content_answer(body.get("content"))
        if content_answer:
            return content_answer

        output_answer = AIService._extract_output_answer(body.get("output"))
        if output_answer:
            return output_answer

        for key in ("data", "result", "response"):
            nested = body.get(key)
            if isinstance(nested, dict):
                nested_answer = AIService._extract_openai_answer(nested)
                if nested_answer:
                    return nested_answer

        return ""

    @staticmethod
    def _extract_anthropic_answer(body: dict) -> str:
        content = body.get("content")
        if isinstance(content, list):
            texts: list[str] = []
            for item in content:
                if isinstance(item, dict):
                    text = str(item.get("text", "")).strip()
                    if text:
                        texts.append(text)
            if texts:
                return "\n".join(texts).strip()

        output_text = body.get("output_text")
        if isinstance(output_text, str) and output_text.strip():
            return output_text.strip()

        return AIService._extract_openai_answer(body)

    @staticmethod
    def _extract_message_answer(message: object) -> str:
        if isinstance(message, str) and message.strip():
            return message.strip()

        if isinstance(message, dict):
            return AIService._extract_content_answer(message.get("content", ""))

        return ""

    @staticmethod
    def _extract_content_answer(content: object) -> str:
        if isinstance(content, str):
            return content.strip()

        if isinstance(content, dict):
            for key in ("text", "content", "answer"):
                extracted = AIService._extract_content_answer(content.get(key))
                if extracted:
                    return extracted
            return ""

        if isinstance(content, list):
            texts: list[str] = []
            for item in content:
                if isinstance(item, dict):
                    item_type = str(item.get("type", "")).strip().lower()
                    if item_type in {"text", "output_text", "input_text"}:
                        text = str(item.get("text", "")).strip()
                        if text:
                            texts.append(text)
                            continue

                    extracted = AIService._extract_content_answer(item.get("content"))
                    if extracted:
                        texts.append(extracted)
                        continue

                    text_value = str(item.get("text", "")).strip()
                    if text_value:
                        texts.append(text_value)
                elif isinstance(item, str) and item.strip():
                    texts.append(item.strip())

            return "\n".join(texts).strip()

        return ""

    @staticmethod
    def _extract_output_answer(output: object) -> str:
        if isinstance(output, list):
            texts: list[str] = []
            for item in output:
                if not isinstance(item, dict):
                    continue

                extracted = AIService._extract_content_answer(item.get("content"))
                if extracted:
                    texts.append(extracted)
                    continue

                for key in ("text", "output_text"):
                    value = item.get(key)
                    if isinstance(value, str) and value.strip():
                        texts.append(value.strip())
                        break

            return "\n".join(texts).strip()

        return ""

    @staticmethod
    def _extract_provider_error(body: dict) -> str:
        error = body.get("error")
        if isinstance(error, str) and error.strip():
            return error.strip()

        if isinstance(error, dict):
            for key in ("message", "detail", "type"):
                value = error.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()

        detail = body.get("detail")
        if isinstance(detail, str) and detail.strip():
            return detail.strip()

        return ""

    @staticmethod
    def _build_openai_endpoint(base_url: str) -> str:
        base = base_url.rstrip("/")
        if base.endswith("/chat/completions"):
            return base
        return f"{base}/chat/completions"

    @staticmethod
    def _build_openai_responses_endpoint(base_url: str) -> str:
        base = base_url.rstrip("/")
        if base.endswith("/responses"):
            return base
        return f"{base}/responses"

    @staticmethod
    def _build_anthropic_endpoint(base_url: str) -> str:
        base = base_url.rstrip("/")
        if base.endswith("/v1/messages") or base.endswith("/messages"):
            return base
        if base.endswith("/v1"):
            return f"{base}/messages"
        return f"{base}/v1/messages"
