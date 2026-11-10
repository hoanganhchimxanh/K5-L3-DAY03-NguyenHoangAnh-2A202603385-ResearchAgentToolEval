"""Minimal Streamlit UI for the research agent.

Run from starter_v0/:  streamlit run app.py
Reuses the multi-round tool loop from chat.py and logs each session to transcripts/.
"""
from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import streamlit as st

from chat import ARTIFACTS_DIR, ROOT, run_model_tool_loop, trim_history, write_transcript
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

PROVIDER = os.getenv("APP_PROVIDER", "openai")
VERSION = os.getenv("APP_VERSION", "v7")
PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"

st.set_page_config(page_title="Research Agent", page_icon="🔎")


@st.cache_resource
def load_agent():
    declarations = load_tool_declarations(TOOLS_PATH)
    return (
        make_provider(PROVIDER),
        PROMPT_PATH.read_text(encoding="utf-8"),
        to_openai_tools(declarations),
        [item["name"] for item in declarations],
        build_artifact_version(VERSION, PROMPT_PATH, TOOLS_PATH),
    )


provider, system_prompt, tools, tool_names, artifact_version = load_agent()

if "history" not in st.session_state:
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    st.session_state.history = []          # [{"role", "content", "tool_events"?}]
    st.session_state.transcript_path = ROOT / "transcripts" / f"{VERSION}_{PROVIDER}_ui_{stamp}.transcript.json"
    st.session_state.transcript = {
        "transcript_id": st.session_state.transcript_path.stem,
        "source": "streamlit_ui",
        **artifact_version_dict(artifact_version),
        "provider": PROVIDER,
        "model": getattr(provider, "default_model", None),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "turns": [],
    }

with st.sidebar:
    st.header("🔎 Research Agent")
    st.caption(f"`{artifact_version.artifact_version}` · {PROVIDER}")
    st.markdown("**Tools:** " + ", ".join(f"`{name}`" for name in tool_names))
    st.markdown(
        "**Thử hỏi:**\n"
        "- Tin tức AI hôm nay có gì nổi bật?\n"
        "- 3 tweet mới nhất của Andrej Karpathy\n"
        "- Dân dev trên Hacker News bàn gì về Rust?\n"
        "- Transformer trong deep learning là gì?\n"
        "- Đăng bản tin này lên Telegram"
    )
    if st.button("Cuộc hội thoại mới"):
        st.session_state.clear()
        st.rerun()

st.title("Research Agent")

for message in st.session_state.history:
    with st.chat_message(message["role"]):
        for event in message.get("tool_events", []):
            with st.expander(f"🔧 {event['tool']}"):
                st.json({"args": event["args"], "result": event["result"]}, expanded=False)
        st.markdown(message["content"])

if user_text := st.chat_input("Hỏi gì đó…"):
    with st.chat_message("user"):
        st.markdown(user_text)
    plain_history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.history]
    messages = [{"role": "system", "content": system_prompt}, *trim_history(plain_history, 5),
                {"role": "user", "content": user_text}]
    with st.chat_message("assistant"):
        with st.spinner("Đang suy nghĩ / gọi tool…"):
            try:
                result = run_model_tool_loop(provider=provider, messages=messages, tools=tools, model=None, max_tool_rounds=4)
            except Exception as exc:  # show provider errors instead of crashing the page
                result = {"status": "provider_error", "assistant_text": f"Lỗi: {type(exc).__name__}: {exc}",
                          "rounds": [], "tool_events": []}
        for event in result["tool_events"]:
            with st.expander(f"🔧 {event['tool']}"):
                st.json({"args": event["args"], "result": event["result"]}, expanded=False)
        st.markdown(result["assistant_text"])

    st.session_state.history += [
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": result["assistant_text"], "tool_events": result["tool_events"]},
    ]
    st.session_state.transcript["turns"].append({
        "turn_index": len(st.session_state.transcript["turns"]) + 1,
        "user": user_text,
        **result,
    })
    write_transcript(Path(st.session_state.transcript_path), st.session_state.transcript)
