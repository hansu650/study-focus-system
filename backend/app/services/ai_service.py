"""AI provider adapter.

Supports OpenAI-compatible and Anthropic-compatible providers.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from urllib import error, request

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
        payload = {
            "model": settings.ai_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ],
            "temperature": 0.4,
        }

        endpoint = AIService._build_openai_endpoint(settings.ai_api_base)
        body = AIService._post_json(
            endpoint=endpoint,
            payload=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.resolved_ai_api_key}",
            },
        )

        answer = AIService._extract_openai_answer(body)
        if not answer:
            raise RuntimeError("AI provider returned empty answer.")
        return answer

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
                "Content-Type": "application/json",
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
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(endpoint, data=data, headers=headers, method="POST")

        try:
            with request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw)
        except error.HTTPError as exc:
            detail = ""
            try:
                detail = exc.read().decode("utf-8").strip()
            except Exception:
                detail = ""
            if detail:
                raise RuntimeError(f"AI provider returned HTTP {exc.code}: {detail[:400]}") from exc
            raise RuntimeError(f"AI provider returned HTTP {exc.code}.") from exc
        except error.URLError as exc:
            raise RuntimeError(f"Failed to reach AI provider: {exc.reason}") from exc

    @staticmethod
    def _extract_openai_answer(body: dict) -> str:
        choices = body.get("choices") or []
        if not choices:
            return ""

        message = choices[0].get("message", {}) if isinstance(choices[0], dict) else {}
        content = message.get("content", "")

        if isinstance(content, str):
            return content.strip()

        if isinstance(content, list):
            texts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text = str(item.get("text", "")).strip()
                    if text:
                        texts.append(text)
            return "\n".join(texts).strip()

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

        # Fallback: some providers still return OpenAI-like structure.
        return AIService._extract_openai_answer(body)

    @staticmethod
    def _build_openai_endpoint(base_url: str) -> str:
        base = base_url.rstrip("/")
        if base.endswith("/chat/completions"):
            return base
        return f"{base}/chat/completions"

    @staticmethod
    def _build_anthropic_endpoint(base_url: str) -> str:
        base = base_url.rstrip("/")
        if base.endswith("/v1/messages") or base.endswith("/messages"):
            return base
        if base.endswith("/v1"):
            return f"{base}/messages"
        return f"{base}/v1/messages"

