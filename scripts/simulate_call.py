#!/usr/bin/env python3
"""Drive app/conversation.py from the terminal, no Twilio account, no phone,
no cost beyond the free-tier LLM calls. Get the dialogue right before
spending any of the 75 free Twilio trial minutes on a real call.

Usage:
    uv run python scripts/simulate_call.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

from app import conversation, ivr

load_dotenv()


def main() -> None:
    print(ivr.MENU_PROMPT)
    print("(this simulator skips the digit menu and goes straight to conversation)")
    print("Type 'bye' to end the call. Ctrl+C to quit.\n")

    call_sid = "SIMULATED_CALL"
    conversation.start_session(call_sid)

    while True:
        try:
            caller_text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not caller_text:
            continue

        reply_text, should_hangup = conversation.handle_turn(call_sid, caller_text)
        print(f"CallPKT: {reply_text}")
        if should_hangup:
            print("\n[call ended]")
            break


if __name__ == "__main__":
    main()
