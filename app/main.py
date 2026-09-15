"""The webhook server. Two Twilio-facing endpoints:

  POST /voice    first ring: greeting + open the mic / menu
  POST /gather   every subsequent turn: digit or speech in, TwiML out

Point a Twilio number's "A call comes in" webhook at /voice on this server's
public URL (ngrok or Railway; see README) once you have a trial account.
"""

from dotenv import load_dotenv
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import Response

from app import conversation, ivr, twiml
from app.security import verify_twilio_request

load_dotenv()

app = FastAPI(title="CallPKT")


def _xml(body: str) -> Response:
    return Response(content=body, media_type="application/xml")


@app.post("/voice")
async def voice(request: Request) -> Response:
    await _verify(request)
    return _xml(twiml.greeting_response(action_url="/gather", greeting=ivr.MENU_PROMPT))


@app.post("/gather")
async def gather(
    request: Request,
    CallSid: str = Form(...),
    Digits: str | None = Form(default=None),
    SpeechResult: str | None = Form(default=None),
) -> Response:
    await _verify(request)

    if ivr.is_menu_digit(Digits):
        return _xml(twiml.turn_response("/gather", ivr.MENU_INFO))

    caller_text = SpeechResult or ("Tell me about this demo" if ivr.is_handoff_digit(Digits) else None)
    if not caller_text:
        return _xml(
            twiml.turn_response("/gather", "I didn't catch anything. Try speaking after the beep.")
        )

    reply_text, should_hangup = conversation.handle_turn(CallSid, caller_text)
    return _xml(twiml.turn_response("/gather", reply_text, hangup=should_hangup))


@app.get("/status")
async def status() -> dict:
    return {"ok": True, "service": "CallPKT"}


async def _verify(request: Request) -> None:
    try:
        await verify_twilio_request(request)
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
