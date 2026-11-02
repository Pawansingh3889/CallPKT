# CallPKT — an AI voicebot, built from scratch, for $0

Open the page, hit "Start the call," and talk to it, a real voice conversation with an AI,
running entirely in the browser: no phone number, no telephony provider, no subscription.
Built the same way as [AskPKT](https://github.com/Pawansingh3889/AskPKT) and
[CodeRAG-PKT](https://github.com/Pawansingh3889/CodeRAG-PKT): every piece of the call logic
is hand-written so each concept (speech-in, dialogue state, speech-out) maps to real,
readable code — no Vapi, no Bland.ai, no managed "AI phone agent" platform.

Built after being shortlisted at MyOperator (Front Deployed Engineer), whose product is
exactly this category: AI Suite (voicebots), Call Management Suite (IVR, routing, recording).
This is a small, honest demonstration of the same mechanism, built rather than bought.

## Why browser voice, not a phone number

The original plan used Twilio's free trial (`<Gather input="speech">` for STT, `<Say>` for
TTS, both included free in trial voice minutes). That's still in the repo and still works in
principle, but Twilio's trial gates real number purchase behind a paid plan in some regions —
hit that live on 15 Sep 2026 trying to buy an India-reachable number. Rather than pay for a
demo, the default path became the browser: Chrome's built-in Web Speech API
(`SpeechRecognition` for STT, `speechSynthesis` for TTS) is free forever, no account, no
trial window, no region restrictions. The conversation manager underneath
(`app/conversation.py`, `app/llm.py`) doesn't know or care which one is calling it, both
paths feed it the same way.

Total cost to run the default (browser) path: **$0**, forever, just a free-tier LLM key
(Groq's OpenAI-compatible API, or swap in any OpenAI-compatible endpoint via `.env`).

## Architecture

```
Browser: open http://localhost:8000, click "Start the call"
        │
        ▼
GET /              serves web/index.html
        │
        ▼
Web Speech API listens (SpeechRecognition, free, built into Chrome)
        │
        ▼
POST /chat  {session_id, text}
        │  conversation.py: append to history, ask the LLM for a reply,
        │  log the turn to data/calls/<session_id>.json
        ▼
{reply, hangup} back to the browser
        │
        ▼
speechSynthesis speaks the reply, then either listens again or ends the call
```

The Twilio path (optional, see below) is the same `conversation.py` behind a different
front door: `POST /voice` and `POST /gather` instead of `GET /` and `POST /chat`.

No server is even required to *test the dialogue logic itself* — see
`scripts/simulate_call.py`, which drives `conversation.py` directly from the terminal.

## Setup

```bash
uv sync
cp .env.example .env
# fill in LLM_API_KEY (free at console.groq.com/keys)
```

Test the conversation loop from the terminal first, fastest way to check the LLM key works:

```bash
uv run python scripts/simulate_call.py
```

Then run the real thing:

```bash
uv run uvicorn app.main:app --reload
```

Open **http://localhost:8000**, click "Start the call," allow microphone access, talk.
Web Speech API works on `localhost` without HTTPS, so no tunnel or deployment is needed to
try it yourself. (Chrome desktop or Android; Safari's support is inconsistent as of 2026.)

## Milestones

- [x] 1. Dialogue manager with per-session state (`app/conversation.py`), shared by both
      call paths
- [x] 2. LLM call, pluggable provider via `.env` (defaults to Groq's free tier) — `app/llm.py`
- [x] 3. Per-call transcript logging to local JSON — `app/call_log.py`
- [x] 4. Browser voice frontend, Web Speech API, no build step — `web/index.html`
- [x] 5. `/chat` endpoint wiring the browser to the dialogue manager — `app/main.py`
- [x] 6. Terminal call simulator, no browser/server needed to test — `scripts/simulate_call.py`
- [x] 7. Hand-written TwiML generation, no Twilio helper-library builder — `app/twiml.py`
- [x] 8. IVR menu (press 1 / press 2) — `app/ivr.py`
- [x] 9. Twilio webhook server (`/voice`, `/gather`) — same backend, optional front door
- [ ] 10. Twilio path going live — blocked on Twilio's trial paywall, not a code problem;
      revisit if a working number turns up another way
- [ ] 11. Optional: log each call summary into the Notion Job Hunt Tracker instead of local
      JSON, using the same `NOTION_API_KEY` pattern the WhatsApp workflow already uses

## Going live on Twilio anyway (optional, needs a working number)

1. Buy/claim a Twilio number and verify a recipient number in the console.
2. Add `TWILIO_ACCOUNT_SID` / `TWILIO_AUTH_TOKEN` / `TWILIO_PHONE_NUMBER` to `.env`.
3. Expose the server publicly: `ngrok http 8000`, or Railway for a stable URL.
4. Set the Twilio number's "A call comes in" webhook to `https://<public-url>/voice`.
5. Call the Twilio number from the verified phone.

## Call center QA reference

[docs/qa-glossary.md](docs/qa-glossary.md) lists the QA vocabulary a BPO voice process uses
(CSAT, NPS, FCR, AHT, calibration, fatal errors, script deviation, scorecard parameters,
compliance and speech analytics terms), the reference for simulating call QA on CallPKT calls.

## Call QA scorer

`scripts/score_call.py` scores a call transcript out of 100 (`app/qa_score.py`).

```bash
uv run python scripts/score_call.py data/calls/*.json              # CallPKT calls
uv run python scripts/score_call.py path/to/calls/*.json --no-llm  # rules only, no API key
```

### Rules

| Parameter | Pts | Checked by | Passes when |
|---|---|---|---|
| Opening | 10 | rule | First 60 agent words have a greeting and a name or offer to help |
| Dead air | 10 | rule | No silence of 10s or more before the agent speaks (`--dead-air` to change) |
| Further assistance | 5 | rule | "Anything else" in the last 80 agent words |
| Closing | 5 | rule | Thanks and a goodbye in the last 80 agent words |
| Probing | 15 | LLM | Agent asked questions before acting |
| Empathy | 15 | LLM | Agent acknowledged the customer's situation |
| Accuracy | 25 | LLM | Information and resolution correct and complete |
| Professionalism | 15 | LLM | Courteous, no rudeness or blaming |

### Scoring

- Score = points passed / points checked × 100.
- **Fatal errors** (rudeness, harmful misinformation, no verification, hanging up, survey begging)
  make the score 0.
- Every LLM verdict must quote the call. **A quote not found in the transcript is not scored**;
  the item goes to `REVIEW` for a human.
- Every rule result prints its evidence (matched phrase, or the silence time and the words before it).

### Findings (first runs, 2 Nov 2026)

Data: [CallCenterEN](https://huggingface.co/datasets/AIxBlock/92k-real-world-call-center-scripts-english),
91,706 real English call center transcripts, redacted, CC BY-NC 4.0. Put the zips in
`data/external/` (gitignored).

- **5 outbound calls, rules only:** average 36.6%. 4 of 5 had silence over 10s, 0 of 5 asked
  "anything else", 1 of 5 closed with thanks and goodbye.
- **Dead air needs a human:** one 34s "silence" came right after "Just a moment", a proper hold.
  CallCenterEN has no speaker labels, so every pause counts.
- **Opening fails can be the recording:** one call started mid-conversation, so no greeting exists.
- **Quote check works:** the LLM gave a greeting quote that is not in the call; probing, empathy and
  professionalism went to review instead of being scored.
- **It caught a real CallPKT bug:** the bot said "Sure" to "can I redirect this to my number"
  (it can't). Accuracy failed with that quote.

Small sample: these show the scorer working, not call center benchmarks.

Ideas borrowed, code not: quote-backed verdicts from
[call-insight-ai](https://github.com/bogdan0089/call-insight-ai); the rubric-plus-flags shape
from [CallQA](https://github.com/kndkrakhil/CallQA).

## What this is not

Not a replacement for MyOperator's actual product (multi-tenant, carrier-grade, years of
engineering). It's a demo of the mechanism at a scale one person can build and explain line
by line, which is the point: interview material, not a competitor.
