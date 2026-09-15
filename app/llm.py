"""The dialogue "brain": one call to an OpenAI-compatible chat completions
endpoint. Defaults to Groq's free tier, but any OpenAI-compatible endpoint
works by changing LLM_BASE_URL/LLM_MODEL — nothing here is Groq-specific.
"""

import os

import httpx

SYSTEM_PROMPT = (
    "You are the voice assistant answering a phone call on CallPKT, a small "
    "personal demo project. Keep every reply to one or two short sentences: "
    "this is read aloud over a phone line, not read on a screen. Be warm and "
    "direct. If the caller says goodbye, thanks, or bye, end your reply with "
    "a short goodbye and nothing else."
)


class LLMConfigError(RuntimeError):
    """Raised when required LLM configuration is missing. Never silently
    fall back to a canned reply here — a misconfigured demo should fail
    loudly during setup, not mid-call."""


def _client_config() -> tuple[str, str, str]:
    api_key = os.environ.get("LLM_API_KEY")
    base_url = os.environ.get("LLM_BASE_URL", "https://api.groq.com/openai/v1")
    model = os.environ.get("LLM_MODEL", "openai/gpt-oss-20b")
    if not api_key:
        raise LLMConfigError(
            "LLM_API_KEY is not set. Get a free key at console.groq.com and put it "
            "in .env before starting a real call — scripts/simulate_call.py needs "
            "this too."
        )
    return api_key, base_url, model


def reply(history: list[tuple[str, str]]) -> str:
    """history is a list of (role, text) pairs, role in {'user', 'assistant'}.
    Returns the assistant's next line."""
    api_key, base_url, model = _client_config()
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend({"role": role, "content": text} for role, text in history)

    response = httpx.post(
        f"{base_url}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": model, "messages": messages, "temperature": 0.6, "max_tokens": 120},
        timeout=15.0,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()
