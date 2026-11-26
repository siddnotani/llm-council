import runpy

import pytest
import uvicorn
from fastapi.testclient import TestClient

from backend import main, storage
from backend.main import MAX_MESSAGE_LENGTH, SendMessageRequest, app

client = TestClient(app)

SEND_ROUTES = [
    "/api/conversations/{id}/message",
    "/api/conversations/{id}/message/stream",
]


def run_launcher(monkeypatch):
    calls = []
    monkeypatch.setattr(uvicorn, "run", lambda *args, **kwargs: calls.append(kwargs))
    runpy.run_module("backend.main", run_name="__main__")
    return calls[0]


def test_launcher_binds_localhost_by_default(monkeypatch):
    monkeypatch.delenv("LLM_COUNCIL_HOST", raising=False)
    kwargs = run_launcher(monkeypatch)
    assert kwargs["host"] == "127.0.0.1"
    assert kwargs["port"] == 8001


def test_launcher_host_opt_in(monkeypatch):
    monkeypatch.setenv("LLM_COUNCIL_HOST", "0.0.0.0")
    assert run_launcher(monkeypatch)["host"] == "0.0.0.0"


@pytest.mark.parametrize("route", SEND_ROUTES)
def test_send_routes_reject_oversized_content(route, monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("handler must not run for oversized content")

    monkeypatch.setattr(storage, "get_conversation", fail)
    monkeypatch.setattr(main, "run_full_council", fail)
    monkeypatch.setattr(main, "stage1_collect_responses", fail)

    response = client.post(
        route.format(id="any"), json={"content": "x" * (MAX_MESSAGE_LENGTH + 1)}
    )
    assert response.status_code == 422


@pytest.mark.parametrize("route", SEND_ROUTES)
def test_send_routes_accept_content_at_limit(route, monkeypatch):
    monkeypatch.setattr(storage, "get_conversation", lambda conversation_id: None)

    response = client.post(
        route.format(id="missing"), json={"content": "x" * MAX_MESSAGE_LENGTH}
    )
    assert response.status_code == 404


def test_max_length_is_generous_for_normal_messages():
    assert SendMessageRequest(content="What is the capital of France?").content
    assert MAX_MESSAGE_LENGTH >= 10_000
