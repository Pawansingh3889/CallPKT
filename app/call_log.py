"""Per-call transcript logging to local JSON. Milestone 10 in the README
swaps this for a Notion Job Hunt Tracker entry once NOTION_API_KEY is wired
in the same way the WhatsApp workflow already uses it; this local version
needs nothing beyond a writable data/ directory, so the demo works standalone.
"""

import json
from datetime import UTC, datetime
from pathlib import Path

_LOG_DIR = Path(__file__).resolve().parent.parent / "data" / "calls"


def _path_for(call_sid: str) -> Path:
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    return _LOG_DIR / f"{call_sid}.json"


def append_turn(call_sid: str, role: str, text: str) -> None:
    path = _path_for(call_sid)
    record = json.loads(path.read_text()) if path.exists() else {"call_sid": call_sid, "turns": []}
    record["turns"].append(
        {"role": role, "text": text, "at": datetime.now(UTC).isoformat()}
    )
    path.write_text(json.dumps(record, indent=2))


def finalize(call_sid: str) -> None:
    path = _path_for(call_sid)
    if not path.exists():
        return
    record = json.loads(path.read_text())
    record["ended_at"] = datetime.now(UTC).isoformat()
    path.write_text(json.dumps(record, indent=2))
