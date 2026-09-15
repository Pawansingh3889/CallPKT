"""Hand-written TwiML generation.

Twilio's own Python SDK ships a VoiceResponse builder that does this for you;
this module skips it on purpose. TwiML is just XML, and writing it directly
keeps the one thing this repo is meant to demonstrate (the call flow) visible
in one place instead of behind a builder API.
"""

from xml.sax.saxutils import escape

# Twilio's <Gather> speechTimeout="auto" ends listening on a detected pause,
# which is more natural for a phone call than a fixed timeout.
_GATHER_OPEN = (
    '<Gather input="speech dtmf" action="{action}" method="POST" '
    'speechTimeout="auto" numDigits="1" language="en-IN">'
)


def say(text: str, voice: str = "Polly.Aditi") -> str:
    """A single <Say> element. Polly.Aditi is an Indian-English neural voice,
    included free in Twilio's TTS, no extra per-minute charge."""
    return f'<Say voice="{voice}">{escape(text)}</Say>'


def greeting_response(action_url: str, greeting: str) -> str:
    """Initial TwiML for /voice: speak the greeting, then listen."""
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
        "<Response>"
        f"{say(greeting)}"
        f"{_GATHER_OPEN.format(action=action_url)}</Gather>"
        f"{say('Sorry, I did not catch that. Goodbye.')}"
        "<Hangup/>"
        "</Response>"
    )


def turn_response(action_url: str, reply: str, *, hangup: bool = False) -> str:
    """TwiML for one /gather turn: speak the reply, then either listen again
    or hang up if the conversation manager decided the call is over."""
    if hangup:
        return (
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
            f"<Response>{say(reply)}<Hangup/></Response>"
        )
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
        "<Response>"
        f"{say(reply)}"
        f"{_GATHER_OPEN.format(action=action_url)}</Gather>"
        f"{say('Sorry, I did not catch that. Goodbye.')}"
        "<Hangup/>"
        "</Response>"
    )
