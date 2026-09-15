from app import call_log, conversation, ivr, twiml


def test_ivr_digit_detection():
    assert ivr.is_menu_digit("1") is True
    assert ivr.is_menu_digit("2") is False
    assert ivr.is_handoff_digit("2") is True
    assert ivr.is_handoff_digit(None) is False


def test_twiml_escapes_special_characters():
    xml = twiml.say("Tom & Jerry's <call>")
    assert "&amp;" in xml
    assert "&lt;call&gt;" in xml
    assert "&apos;" in xml or "'" in xml  # apostrophe doesn't strictly need escaping


def test_greeting_response_contains_gather_and_action_url():
    xml = twiml.greeting_response(action_url="/gather", greeting="Hello")
    assert "<Gather" in xml
    assert 'action="/gather"' in xml
    assert "Hello" in xml


def test_turn_response_hangup_has_no_gather():
    xml = twiml.turn_response("/gather", "Goodbye then.", hangup=True)
    assert "<Hangup/>" in xml
    assert "<Gather" not in xml


def test_handle_turn_ends_on_goodbye(monkeypatch, tmp_path):
    monkeypatch.setattr(call_log, "_LOG_DIR", tmp_path)
    monkeypatch.setattr(conversation.llm, "reply", lambda history: "Goodbye, take care.")

    conversation.start_session("CA_TEST_1")
    reply_text, should_hangup = conversation.handle_turn("CA_TEST_1", "Alright, bye then")

    assert reply_text == "Goodbye, take care."
    assert should_hangup is True
    assert "CA_TEST_1" not in conversation._sessions


def test_handle_turn_continues_without_goodbye(monkeypatch, tmp_path):
    monkeypatch.setattr(call_log, "_LOG_DIR", tmp_path)
    monkeypatch.setattr(conversation.llm, "reply", lambda history: "Sure, tell me more.")

    conversation.start_session("CA_TEST_2")
    reply_text, should_hangup = conversation.handle_turn("CA_TEST_2", "What is this project?")

    assert reply_text == "Sure, tell me more."
    assert should_hangup is False
    assert "CA_TEST_2" in conversation._sessions


def test_handle_turn_hits_max_turn_limit(monkeypatch, tmp_path):
    monkeypatch.setattr(call_log, "_LOG_DIR", tmp_path)
    monkeypatch.setattr(conversation.llm, "reply", lambda history: "Still here.")

    conversation.start_session("CA_TEST_3")
    should_hangup = False
    for _ in range(conversation.MAX_TURNS):
        _, should_hangup = conversation.handle_turn("CA_TEST_3", "keep going")

    assert should_hangup is True
