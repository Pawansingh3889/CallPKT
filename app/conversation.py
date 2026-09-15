"""The dialogue manager: per-call session state, turn limit, and goodbye
detection. This is the piece a managed platform (Vapi/Bland) would normally
hide from you — kept small and explicit here on purpose.
"""

from dataclasses import dataclass, field

from app import call_log, llm

MAX_TURNS = 6
_GOODBYE_WORDS = ("bye", "goodbye", "that's all", "thank you, bye", "hang up")


@dataclass
class CallSession:
    call_sid: str
    history: list[tuple[str, str]] = field(default_factory=list)
    turns: int = 0


# In-memory only: fine for a single-process demo. A production version would
# need shared state (Redis, a DB) across worker processes.
_sessions: dict[str, CallSession] = {}


def start_session(call_sid: str) -> CallSession:
    session = CallSession(call_sid=call_sid)
    _sessions[call_sid] = session
    return session


def _get_or_start(call_sid: str) -> CallSession:
    return _sessions.get(call_sid) or start_session(call_sid)


def handle_turn(call_sid: str, caller_text: str) -> tuple[str, bool]:
    """Returns (reply_text, should_hangup)."""
    session = _get_or_start(call_sid)
    session.turns += 1
    session.history.append(("user", caller_text))
    call_log.append_turn(call_sid, "user", caller_text)

    reply_text = llm.reply(session.history)
    session.history.append(("assistant", reply_text))
    call_log.append_turn(call_sid, "assistant", reply_text)

    caller_said_bye = any(word in caller_text.lower() for word in _GOODBYE_WORDS)
    hit_turn_limit = session.turns >= MAX_TURNS
    should_hangup = caller_said_bye or hit_turn_limit

    if should_hangup:
        call_log.finalize(call_sid)
        _sessions.pop(call_sid, None)

    return reply_text, should_hangup
