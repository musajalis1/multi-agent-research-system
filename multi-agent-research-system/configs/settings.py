import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    api_key: str
    model: str = "gpt-4.1-mini"
    base_url: str = "https://api.openai.com/v1"
    max_sources: int = 5

    @classmethod
    def from_env(cls):
        return cls(
            api_key=os.getenv("OPENAI_API_KEY", ""),
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            max_sources=max(1, min(10, int(os.getenv("RESEARCH_MAX_SOURCES", "5")))),
        )
