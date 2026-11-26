import json
import logging

from fastapi.testclient import TestClient

from backend import main


SECRET_DETAIL = "data/conversations/abc-123.json: permission denied"


def _parse_events(body: str):
    return [
        json.loads(line[len("data: "):])
        for line in body.splitlines()
        if line.startswith("data: ")
    ]


def test_stream_error_does_not_leak_exception_details(monkeypatch, caplog):
    monkeypatch.setattr(
        main.storage,
        "get_conversation",
        lambda conversation_id: {"id": conversation_id, "messages": []},
    )

    def failing_add_user_message(conversation_id, content):
        raise OSError(SECRET_DETAIL)

    monkeypatch.setattr(main.storage, "add_user_message", failing_add_user_message)

    client = TestClient(main.app)
    with caplog.at_level(logging.ERROR, logger=main.logger.name):
        response = client.post(
            "/api/conversations/abc-123/message/stream",
            json={"content": "hello"},
        )

    assert response.status_code == 200
    assert SECRET_DETAIL not in response.text
    assert "data/conversations" not in response.text

    events = _parse_events(response.text)
    assert events[-1]["type"] == "error"
    assert isinstance(events[-1]["message"], str) and events[-1]["message"]

    assert SECRET_DETAIL in caplog.text
