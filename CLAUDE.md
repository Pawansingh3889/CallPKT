# CallPKT

An AI voicebot, hand-built end to end. Default path is a free browser voice
call (Web Speech API, no phone number, no telephony provider, no cost). A
Twilio phone path exists too but is optional/stretch, Twilio's trial
account gated real number purchase behind a paid plan when this was tried
live on 15 Sep 2026. See README.md for the full architecture diagram and
milestone list.

## Architecture

```
web/index.html      → browser frontend: Web Speech API (STT + TTS), no build step
app/main.py           → FastAPI: GET / (serves the page), POST /chat (browser path),
                          POST /voice + POST /gather (optional Twilio path)
app/conversation.py     → the dialogue manager: per-session state, turn limit,
                            goodbye detection; the one piece both call paths share
app/llm.py                → the LLM call; pluggable OpenAI-compatible endpoint,
                              defaults to Groq's free tier
app/call_log.py              → per-call transcript logged to local JSON
app/qa_score.py              → QA scorecard: rule checks + quote-verified LLM checks
scripts/score_call.py        → CLI for the scorer (CallPKT logs and CallCenterEN JSON)
app/twiml.py                   → hand-written TwiML (Twilio path only)
app/ivr.py                       → IVR menu logic (Twilio path only)
app/security.py                    → Twilio request-signature validation (stubbed
                                       until a real TWILIO_AUTH_TOKEN exists to test against)
```

## Twilio phone path (optional, needs a working number)

1. Buy/claim a Twilio number and verify a recipient number in the console.
2. Add `TWILIO_ACCOUNT_SID` / `TWILIO_AUTH_TOKEN` / `TWILIO_PHONE_NUMBER` to `.env`.
3. Expose the server publicly: `ngrok http 8000`, or Railway for a stable URL.
4. Set the Twilio number's "A call comes in" webhook to `https://<public-url>/voice`.
5. Call the Twilio number from the verified phone.

## Dev commands

```bash
uv sync
uv run pytest
uv run ruff check .
uv run uvicorn app.main:app --reload   # then open http://localhost:8000
uv run python scripts/simulate_call.py # test the dialogue manager with no server at all
```

## A real bug worth remembering, not just a note

`openai/gpt-oss-20b` (the default Groq model) is a reasoning model, it
spends tokens on an internal reasoning trace before writing the visible
reply. `max_tokens` set too tight (120 was the original guess) silently
truncates the reasoning step and returns an **empty** `content` field, not
an error. `app/llm.py` now raises loudly on empty content instead of
returning silence to a live call, and `max_tokens=400` gives the reasoning
room to finish. If a reasoning model ever goes back to returning empty
replies, suspect the token budget first.

## What NOT to do

- **Don't make the phone-call path the default without a working Twilio
  number in hand.** The browser path is default for a real reason (it
  cost $0 the day this was hit live), not an oversight.
- **Don't let `app/llm.py` return an empty string on a failure.** A silent
  empty reply is dead air on a live call, worse than a visible error.
- **Don't add a system-prompt claim about what CallPKT can do without
  checking it's true.** The redirect-to-a-real-phone bug happened exactly
  because the model wasn't told the truth about its own limits.
