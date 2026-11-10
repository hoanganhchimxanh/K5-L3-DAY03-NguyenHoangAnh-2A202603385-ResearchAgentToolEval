from __future__ import annotations

import json
from pathlib import Path

from streamlit.testing.v1 import AppTest

from providers.base import ModelResponse, ToolCall
from test_ui_session import FakeProvider

ROOT = Path(__file__).resolve().parents[1]


def test_chat_ui_renders_and_cancellation_button_resumes_the_conversation(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("env_loader.load_lab_env", lambda root: None)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-ui-key")
    monkeypatch.setenv("UI_TRANSCRIPTS_DIR", str(tmp_path))
    provider = FakeProvider([
        ModelResponse(text=None, tool_calls=[ToolCall("clarify", {
            "question": "Bạn xác nhận đăng bản tin này chứ?", "response_type": "yes_no",
        })]),
        ModelResponse(text="Đã hủy đăng bản tin."),
    ])
    monkeypatch.setattr("providers.make_provider", lambda name: provider)
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    assert not app.exception
    assert app.title[0].value == "Từ câu hỏi đến bản tin có nguồn."
    assert app.chat_input[0].disabled is False
    assert list(tmp_path.glob("*.transcript.json")) == []

    app.chat_input[0].set_value("Đăng bản tin: AI research update.").run()
    assert not app.exception
    session = app.session_state["research_session"]
    assert session.waiting_for_user["response_type"] == "yes_no"

    cancel_button = next(button for button in app.button if button.label == "Không, hủy")
    cancel_button.click().run()
    assert not app.exception
    assert provider.messages[-1][-1]["content"] == "Không, hủy yêu cầu đó."
    session = app.session_state["research_session"]
    assert session.waiting_for_user is None
    assert session.transcript["turns"][-1]["assistant_text"] == "Đã hủy đăng bản tin."
    assert len(app.chat_message) == 4
    saved = json.loads(next(tmp_path.glob("*.transcript.json")).read_text(encoding="utf-8"))
    assert len(saved["turns"]) == 2
    assert saved["version"] == "v7-integration"
    assert saved["origin"] == "streamlit"
    assert all(event["tool"] != "send" for turn in saved["turns"] for event in turn["tool_events"])

    previous_path = session.transcript_path
    next(button for button in app.button if button.label == "Cuộc trò chuyện mới").click().run()
    assert not app.exception
    restarted = app.session_state["research_session"]
    assert restarted.transcript_path != previous_path
    assert restarted.transcript["turns"] == []
    assert json.loads(previous_path.read_text(encoding="utf-8"))["turns"] == saved["turns"]
