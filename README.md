# CallPKT — an AI voicebot, built from scratch, for $0

A phone number you can call that runs a hand-written IVR + conversational AI loop, built
the same way as [AskPKT](https://github.com/Pawansingh3889/AskPKT) and
[CodeRAG-PKT](https://github.com/Pawansingh3889/CodeRAG-PKT): every piece of the call logic
is hand-written so each concept (speech-in, dialogue state, speech-out, IVR menu) maps to
real, readable code — no Vapi, no Bland.ai, no managed "AI phone agent" platform.

Built after being shortlisted at MyOperator (Front Deployed Engineer), whose product is
exactly this category: AI Suite (voicebots), Call Management Suite (IVR, routing, recording).
This is a small, honest demonstration of the same mechanism, built rather than bought.

## Why this design

Twilio's own `<Gather input="speech">` (speech-to-text) and `<Say>` (text-to-speech, Amazon
Polly voices) are included free inside trial voice minutes — no per-minute AI platform fee
on top. The only thing Twilio doesn't do for you is decide *what to say back*, which is what
this repo builds: a small dialogue manager that takes the caller's transcribed speech, asks
an LLM for a reply, and hands the reply back to Twilio as `<Say>`.

Total cost to run this demo: **$0**, inside Twilio's free trial (75 voice minutes, 100 SMS,
5 verified numbers, no credit card) plus a free-tier LLM (Groq's OpenAI-compatible API, free
tier, or swap in any OpenAI-compatible endpoint via `.env`).

## Architecture

```
Caller dials Twilio number
        │
        ▼
POST /voice   (Twilio webhook, first ring)
        │  returns TwiML: greeting + <Gather input="speech dtmf">
        ▼
Caller speaks or presses a digit
        │
        ▼
POST /gather  (Twilio webhook, per turn)
        │  digit 1 → canned IVR info (Call Management Suite-style menu)
        │  digit 2 / speech → conversation.py asks the LLM for a reply
        │  every turn logged to data/calls/<CallSid>.json
        ▼
TwiML <Say> reply + another <Gather>, or <Hangup> after goodbye / 6 turns
```

No webhook server is required to *test the dialogue logic itself* — see
`scripts/simulate_call.py`, which drives `conversation.py` directly from the terminal with
no Twilio account needed at all. Get the conversation right for free before spending any of
the 75 trial minutes on real calls.

## Setup

```bash
uv sync
cp .env.example .env
# fill in GROQ_API_KEY (free at console.groq.com) once you have one
```

Test the conversation loop with no phone, no Twilio account, no cost:

```bash
uv run python scripts/simulate_call.py
```

## Going live (once you have a free Twilio trial account)

1. Sign up at [twilio.com/try-twilio](https://www.twilio.com/try-twilio) — no credit card.
2. Buy/claim your trial number, verify your own phone number as a recipient (trial accounts
   can only call verified numbers, that's fine for a personal demo).
3. Add `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` to `.env`.
4. Run the server: `uv run uvicorn app.main:app --reload`
5. Expose it publicly (pick one, both are free):
   - `ngrok http 8000` (quick, URL changes each restart on the free tier)
   - Railway free tier (stable URL, matches how Elenchus is already deployed)
6. In the Twilio console, set the number's "A call comes in" webhook to
   `https://<your-public-url>/voice`.
7. Call your Twilio number from your verified phone.

## Milestones

- [x] 1. TwiML generation, hand-written, no Twilio helper-library TwiML builder — `app/twiml.py`
- [x] 2. IVR menu (press 1 / press 2) — `app/ivr.py`
- [x] 3. Dialogue manager with per-call session state, keyed by CallSid — `app/conversation.py`
- [x] 4. LLM call, pluggable provider via `.env` (defaults to Groq's free tier) — `app/llm.py`
- [x] 5. Per-call transcript logging to local JSON — `app/call_log.py`
- [x] 6. FastAPI webhook server (`/voice`, `/gather`, `/status`) — `app/main.py`
- [x] 7. Terminal call simulator, no Twilio/phone needed to test — `scripts/simulate_call.py`
- [ ] 8. Twilio request-signature validation (`app/security.py` stubbed, needs a live
      Twilio auth token to test against)
- [ ] 9. Public deployment (ngrok for testing, or Railway for a stable demo URL) — needs your
      own Twilio account and a deploy target, not something to do from a repo alone
- [ ] 10. Optional: log each call summary into the Notion Job Hunt Tracker instead of local
      JSON, using the same `NOTION_API_KEY` pattern the WhatsApp workflow already uses

## What this is not

Not a replacement for MyOperator's actual product (multi-tenant, carrier-grade, years of
engineering). It's a demo of the mechanism at a scale one person can build and explain line
by line, which is the point: interview material, not a competitor.
