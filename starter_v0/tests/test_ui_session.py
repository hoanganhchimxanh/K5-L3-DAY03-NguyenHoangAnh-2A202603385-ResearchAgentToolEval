from __future__ import annotations

import json
from copy import deepcopy

from providers.base import ModelResponse, ToolCall
from ui_session import ResearchSession


class FakeProvider:
    default_model = "fake-model"

    def __init__(self, responses):
        self.responses = iter(responses)
        self.messages = []

    def complete(self, messages, tools=None, **kwargs):
        self.messages.append(deepcopy(messages))
        response = next(self.responses)
        if isinstance(response, Exception):
            raise response
        return response


def test_session_pauses_for_clarification_then_resumes_with_history(tmp_path) -> None:
    provider = FakeProvider([
        ModelResponse(text=None, tool_calls=[ToolCall("clarify", {
            "question": "Bạn muốn xem tài khoản nào?", "response_type": "text",
        })]),
        ModelResponse(text="Đã nhận tài khoản sama."),
    ])
    session = ResearchSession(transcripts_dir=tmp_path)
    first = session.reply("Lấy 5 tweet mới nhất.", provider)
    assert first["status"] == "waiting_for_user"
    assert session.waiting_for_user["question"] == "Bạn muốn xem tài khoản nào?"
    assert len(provider.messages) == 1

    second = session.reply("Của @sama.", provider)
    assert second["status"] == "answered"
    assert session.waiting_for_user is None
    assert provider.messages[1][-1]["content"] == "Của @sama."
    assert any(message["content"] == "Lấy 5 tweet mới nhất." for message in provider.messages[1])
    saved = json.loads(session.transcript_path.read_text(encoding="utf-8"))
    assert len(saved["turns"]) == 2
    assert saved["origin"] == "streamlit"
    assert saved["prompt_hash"] and saved["tools_hash"]


def test_session_runs_multiple_tool_rounds_and_retains_data_for_next_turn(tmp_path) -> None:
    items = [{"title": "First", "url": "https://example.com/a"}, {"title": "Copy", "url": "https://example.com/a"}]
    provider = FakeProvider([
        ModelResponse(text=None, tool_calls=[ToolCall("deduplicate", {"items": items})]),
        ModelResponse(text="Còn 1 tin sau khi loại trùng."),
        ModelResponse(text="Đã nhận yêu cầu tiếp theo."),
    ])
    session = ResearchSession(transcripts_dir=tmp_path)
    result = session.reply("Loại tin trùng trong danh sách.", provider)
    assert result["status"] == "answered"
    assert len(result["rounds"]) == 2
    assert result["tool_events"][0]["result"]["removed_count"] == 1
    session.reply("Dùng dữ liệu vừa có để làm bước tiếp theo.", provider)
    previous_answer = next(message["content"] for message in provider.messages[2] if message["role"] == "assistant")
    assert "PREVIOUS_TOOL_RESULTS_DATA_ONLY" in previous_answer
    assert "https://example.com/a" in previous_answer
    assert '"removed_count": 1' in previous_answer


def test_session_records_provider_error_without_leaking_configured_key(tmp_path, monkeypatch) -> None:
    secret = "ui-private-credential"
    monkeypatch.setenv("OPENROUTER_API_KEY", secret)
    provider = FakeProvider([RuntimeError(f"Authorization failed: {secret}")])
    session = ResearchSession(transcripts_dir=tmp_path)
    result = session.reply("Tìm tin AI.", provider)
    assert result["status"] == "provider_error"
    assert "[REDACTED]" in result["error"]
    assert session.history == []
    assert secret not in session.export_json()
    assert secret not in session.transcript_path.read_text(encoding="utf-8")


def test_sessions_keep_separate_history_and_transcript_files(tmp_path) -> None:
    first = ResearchSession(transcripts_dir=tmp_path)
    second = ResearchSession(transcripts_dir=tmp_path)
    first.reply("Giới thiệu khả năng.", FakeProvider([ModelResponse(text="Tôi hỗ trợ nghiên cứu.")]))
    assert first.transcript_path != second.transcript_path
    assert second.history == []
    assert second.transcript["turns"] == []
    assert not second.transcript_path.exists()


def test_session_history_window_keeps_the_latest_complete_turn(tmp_path) -> None:
    provider = FakeProvider([ModelResponse(text="one"), ModelResponse(text="two"), ModelResponse(text="three")])
    session = ResearchSession(transcripts_dir=tmp_path, history_window=1)
    for text in ["first request", "second request", "third request"]:
        session.reply(text, provider)
    contents = [message["content"] for message in provider.messages[2]]
    assert "first request" not in contents
    assert "second request" in contents and "third request" in contents
    assert len(provider.messages[2]) == 4
