"""The shared LLM transport (`app/llm/client.py`).

The structured-output degradation ladder was copied into three modules and
tested by none of them, because testing it needs a live endpoint — unless the
client is a parameter, which after the consolidation it is. These use a fake in
place of the `openai` client, so they run with no server and no network.
"""
from __future__ import annotations

import json

import pytest

from app.llm.client import api_base, chat_json, loads_loose

# --- api_base --------------------------------------------------------------


@pytest.mark.parametrize("given,expected", [
    ("http://localhost:8080", "http://localhost:8080/v1"),
    ("http://localhost:8080/", "http://localhost:8080/v1"),
    ("http://localhost:8080/v1", "http://localhost:8080/v1"),
    ("http://localhost:8080/v1/", "http://localhost:8080/v1"),
    ("https://api.example.com/openai", "https://api.example.com/openai/v1"),
])
def test_api_base_appends_v1_exactly_once(given, expected):
    assert api_base(given) == expected


# --- loads_loose -----------------------------------------------------------

def test_loads_loose_reads_plain_json():
    assert loads_loose('{"a": 1}') == {"a": 1}


@pytest.mark.parametrize("fence", ["```", "```json", "```JSON"])
def test_loads_loose_strips_a_code_fence(fence):
    assert loads_loose(f'{fence}\n{{"a": 1}}\n```') == {"a": 1}


def test_loads_loose_digs_the_object_out_of_surrounding_prose():
    text = 'Sure! Here is the result:\n{"a": 1}\nLet me know if that helps.'
    assert loads_loose(text) == {"a": 1}


def test_loads_loose_raises_when_there_is_no_json_at_all():
    with pytest.raises(json.JSONDecodeError):
        loads_loose("I'm afraid I can't do that.")


# --- the fake ---------------------------------------------------------------

class _FakeClient:
    """Stands in for the `openai` client. Each scripted item is either an
    exception to raise or a string to return as the message content."""

    def __init__(self, *script):
        self._script = list(script)
        self.calls: list[dict] = []
        self.chat = type("_Chat", (), {"completions": self})()

    def create(self, **kwargs):
        self.calls.append(kwargs)
        item = self._script.pop(0) if self._script else RuntimeError("no more script")
        if isinstance(item, Exception):
            raise item
        return type("_Resp", (), {"choices": [
            type("_C", (), {"message": type("_M", (), {"content": item})()})()]})()


class _RejectedParamError(Exception):
    """A server rejecting an unsupported parameter."""


class _APIConnectionError(Exception):
    """Name-matched by the ladder as 'the server is unreachable'."""


class _APITimeoutError(Exception):
    pass


def _modes(client) -> list:
    """The `response_format` each attempt used (None = the prompt-only attempt)."""
    return [c.get("response_format") for c in client.calls]


# --- chat_json --------------------------------------------------------------

def test_chat_json_asks_for_a_schema_first_and_stops_when_it_works():
    c = _FakeClient('{"ok": 1}')
    assert chat_json(c, model="m", messages=[], what="x",
                     schema={"type": "object"}, schema_name="thing") == {"ok": 1}
    assert len(c.calls) == 1
    assert _modes(c)[0]["type"] == "json_schema"
    assert _modes(c)[0]["json_schema"]["name"] == "thing"
    assert _modes(c)[0]["json_schema"]["strict"] is True


def test_chat_json_degrades_when_the_server_rejects_the_schema():
    c = _FakeClient(_RejectedParamError("unknown param"), '{"ok": 1}')
    assert chat_json(c, model="m", messages=[], what="x",
                     schema={"type": "object"}) == {"ok": 1}
    assert [m and m["type"] for m in _modes(c)] == ["json_schema", "json_object"]


def test_chat_json_falls_all_the_way_back_to_a_plain_request():
    c = _FakeClient(_RejectedParamError("a"), _RejectedParamError("b"), '{"ok": 1}')
    assert chat_json(c, model="m", messages=[], what="x",
                     schema={"type": "object"}) == {"ok": 1}
    assert [m and m["type"] for m in _modes(c)] == \
        ["json_schema", "json_object", None]


def test_chat_json_degrades_when_the_answer_arrives_but_will_not_parse():
    """A server that *ignored* json_schema looks identical to one that honoured
    it until you try to read the answer."""
    c = _FakeClient("not json at all", '{"ok": 1}')
    assert chat_json(c, model="m", messages=[], what="x",
                     schema={"type": "object"}) == {"ok": 1}
    assert len(c.calls) == 2


@pytest.mark.parametrize("exc", [_APIConnectionError("down"), _APITimeoutError("slow")])
def test_chat_json_does_not_walk_the_ladder_for_an_unreachable_server(exc):
    """A laxer response_format will not fix a server that isn't answering, and
    retrying would triple the wait before the caller hears about it."""
    c = _FakeClient(exc, '{"ok": 1}')
    with pytest.raises(RuntimeError):
        chat_json(c, model="m", messages=[], what="x", schema={"type": "object"})
    assert len(c.calls) == 1


def test_chat_json_names_the_operation_and_chains_the_cause():
    c = _FakeClient(_RejectedParamError("a"), _RejectedParamError("b"), _RejectedParamError("c"))
    with pytest.raises(RuntimeError, match="LLM hint generation failed") as exc:
        chat_json(c, model="m", messages=[], what="hint generation",
                  schema={"type": "object"})
    assert isinstance(exc.value.__cause__, _RejectedParamError)


def test_chat_json_skips_the_schema_mode_when_there_is_no_schema():
    c = _FakeClient('{"ok": 1}')
    chat_json(c, model="m", messages=[], what="x")
    assert _modes(c) == [{"type": "json_object"}]


def test_chat_json_disables_thinking_by_default_and_leaves_it_on_when_asked():
    off = _FakeClient('{"ok": 1}')
    chat_json(off, model="m", messages=[], what="x")
    assert off.calls[0]["extra_body"] == {
        "chat_template_kwargs": {"enable_thinking": False}}

    on = _FakeClient('{"ok": 1}')
    chat_json(on, model="m", messages=[], what="x", thinking=True)
    assert "extra_body" not in on.calls[0]


def test_chat_json_forwards_a_callers_extra_body():
    c = _FakeClient('{"ok": 1}')
    chat_json(c, model="m", messages=[], what="x", extra_body={"seed": 7})
    assert c.calls[0]["extra_body"]["seed"] == 7
    assert c.calls[0]["extra_body"]["chat_template_kwargs"] == {"enable_thinking": False}


def test_chat_json_omits_optional_parameters_it_was_not_given():
    """A bare endpoint can reject a parameter it doesn't know; don't send noise."""
    c = _FakeClient('{"ok": 1}')
    chat_json(c, model="m", messages=[], what="x")
    assert "temperature" not in c.calls[0]
    assert "max_tokens" not in c.calls[0]

    c2 = _FakeClient('{"ok": 1}')
    chat_json(c2, model="m", messages=[], what="x", temperature=0.3, max_tokens=99)
    assert c2.calls[0]["temperature"] == 0.3
    assert c2.calls[0]["max_tokens"] == 99


def test_chat_json_uses_the_callers_parser():
    c = _FakeClient('{"hints": ["a", "b"]}')
    out = chat_json(c, model="m", messages=[], what="x",
                    parse=lambda text: loads_loose(text)["hints"])
    assert out == ["a", "b"]
