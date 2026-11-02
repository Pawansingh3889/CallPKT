"""Call QA scorer: audits one call transcript against a voice-process QA scorecard.

Two kinds of check, as mapped in docs/qa-glossary.md section 8:
- rule checks the transcript proves on its own: opening, dead air, further assistance, closing
- judgement checks an LLM makes: probing, empathy, accuracy, professionalism, fatal errors.
  Every LLM verdict must quote the call. A quote that is not in the transcript is thrown out
  and the item goes to human review instead of being scored (idea from
  github.com/bogdan0089/call-insight-ai).

Reads CallPKT call logs (data/calls/*.json) and CallCenterEN transcripts
(huggingface.co/datasets/AIxBlock/92k-real-world-call-center-scripts-english).
"""

import json
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from itertools import pairwise
from pathlib import Path

from app import llm

DEAD_AIR_SECONDS = 10.0  # calibration knob: clients set 10 to 15 s in their SLA
TURN_GAP_SECONDS = 1.5  # CallCenterEN has no turns, only timed words; split on pauses
OPENING_WORDS = 60
CLOSING_WORDS = 80

WEIGHTS = {
    "opening": 10,
    "probing": 15,
    "empathy": 15,
    "accuracy": 25,
    "professionalism": 15,
    "dead_air": 10,
    "further_assistance": 5,
    "closing": 5,
}
JUDGED = ("probing", "empathy", "accuracy", "professionalism")


class TranscriptFormatError(ValueError):
    """The file is not a transcript format this scorer reads."""


class QAScoreError(RuntimeError):
    """The LLM judge returned something that cannot be scored."""


@dataclass(frozen=True)
class Turn:
    speaker: str | None  # "agent", "customer", or None when the source has no labels
    text: str
    start: float  # seconds from the start of the call
    end: float


@dataclass(frozen=True)
class Call:
    call_id: str
    turns: list[Turn]

    @property
    def duration(self) -> float:
        return self.turns[-1].end - self.turns[0].start

    @property
    def has_speakers(self) -> bool:
        return any(t.speaker for t in self.turns)

    def agent_text(self) -> str:
        turns = [t for t in self.turns if t.speaker == "agent"] if self.has_speakers else self.turns
        return " ".join(t.text for t in turns)


@dataclass(frozen=True)
class Check:
    parameter: str
    passed: bool
    evidence: str


@dataclass
class Scorecard:
    call_id: str
    duration: float
    checks: list[Check]
    fatal_errors: list[Check] = field(default_factory=list)
    needs_review: list[str] = field(default_factory=list)

    @property
    def score(self) -> float:
        if self.fatal_errors:
            return 0.0
        possible = sum(WEIGHTS[c.parameter] for c in self.checks)
        earned = sum(WEIGHTS[c.parameter] for c in self.checks if c.passed)
        return round(100 * earned / possible, 1)


# ---------- loading ----------


def load(path: Path) -> Call:
    data = json.loads(path.read_text())
    if "turns" in data:
        return _load_callpkt(data)
    if "words" in data:
        return _load_callcenteren(data, path.stem)
    raise TranscriptFormatError(
        f"{path}: expected a CallPKT log ('turns') or CallCenterEN ('words')"
    )


def _load_callpkt(data: dict) -> Call:
    roles = {"assistant": "agent", "user": "customer"}
    raw = data["turns"]
    if not raw:
        raise TranscriptFormatError(f"call {data['call_sid']} has no turns")
    t0 = datetime.fromisoformat(raw[0]["at"])
    turns = []
    for t in raw:
        if t["role"] not in roles:
            raise TranscriptFormatError(f"unknown role {t['role']!r} in call {data['call_sid']}")
        at = (datetime.fromisoformat(t["at"]) - t0).total_seconds()
        turns.append(Turn(roles[t["role"]], t["text"], at, at))
    return Call(data["call_sid"], turns)


def _load_callcenteren(data: dict, call_id: str) -> Call:
    words = data["words"]
    if not words:
        raise TranscriptFormatError(f"call {call_id} has no words")
    turns, chunk = [], [words[0]]
    for prev, word in pairwise(words):
        if (word["start"] - prev["end"]) / 1000 >= TURN_GAP_SECONDS:
            turns.append(_chunk_to_turn(chunk))
            chunk = []
        chunk.append(word)
    turns.append(_chunk_to_turn(chunk))
    return Call(call_id, turns)


def _chunk_to_turn(words: list[dict]) -> Turn:
    text = " ".join(w["text"] for w in words)
    return Turn(None, text, words[0]["start"] / 1000, words[-1]["end"] / 1000)


# ---------- rule checks ----------

_GREETING = re.compile(
    r"\b(hello|hi|good (morning|afternoon|evening|day)|thank you for calling|welcome)\b"
)
_INTRO = re.compile(r"\b(my name is|this is|calling from|how (can|may) i (help|assist))\b")
_FURTHER = re.compile(r"\banything else\b")
_THANKS = re.compile(r"\b(thank you|thanks)\b")
_BYE = re.compile(
    r"\b(bye|goodbye|have a (great|good|nice|wonderful|lovely) (day|evening|one|weekend))\b"
)


def _norm(text: str) -> str:
    return " ".join(
        re.sub(r"[^a-z0-9 ]", " ", text.lower().replace("’", "'").replace("'", "")).split()
    )


def _clock(seconds: float) -> str:
    return f"{int(seconds // 60)}:{int(seconds % 60):02d}"


def rule_checks(call: Call, dead_air_seconds: float = DEAD_AIR_SECONDS) -> list[Check]:
    words = _norm(call.agent_text()).split()
    opening = " ".join(words[:OPENING_WORDS])
    ending = " ".join(words[-CLOSING_WORDS:])

    greeting, intro = _GREETING.search(opening), _INTRO.search(opening)
    further = _FURTHER.search(ending)
    thanks, bye = _THANKS.search(ending), _BYE.search(ending)

    return [
        Check(
            "opening",
            bool(greeting and intro),
            f"greeting: {greeting[0] if greeting else 'missing'}; "
            f"intro or offer to help: {intro[0] if intro else 'missing'}",
        ),
        _dead_air(call, dead_air_seconds),
        Check("further_assistance", bool(further), further[0] if further else "never asked"),
        Check(
            "closing",
            bool(thanks and bye),
            f"thanks: {thanks[0] if thanks else 'missing'}; goodbye: {bye[0] if bye else 'missing'}",
        ),
    ]


def _dead_air(call: Call, limit: float) -> Check:
    """Silence before the agent speaks. With speaker labels only customer-to-agent gaps count
    (the time a customer takes to answer is not the agent's dead air); without labels every
    pause counts, so a proper hold will show up here too and needs a human look."""
    worst: tuple[float, Turn] | None = None
    for prev, nxt in pairwise(call.turns):
        if call.has_speakers and not (prev.speaker == "customer" and nxt.speaker == "agent"):
            continue
        gap = nxt.start - prev.end
        if worst is None or gap > worst[0]:
            worst = (gap, prev)
    if worst is None or worst[0] < limit:
        longest = f"{worst[0]:.1f}s" if worst else "n/a"
        return Check("dead_air", True, f"longest silence {longest}, limit {limit:.0f}s")
    gap, before = worst
    tail = " ".join(before.text.split()[-8:])
    return Check("dead_air", False, f'{gap:.1f}s silence at {_clock(before.end)} after: "{tail}"')


# ---------- LLM judge ----------

_JUDGE_PROMPT = """You are a call center quality analyst auditing one recorded voice call.
Score these parameters as passed true or false:
- probing: the agent asked questions to understand the issue before acting
- empathy: the agent acknowledged the customer's feelings or situation
- accuracy: the agent's information and resolution were correct and complete as far as the call shows
- professionalism: courteous throughout, no rudeness, arguing or blaming
Also list fatal errors, only if clearly present: rude or abusive language, misinformation that
could harm the customer, sharing account details without verifying identity, hanging up on the
customer, asking the customer for a high survey score.

Every item needs "quote": an exact, word-for-word excerpt from the transcript that proves it.
Copy it exactly; do not paraphrase. Reply with JSON only, in this shape:
{"parameters": {"probing": {"passed": true, "quote": "..."}, "empathy": {...},
"accuracy": {...}, "professionalism": {...}},
"fatal_errors": [{"type": "...", "quote": "..."}]}"""


def _transcript_for_llm(call: Call) -> str:
    lines = [
        f"[{_clock(t.start)}] {(t.speaker or 'unlabelled').capitalize()}: {t.text}"
        for t in call.turns
    ]
    note = "" if call.has_speakers else "Speakers are not labelled; work out who is the agent.\n"
    return note + "\n".join(lines)


def llm_judge(call: Call) -> dict:
    raw = llm.complete(
        [
            {"role": "system", "content": _JUDGE_PROMPT},
            {"role": "user", "content": _transcript_for_llm(call)},
        ],
        temperature=0.0,
        max_tokens=2000,
        timeout=90.0,
    )
    raw = re.sub(r"^```(json)?|```$", "", raw.strip()).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise QAScoreError(f"judge did not return JSON for call {call.call_id}: {raw[:200]}") from e


def score(
    call: Call,
    *,
    judge: Callable[[Call], dict] | None = llm_judge,
    dead_air_seconds: float = DEAD_AIR_SECONDS,
) -> Scorecard:
    """judge=None skips the LLM: only rule checks are scored, judged items go to review."""
    card = Scorecard(call.call_id, call.duration, rule_checks(call, dead_air_seconds))
    if judge is None:
        card.needs_review += [f"{p}: not scored (no LLM judge)" for p in JUDGED]
        return card

    verdict = judge(call)
    if "parameters" not in verdict or "fatal_errors" not in verdict:
        raise QAScoreError(f"judge reply for call {call.call_id} is missing keys: {verdict}")
    transcript = _norm(" ".join(t.text for t in call.turns))

    for p in JUDGED:
        if p not in verdict["parameters"]:
            raise QAScoreError(f"judge reply for call {call.call_id} has no '{p}'")
        item = verdict["parameters"][p]
        if _quoted(item["quote"], transcript):
            card.checks.append(Check(p, bool(item["passed"]), item["quote"]))
        else:
            card.needs_review.append(f'{p}: judge quote not found in call: "{item["quote"]}"')

    for fatal in verdict["fatal_errors"]:
        if _quoted(fatal["quote"], transcript):
            card.fatal_errors.append(Check(fatal["type"], False, fatal["quote"]))
        else:
            card.needs_review.append(f"possible fatal ({fatal['type']}), quote not found in call")
    return card


def _quoted(quote: str, transcript: str) -> bool:
    q = _norm(quote)
    return bool(q) and q in transcript


# ---------- report ----------


def render(card: Scorecard) -> str:
    lines = [
        f"Call {card.call_id}  |  handle time {_clock(card.duration)}  |  QA score {card.score}%",
    ]
    for c in card.checks:
        mark = "PASS" if c.passed else "FAIL"
        lines.append(f"  {mark}  {c.parameter:<19} ({WEIGHTS[c.parameter]:>2} pts)  {c.evidence}")
    for f in card.fatal_errors:
        lines.append(f'  FATAL {f.parameter}: "{f.evidence}"  -> score 0')
    for r in card.needs_review:
        lines.append(f"  REVIEW {r}")
    return "\n".join(lines)
