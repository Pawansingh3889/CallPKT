"""Twilio request-signature validation — milestone 8, stubbed until a real
TWILIO_AUTH_TOKEN exists to test against. Controlled by
VALIDATE_TWILIO_SIGNATURE so the server runs (e.g. against
scripts/simulate_call.py's flow, or manual curl testing) before you have a
Twilio account at all.
"""

import os

from fastapi import Request
from twilio.request_validator import RequestValidator


async def verify_twilio_request(request: Request) -> None:
    """Raises ValueError if the request is not a genuine Twilio webhook.
    No-op while VALIDATE_TWILIO_SIGNATURE is unset, so local testing and
    early development aren't blocked on having a real Twilio account yet.
    """
    if os.environ.get("VALIDATE_TWILIO_SIGNATURE", "false").lower() != "true":
        return

    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    if not auth_token:
        raise ValueError(
            "VALIDATE_TWILIO_SIGNATURE is true but TWILIO_AUTH_TOKEN is not set."
        )

    signature = request.headers.get("X-Twilio-Signature", "")
    form = await request.form()
    validator = RequestValidator(auth_token)
    url = str(request.url)
    if not validator.validate(url, dict(form), signature):
        raise ValueError("Twilio request signature did not validate.")
