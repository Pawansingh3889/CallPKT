import json

import pytest

from app import qa_score


def _callpkt_log(tmp_path, turns):
    path = tmp_path / "call.json"
    path.write_text(json.dumps({"call_sid": "CA1", "turns": turns}))
    return path


def _at(second):
    return f"2026-11-02T10:00:{second:02d}+00:00"


GOOD_CALL = [
    ("user", "my order has not arrived", 0),
    (
        "assistant",
        "Hello, my name is Asha. I'm sorry your order is late. What is the order number?",
        2,
    ),
    ("user", "it is 4412", 8),
    (
        "assistant",
        "Thank you. It is out for delivery today. Is there anything else I can help with?",
        10,
    ),
    ("user", "no thanks", 14),
    ("assistant", "Thank you for calling, have a great day. Bye.", 15),
]


def _check(call, parameter):
    return next(c for c in qa_score.rule_checks(call) if c.parameter == parameter)


def _good_log(tmp_path):
    return _callpkt_log(tmp_path, [{"role": r, "text": t, "at": _at(s)} for r, t, s in GOOD_CALL])


def test_rule_checks_pass_on_a_clean_call(tmp_path):
    card = qa_score.score(qa_score.load(_good_log(tmp_path)), judge=None)
    assert {c.parameter: c.passed for c in card.checks} == {
        "opening": True,
        "dead_air": True,
        "further_assistance": True,
        "closing": True,
    }
    assert card.score == 100.0
    assert len(card.needs_review) == len(qa_score.JUDGED)


def test_dead_air_counts_only_the_agent_side(tmp_path):
    turns = [
        {"role": "user", "text": "hello", "at": _at(0)},
        {"role": "assistant", "text": "hi, how can I help", "at": _at(12)},  # 12 s: agent silence
        {"role": "user", "text": "never mind", "at": _at(40)},  # customer took 28 s: not counted
        {"role": "assistant", "text": "ok bye", "at": _at(41)},
    ]
    dead_air = _check(qa_score.load(_callpkt_log(tmp_path, turns)), "dead_air")
    assert dead_air.passed is False
    assert dead_air.evidence.startswith("12.0s silence at 0:00")


def test_callcenteren_words_split_into_turns_and_dead_air(tmp_path):
    def w(text, start_s, end_s):
        return {
            "text": text,
            "start": int(start_s * 1000),
            "end": int(end_s * 1000),
            "speaker": None,
        }

    path = tmp_path / "cc.json"
    path.write_text(
        json.dumps(
            {
                "text": "",
                "words": [
                    w("Hello,", 0, 0.4),
                    w("my", 0.5, 0.6),
                    w("name", 0.6, 0.8),
                    w("is", 0.8, 0.9),
                    w("Sam.", 0.9, 1.2),
                    w("Okay.", 20.0, 20.4),  # 18.8 s gap
                ],
            }
        )
    )
    call = qa_score.load(path)
    assert len(call.turns) == 2
    assert call.has_speakers is False
    dead_air = _check(call, "dead_air")
    assert dead_air.passed is False
    assert "18.8s" in dead_air.evidence


def _judge(quote_for_empathy, fatal=None):
    def judge(call):
        params = {
            p: {"passed": True, "quote": "What is the order number?"} for p in qa_score.JUDGED
        }
        params["empathy"] = {"passed": True, "quote": quote_for_empathy}
        return {"parameters": params, "fatal_errors": fatal or []}

    return judge


def test_judge_verdict_without_a_real_quote_goes_to_review(tmp_path):
    call = qa_score.load(_good_log(tmp_path))
    card = qa_score.score(call, judge=_judge("I completely understand how upsetting this is"))
    assert "empathy" not in {c.parameter for c in card.checks}
    assert any(r.startswith("empathy: judge quote not found") for r in card.needs_review)


def test_quote_matching_ignores_case_and_punctuation(tmp_path):
    call = qa_score.load(_good_log(tmp_path))
    card = qa_score.score(call, judge=_judge("i'm SORRY your order is late"))
    assert "empathy" in {c.parameter for c in card.checks}
    assert card.score == 100.0


def test_verified_fatal_error_zeroes_the_score(tmp_path):
    call = qa_score.load(_good_log(tmp_path))
    fatal = [{"type": "misinformation", "quote": "It is out for delivery today"}]
    card = qa_score.score(call, judge=_judge("I'm sorry your order is late", fatal))
    assert card.score == 0.0
    assert card.fatal_errors[0].parameter == "misinformation"


def test_unknown_format_fails_loudly(tmp_path):
    path = tmp_path / "x.json"
    path.write_text(json.dumps({"something": []}))
    with pytest.raises(qa_score.TranscriptFormatError):
        qa_score.load(path)
