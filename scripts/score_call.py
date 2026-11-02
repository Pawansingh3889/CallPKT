#!/usr/bin/env python3
"""Score call transcripts against the QA scorecard in app/qa_score.py.

Usage:
    uv run python scripts/score_call.py data/calls/*.json
    uv run python scripts/score_call.py data/external/medical_equipment_outbound/*.json --no-llm
    uv run python scripts/score_call.py CALL.json --json   # machine-readable output
"""

import argparse
import dataclasses
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

from app import qa_score

load_dotenv()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--no-llm", action="store_true", help="rule checks only, no API key needed")
    parser.add_argument("--json", action="store_true", help="print JSON instead of a report")
    parser.add_argument("--dead-air", type=float, default=qa_score.DEAD_AIR_SECONDS)
    args = parser.parse_args()

    judge = None if args.no_llm else qa_score.llm_judge
    cards = [
        qa_score.score(qa_score.load(p), judge=judge, dead_air_seconds=args.dead_air)
        for p in args.paths
    ]
    if args.json:
        print(json.dumps([dataclasses.asdict(c) | {"score": c.score} for c in cards], indent=2))
        return
    print("\n\n".join(qa_score.render(c) for c in cards))
    if len(cards) > 1:
        avg = sum(c.score for c in cards) / len(cards)
        fatal = sum(bool(c.fatal_errors) for c in cards)
        print(
            f"\n{len(cards)} calls  |  average QA score {avg:.1f}%  |  calls with a fatal: {fatal}"
        )


if __name__ == "__main__":
    main()
