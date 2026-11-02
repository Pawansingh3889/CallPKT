# CallPKT: a practice call center, with a quality checker

CallPKT has two parts:

1. **A helpline bot you can talk to.** Open a web page, press "Start the call" and speak. An AI
   answers out loud. No phone number and no cost.
2. **A call quality checker.** It reads a call transcript and scores it out of 100, the way a
   Quality Analyst in a call center audits an agent's call.

## How a call is scored

| What is checked | Points | How |
|---|---|---|
| Opening: greeting and name or offer to help | 10 | automatic rule |
| Dead air: no silence of 10 seconds or more | 10 | automatic rule |
| Asked "anything else?" near the end | 5 | automatic rule |
| Closing: thanks and goodbye | 5 | automatic rule |
| Probing: asked questions before acting | 15 | AI judge |
| Empathy: acknowledged the customer's feelings | 15 | AI judge |
| Accuracy: correct and complete answer | 25 | AI judge |
| Professionalism: polite, no blaming | 15 | AI judge |

- **Fatal errors** make the whole score 0: rudeness, wrong information that could harm the
  customer, no identity check, hanging up, or asking for a good survey score.
- **The AI must prove every verdict with a quote from the call.** If the quote is not really in
  the call, that item is not scored and goes to a person to review.

## What we found (first test, 2 Nov 2026)

Tested on real call center calls from [CallCenterEN](https://huggingface.co/datasets/AIxBlock/92k-real-world-call-center-scripts-english)
(91,706 real English calls with personal details removed) and on our own bot's calls.

- 5 real calls averaged **36.6%**. 4 had a silence over 10 seconds, none asked "anything else?",
  and only 1 closed with thanks and goodbye.
- One "silence" came right after "Just a moment": a proper hold, not dead air. **A person should
  always check the evidence.**
- One call failed the opening because the recording started mid-call.
- The AI once quoted words that were not in the call. The quote check caught it.
- It caught a real mistake in our own bot: it said "Sure" when asked to transfer the call to a
  phone number, which it cannot do. Scored as an accuracy fail.

Five calls is a small test. It shows the checker works, not how call centers perform.

## Learn the terms

[docs/qa-glossary.md](docs/qa-glossary.md) explains the words call center QA teams use: CSAT, NPS,
FCR, AHT, calibration, fatal errors, script deviation and more.

## For developers

```bash
uv sync && cp .env.example .env                           # add a free Groq key as LLM_API_KEY
uv run uvicorn app.main:app --reload                      # the bot: open http://localhost:8000
uv run python scripts/score_call.py data/calls/*.json     # score calls
uv run python scripts/score_call.py FILES --no-llm        # rules only, no key needed
uv run pytest
```

How the code fits together is in [CLAUDE.md](CLAUDE.md). An optional real phone line (Twilio)
exists in the code but is not switched on.

Ideas borrowed (no code copied): quotes as evidence from
[call-insight-ai](https://github.com/bogdan0089/call-insight-ai), scoring layout from
[CallQA](https://github.com/kndkrakhil/CallQA). Call data license: CC BY-NC 4.0, non-commercial.
