"""Central configuration loaded from environment / .env."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the LLM provider and agent loop."""

    api_key: str
    base_url: str
    model: str
    max_retries: int
    request_timeout: float

    @classmethod
    def load(cls) -> "Settings":
        return cls(
            api_key=os.getenv("DEEPSEEK_API_KEY", ""),
            base_url=os.getenv("LLM_BASE_URL", "https://api.deepseek.com"),
            model=os.getenv("LLM_MODEL", "deepseek-chat"),
            max_retries=int(os.getenv("AGENT_MAX_RETRIES", "3")),
            request_timeout=float(os.getenv("LLM_TIMEOUT", "120")),
        )

    @property
    def has_api_key(self) -> bool:
        return bool(self.api_key.strip())


settings = Settings.load()
