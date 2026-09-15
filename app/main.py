"""The webhook server. Two call paths, both driving the same conversation
manager (app/conversation.py):

  GET  /             the browser voice demo (default path — free, no
                      telephony provider, no phone number; see web/index.html)
  POST /chat          one turn of the browser call: {session_id, text} in,
                      {reply, hangup} out

  POST /voice          Twilio path, optional: first ring, greeting + menu
  POST /gather          Twilio path, optional: every subsequent turn

Twilio's trial account gates real phone numbers behind a paid plan in some
regions (hit that live 15 Sep 2026), so /voice and /gather are kept as an
optional stretch path rather than the default — wire them up if you later
have a working Twilio number.
"""

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel

from app import conversation, ivr, twiml
from app.security import verify_twilio_request

load_dotenv()

app = FastAPI(title="CallPKT")

_WEB_DIR = Path(__file__).resolve().parent.parent / "web"


class ChatTurn(BaseModel):
    session_id: str
    text: str


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(_WEB_DIR / "index.html")


@app.post("/chat")
async def chat(turn: ChatTurn) -> dict:
    reply_text, should_hangup = conversation.handle_turn(turn.session_id, turn.text)
    return {"reply": reply_text, "hangup": should_hangup}


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
