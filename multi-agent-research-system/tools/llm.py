"""Minimal OpenAI-compatible chat-completions adapter."""
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class LLMError(RuntimeError):
    pass


class ChatLLM:
    def __init__(self, api_key: str, model: str, base_url: str):
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for live research; use --demo for an offline example")
        if not base_url.startswith("https://"):
            raise ValueError("OPENAI_BASE_URL must use HTTPS")
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    def complete(self, system: str, user: str) -> str:
        payload = json.dumps({"model": self.model, "temperature": 0.2,
                              "max_tokens": 1800,
                              "messages": [{"role": "system", "content": system},
                                           {"role": "user", "content": user}]}).encode()
        request = Request(self.base_url + "/chat/completions", data=payload,
                          headers={"Authorization": "Bearer " + self.api_key,
                                   "Content-Type": "application/json"}, method="POST")
        try:
            with urlopen(request, timeout=60) as response:
                data = json.load(response)
            return data["choices"][0]["message"]["content"]
        except (HTTPError, URLError, KeyError, IndexError, ValueError) as exc:
            raise LLMError(f"Chat completion failed: {exc}") from exc
