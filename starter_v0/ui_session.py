"""State and transcript handling for the Streamlit chat, using the CLI tool loop."""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from chat import json_text, now_iso, run_model_tool_loop, trim_history, write_transcript
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

ROOT = Path(__file__).resolve().parent
UI_VERSION = "v7-integration"
SECRET_ENV_NAMES = (
    "OPENROUTER_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY",
    "TAVILY_API_KEY", "FIRECRAWL_API_KEY", "RAPIDAPI_KEY", "TELEGRAM_BOT_TOKEN",
)


def public_data(value: Any) -> Any:
    """Keep configured credentials out of displayed errors and exported transcripts."""
    if isinstance(value, str):
        for name in SECRET_ENV_NAMES:
            secret = os.getenv(name)
            if secret and len(secret) >= 6:
                value = value.replace(secret, "[REDACTED]")
        return value
    if isinstance(value, list):
        return [public_data(item) for item in value]
    if isinstance(value, dict):
        return {key: public_data(item) for key, item in value.items()}
    return value


class ResearchSession:
    def __init__(
        self,
        provider_name: str = "openrouter",
        model: str | None = None,
        *,
        version: str = UI_VERSION,
        transcripts_dir: Path | None = None,
        history_window: int = 5,
        max_tool_rounds: int = 4,
    ) -> None:
        prompt_path = ROOT / "artifacts" / "system_prompt.md"
        tools_path = ROOT / "artifacts" / "tools.yaml"
        self.system_prompt = prompt_path.read_text(encoding="utf-8")
        self.tools = to_openai_tools(load_tool_declarations(tools_path))
        self.model = model
        self.history_window = history_window
        self.max_tool_rounds = max_tool_rounds
        self.history: list[dict[str, str]] = []
        self.waiting_for_user: dict[str, Any] | None = None
        identity = build_artifact_version(version, prompt_path, tools_path)
        transcript_id = f"{version}_{provider_name}_ui_{datetime.now():%Y%m%dT%H%M%S%f}_{uuid4().hex[:8]}"
        self.transcript_path = (transcripts_dir or ROOT / "transcripts") / f"{transcript_id}.transcript.json"
        self.transcript: dict[str, Any] = {
            "transcript_id": transcript_id,
            **artifact_version_dict(identity),
            "origin": "streamlit",
            "provider": provider_name,
            "model": model,
            "system_prompt": str(prompt_path),
            "tools": str(tools_path),
            "history_window": history_window,
            "max_tool_rounds": max_tool_rounds,
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "turns": [],
        }

    def reply(self, user_text: str, provider: Any) -> dict[str, Any]:
        user_text = user_text.strip()
        if not user_text:
            raise ValueError("A chat message cannot be empty")
        messages = [
            {"role": "system", "content": self.system_prompt},
            *trim_history(self.history, self.history_window),
            {"role": "user", "content": user_text},
        ]
        turn: dict[str, Any] = {
            "turn_index": len(self.transcript["turns"]) + 1,
            "started_at": now_iso(), "user": user_text,
            "rounds": [], "tool_events": [],
        }
        try:
            result = run_model_tool_loop(
                provider=provider, messages=messages, tools=self.tools,
                model=self.model, max_tool_rounds=self.max_tool_rounds,
            )
            turn.update(public_data(result))
            self.waiting_for_user = None
            if result["status"] == "waiting_for_user":
                self.waiting_for_user = next(
                    (event["result"] for event in reversed(turn["tool_events"])
                     if isinstance(event.get("result"), dict) and event["result"].get("awaiting_user")),
                    None,
                )
            # Retain collected data as context for later requests such as deduplication.
            # It is not displayed as a second chat message.
            context_answer = turn["assistant_text"]
            if turn["tool_events"]:
                context_answer += "\n\nPREVIOUS_TOOL_RESULTS_DATA_ONLY:\n" + json_text(
                    turn["tool_events"], max_chars=24000,
                )
            self.history.extend([
                {"role": "user", "content": user_text},
                {"role": "assistant", "content": context_answer},
            ])
        except Exception as exc:
            turn.update({
                "status": "provider_error",
                "error": public_data(f"{type(exc).__name__}: {exc}"),
                "assistant_text": "Chưa thể hoàn tất yêu cầu. Kiểm tra cấu hình provider hoặc kết nối rồi thử lại.",
            })
        turn["ended_at"] = now_iso()
        safe_turn = public_data(turn)
        self.transcript["turns"].append(safe_turn)
        write_transcript(self.transcript_path, self.transcript)
        return safe_turn

    def export_json(self) -> str:
        return json.dumps(public_data(self.transcript), ensure_ascii=False, indent=2)
