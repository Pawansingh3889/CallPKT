"""The dialogue "brain": one call to an OpenAI-compatible chat completions
endpoint. Defaults to Groq's free tier, but any OpenAI-compatible endpoint
works by changing LLM_BASE_URL/LLM_MODEL — nothing here is Groq-specific.
"""

import os

import httpx

SYSTEM_PROMPT = (
    "You are the voice assistant on CallPKT, a small personal demo project built by "
    "Pawan Singh Kapkoti. Keep every reply to one or two short sentences: this is read "
    "aloud, not read on a screen. Be warm and direct.\n\n"
    "What CallPKT actually is: a call running entirely in the caller's own web browser, "
    "using the browser's built-in Web Speech API for listening and speaking. There is no "
    "real phone number, no telephony provider, and no way to forward, redirect, or connect "
    "this conversation to an actual phone call — say so plainly and briefly if asked, don't "
    "hedge or pretend it might be possible. Never repeat the caller's question back as your "
    "own reply.\n\n"
    "If the caller says goodbye, thanks, or bye, end your reply with a short goodbye and "
    "nothing else."
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
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend({"role": role, "content": text} for role, text in history)
    # 400, not 120: reasoning models (gpt-oss included) spend tokens on an internal
    # reasoning trace before writing the visible reply, and too tight a cap here
    # silently truncates the reasoning step and leaves `content` empty. Learned by
    # hitting it live, not from the docs.
    return complete(messages, temperature=0.6, max_tokens=400, timeout=15.0)


def complete(
    messages: list[dict[str, str]], *, temperature: float, max_tokens: int, timeout: float
) -> str:
    """One chat completion against the configured endpoint. Raises on an empty reply."""
    api_key, base_url, model = _client_config()
    response = httpx.post(
        f"{base_url}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
        timeout=timeout,
    )
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"].strip()
    if not content:
        raise LLMConfigError(
            f"Model '{model}' returned an empty reply (finish_reason="
            f"{data['choices'][0].get('finish_reason')!r}). Likely max_tokens is still too "
            "tight for this model's reasoning overhead, or the model refused the request."
        )
    return content
