from __future__ import annotations

import http.client
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from typing import Any

import local_chat_ui
from local_chat_ui import LocalChatService, create_handler
from providers.base import ModelResponse


class FakeProvider:
    default_model = "test-model"

    def __init__(self) -> None:
        self.messages: list[list[dict[str, str]]] = []

    def complete(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        *,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: Any | None = None,
    ) -> ModelResponse:
        self.messages.append(messages)
        return ModelResponse(text="Test reply")


def make_service(tmp_path: Path, provider: FakeProvider) -> LocalChatService:
    return LocalChatService(
        provider=provider,
        provider_name="test",
        system_prompt="Test system prompt",
        tools=[],
        model="test-model",
        transcript_path=tmp_path / "chat.transcript.json",
        version_info={
            "version": "test",
            "artifact_version": "test+p123+t456",
            "prompt_hash": "p123",
            "tools_hash": "t456",
        },
    )


def test_local_chat_saves_turn_and_returns_model_response(tmp_path: Path) -> None:
    provider = FakeProvider()
    service = make_service(tmp_path, provider)

    result = service.chat("Find recent AI news")

    assert result == {"status": "answered", "text": "Test reply", "tool_events": []}
    transcript = (tmp_path / "chat.transcript.json").read_text(encoding="utf-8")
    assert '"user": "Find recent AI news"' in transcript
    assert '"assistant_text": "Test reply"' in transcript


def test_local_chat_carries_context_between_messages(tmp_path: Path) -> None:
    provider = FakeProvider()
    service = make_service(tmp_path, provider)

    service.chat("First question")
    service.chat("Follow-up question")

    assert [message["content"] for message in provider.messages[1]] == [
        "Test system prompt",
        "First question",
        "Test reply",
        "Follow-up question",
    ]


def test_local_chat_reset_clears_context_but_keeps_transcript(tmp_path: Path) -> None:
    provider = FakeProvider()
    service = make_service(tmp_path, provider)

    service.chat("First question")
    service.reset()
    service.chat("New conversation")

    assert [message["content"] for message in provider.messages[1]] == [
        "Test system prompt",
        "New conversation",
    ]
    assert len(service.transcript["turns"]) == 2


def test_local_chat_rejects_empty_message(tmp_path: Path) -> None:
    service = make_service(tmp_path, FakeProvider())

    try:
        service.chat("  ")
    except ValueError as exc:
        assert "must not be empty" in str(exc)
    else:
        raise AssertionError("Expected empty message validation to fail.")

    assert service.transcript["turns"] == []


def test_markdown_download_serves_only_generated_export_files(tmp_path: Path, monkeypatch) -> None:
    export_dir = tmp_path / "exports"
    export_dir.mkdir()
    (export_dir / "answer.md").write_bytes(b"# Answer\n")
    monkeypatch.setattr(local_chat_ui, "EXPORT_DIR", export_dir)
    service = make_service(tmp_path, FakeProvider())
    server = ThreadingHTTPServer(("127.0.0.1", 0), create_handler(service))
    thread = Thread(target=server.serve_forever)
    thread.start()
    connection = http.client.HTTPConnection("127.0.0.1", server.server_port)

    try:
        connection.request("GET", "/files/answer.md")
        response = connection.getresponse()
        body = response.read()
        assert response.status == 200
        assert response.getheader("Content-Disposition") == 'attachment; filename="answer.md"'
        assert body == b"# Answer\n"

        connection.request("GET", "/files/%2e%2e%2fsecret.md")
        response = connection.getresponse()
        response.read()
        assert response.status == 404
    finally:
        connection.close()
        server.shutdown()
        server.server_close()
        thread.join()
