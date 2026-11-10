"""Minimal Streamlit UI for the research agent.

Run from starter_v0/:  streamlit run app.py
Reuses the multi-round tool loop from chat.py and logs each session to transcripts/.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import streamlit as st

from chat import ARTIFACTS_DIR, ROOT, run_model_tool_loop, trim_history, write_transcript
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

HISTORY_DIR = ARTIFACTS_DIR / "history"
CUSTOM_MODEL = "Khác (tự nhập)…"
# Model presets per provider; the first one is that provider's default. Any other id can be typed in.
MODEL_PRESETS = {
    "openai": ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-4.1"],
    "openrouter": ["openai/gpt-4o-mini", "openai/gpt-4o", "google/gemini-2.5-flash"],
    "gemini": ["gemini-3.5-flash", "gemini-2.5-flash"],
}

st.set_page_config(page_title="Research Agent", page_icon="🔎")


def prompt_versions() -> dict[str, tuple[Path, Path]]:
    """Version label -> (system_prompt, tools) paths: snapshots in artifacts/history plus the live files."""
    versions = {"hiện tại": (ARTIFACTS_DIR / "system_prompt.md", ARTIFACTS_DIR / "tools.yaml")}
    snapshots = sorted(HISTORY_DIR.glob("v*_system_prompt.md"), key=lambda p: int(p.name[1:].split("_")[0]), reverse=True)
    for prompt in snapshots:
        label = prompt.name.split("_")[0]
        tools_file = HISTORY_DIR / f"{label}_tools.yaml"
        if tools_file.exists():
            versions[label] = (prompt, tools_file)
    return versions


@st.cache_resource
def load_agent(provider_name: str, version: str, prompt_path: str, tools_path: str):
    declarations = load_tool_declarations(Path(tools_path))
    return (
        make_provider(provider_name),
        Path(prompt_path).read_text(encoding="utf-8"),
        to_openai_tools(declarations),
        [item["name"] for item in declarations],
        build_artifact_version(version, Path(prompt_path), Path(tools_path)),
    )


VERSIONS = prompt_versions()

with st.sidebar:
    page = st.radio("Trang", ["💬 Chat", "📊 Báo cáo"], horizontal=True, label_visibility="collapsed")
    st.header("🔎 Research Agent")
    provider_name = st.selectbox("Provider", list(MODEL_PRESETS))
    model_choice = st.selectbox("Model", [*MODEL_PRESETS[provider_name], CUSTOM_MODEL])
    model = st.text_input("Model id", MODEL_PRESETS[provider_name][0]) if model_choice == CUSTOM_MODEL else model_choice
    version_label = st.selectbox("Version prompt / tools", list(VERSIONS), index=list(VERSIONS).index("v7") if "v7" in VERSIONS else 0)

prompt_path, tools_path = VERSIONS[version_label]
VERSION = "current" if version_label == "hiện tại" else version_label
provider, system_prompt, tools, tool_names, artifact_version = load_agent(provider_name, VERSION, str(prompt_path), str(tools_path))

# Changing provider / model / version starts a fresh conversation (and a fresh transcript).
config = (provider_name, model, version_label)
if st.session_state.get("config") != config:
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    st.session_state.config = config
    st.session_state.history = []          # [{"role", "content", "tool_events"?}]
    st.session_state.transcript_path = ROOT / "transcripts" / f"{VERSION}_{provider_name}_ui_{stamp}.transcript.json"
    st.session_state.transcript = {
        "transcript_id": st.session_state.transcript_path.stem,
        "source": "streamlit_ui",
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": model,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "turns": [],
    }

SUITES = ["base", "group", "extension"]


def render_report() -> None:
    """Version progress built from runs/*.json, plus the changelog (or REPORT.md if absent)."""
    import pandas as pd

    rows = []
    for path in sorted((ROOT / "runs").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        summary = data.get("summary", {})
        if not summary.get("measured_cases"):
            continue  # skip runs that failed entirely (e.g. missing API key)
        rows.append({
            "version": data["version"], "suite": data["suite"], "generated_at": data.get("generated_at"),
            "case_accuracy": summary.get("case_accuracy"), "tool_routing": summary.get("tool_routing_accuracy"),
            "argument": summary.get("argument_accuracy"), "multiturn": summary.get("multiturn_accuracy"),
            "failed": ", ".join(r["id"] for r in data["results"] if not r["result"]["passed"]) or "—",
            "run_file": path.name,
        })
    st.title("Báo cáo tối ưu prompt / tools")
    if not rows:
        st.info("Chưa có run nào trong runs/.")
        return
    df = pd.DataFrame(rows).sort_values("generated_at")
    latest = df.groupby(["version", "suite"], as_index=False).last()  # latest run per version × suite
    pivot = latest.pivot(index="version", columns="suite", values="case_accuracy").reindex(columns=SUITES).astype(float)
    pivot = pivot.reindex(sorted(pivot.index, key=lambda v: (len(v), v)))

    st.subheader("case_accuracy theo version")
    st.line_chart(pivot, y_label="case_accuracy", x_label="version")
    st.dataframe(pivot.style.format("{:.2f}", na_rep="—"), use_container_width=True)

    suite = st.selectbox("Chi tiết bộ eval", SUITES)
    detail = latest[latest["suite"] == suite].drop(columns=["suite", "generated_at"])
    detail = detail.set_index("version").reindex(pivot.index).dropna(how="all")
    st.dataframe(detail, use_container_width=True)

    notes = ROOT / "CHANGELOG_LOCAL.md"
    source = notes if notes.exists() else ARTIFACTS_DIR / "REPORT.md"
    st.divider()
    st.markdown(source.read_text(encoding="utf-8"))


with st.sidebar:
    st.caption(f"`{artifact_version.artifact_version}`")
    with st.expander("Xem system prompt"):
        st.markdown(system_prompt)
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
        st.session_state.pop("config", None)
        st.rerun()

if page == "📊 Báo cáo":
    render_report()
    st.stop()

st.title("Research Agent")

# Hints for the error types users hit most often; matched against "Type: message".
ERROR_HINTS = [
    (("missing api key", "missing_api_key", "authentication", "401", "invalid api key", "incorrect api key"),
     "Kiểm tra API key tương ứng trong `.env`."),
    (("notfound", "404", "does not exist", "model_not_found", "not a valid model"),
     "Model id không tồn tại với provider này, hãy chọn model khác."),
    (("ratelimit", "429", "quota", "rate limit"), "Hết quota hoặc bị giới hạn tốc độ, đợi một lúc rồi thử lại."),
    (("timeout", "connectionerror", "connection error", "timed out"), "Lỗi mạng hoặc API phản hồi quá chậm."),
]


def hint_for(text: str) -> str:
    lowered = text.lower()
    return next((hint for needles, hint in ERROR_HINTS if any(n in lowered for n in needles)), "")


def collect_errors(result: dict) -> list[dict]:
    """Turn a tool-loop result into a list of {level, title, detail, hint} for display."""
    errors: list[dict] = []
    if result.get("status") == "provider_error":
        detail = result.get("error", "")
        errors.append({"level": "error", "title": f"Không gọi được model `{provider_name} / {model}`",
                       "detail": detail, "hint": hint_for(detail)})
    elif result.get("status") == "max_tool_rounds":
        errors.append({"level": "error", "title": "Agent dừng vì gọi tool quá 4 vòng mà chưa trả lời",
                       "detail": "Xem các tool call bên trên để biết agent bị lặp ở đâu.", "hint": ""})
    elif not (result.get("assistant_text") or "").strip():
        errors.append({"level": "error", "title": "Model không trả về nội dung nào", "detail": "", "hint": ""})
    for event in result.get("tool_events", []):
        tool_result = event.get("result")
        if isinstance(tool_result, dict) and tool_result.get("error"):
            detail = f"{tool_result['error']}: {tool_result.get('message', '')}".strip(": ")
            errors.append({"level": "warning", "title": f"Tool `{event['tool']}` bị lỗi",
                           "detail": detail, "hint": hint_for(detail)})
    return errors


def show_errors(errors: list[dict]) -> None:
    for item in errors:
        body = f"**{item['title']}**"
        if item["detail"]:
            body += f"\n\n`{item['detail'][:500]}`"
        if item["hint"]:
            body += f"\n\n💡 {item['hint']}"
        (st.error if item["level"] == "error" else st.warning)(body, icon="⚠️")


for message in st.session_state.history:
    with st.chat_message(message["role"]):
        for event in message.get("tool_events", []):
            with st.expander(f"🔧 {event['tool']}"):
                st.json({"args": event["args"], "result": event["result"]}, expanded=False)
        show_errors(message.get("errors", []))
        if message["content"]:
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
                result = run_model_tool_loop(provider=provider, messages=messages, tools=tools, model=model, max_tool_rounds=4)
            except Exception as exc:  # show provider errors instead of crashing the page
                result = {"status": "provider_error", "error": f"{type(exc).__name__}: {exc}",
                          "assistant_text": "", "rounds": [], "tool_events": []}
        for event in result["tool_events"]:
            with st.expander(f"🔧 {event['tool']}"):
                st.json({"args": event["args"], "result": event["result"]}, expanded=False)
        errors = collect_errors(result)
        show_errors(errors)
        if result["assistant_text"]:
            st.markdown(result["assistant_text"])

    st.session_state.history += [
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": result["assistant_text"], "tool_events": result["tool_events"], "errors": errors},
    ]
    st.session_state.transcript["turns"].append({
        "turn_index": len(st.session_state.transcript["turns"]) + 1,
        "user": user_text,
        **result,
    })
    write_transcript(Path(st.session_state.transcript_path), st.session_state.transcript)
