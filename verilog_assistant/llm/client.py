"""Provider-agnostic LLM client.

DeepSeek and Qwen (DashScope) both expose OpenAI-compatible APIs, so we use
the `openai` SDK and switch providers purely via base_url + model in .env.
"""

from __future__ import annotations

import time

from openai import OpenAI

from verilog_assistant.config import Settings, settings


class LLMError(RuntimeError):
    """Raised when the LLM cannot be reached or is misconfigured."""


class LLMClient:
    """Thin wrapper around an OpenAI-compatible chat endpoint with retry."""

    def __init__(self, cfg: Settings | None = None) -> None:
        self.cfg = cfg or settings
        if not self.cfg.has_api_key:
            raise LLMError(
                "No API key set. Copy .env.example to .env and set DEEPSEEK_API_KEY."
            )
        self._client = OpenAI(
            api_key=self.cfg.api_key,
            base_url=self.cfg.base_url,
            timeout=self.cfg.request_timeout,
        )

    def generate(self, prompt: str, system: str = "", temperature: float = 0.2) -> str:
        """Return the model's text completion for `prompt`."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        last_err: Exception | None = None
        for attempt in range(3):
            try:
                resp = self._client.chat.completions.create(
                    model=self.cfg.model,
                    messages=messages,
                    temperature=temperature,
                )
                return resp.choices[0].message.content or ""
            except Exception as exc:  # noqa: BLE001 - surface as LLMError after retries
                last_err = exc
                time.sleep(2 * (attempt + 1))
        raise LLMError(f"LLM request failed after retries: {last_err}")
