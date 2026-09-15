"""The IVR menu layer — the "press 1 for X" part, a nod to what MyOperator
calls the Call Management Suite. Digit input is handled here without
touching the LLM at all; only free speech goes to conversation.py.
"""

MENU_PROMPT = (
    "Hi, this is CallPKT, a small AI phone demo. "
    "Press 1 to hear what this is. "
    "Press 2 to leave a message and talk to the assistant. "
    "Or just start talking after the tone."
)

MENU_INFO = (
    "This number runs on a free Twilio trial account and a free-tier language model. "
    "Every part of the call flow, the menu, the listening, the talking back, is "
    "hand-written in a small Python project, no managed voice-AI platform involved. "
    "Press 2 any time to talk to the assistant instead."
)


def is_menu_digit(digits: str | None) -> bool:
    return digits == "1"


def is_handoff_digit(digits: str | None) -> bool:
    return digits == "2"
