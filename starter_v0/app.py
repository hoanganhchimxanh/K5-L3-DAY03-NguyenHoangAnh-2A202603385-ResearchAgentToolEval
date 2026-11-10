from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlsplit

import streamlit as st

from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations
from ui_session import ResearchSession, UI_VERSION
from versioning import build_artifact_version

ROOT = Path(__file__).resolve().parent
load_lab_env(ROOT)
PROVIDERS = {
    "openrouter": "OpenRouter", "openai": "OpenAI", "anthropic": "Anthropic",
    "gemini": "Gemini", "ollama": "Ollama (local)",
}
KEYS = {
    "openrouter": "OPENROUTER_API_KEY", "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY", "gemini": "GEMINI_API_KEY",
}

st.set_page_config(page_title="Research Desk", page_icon="🔎", layout="wide")
st.markdown("""
<style>
.block-container {max-width: 1080px; padding-top: 2.4rem;}
h1 {letter-spacing: -.045em;}
[data-testid="stSidebar"] {border-right: 1px solid #dce5e5;}
[data-testid="stChatMessage"] {border: 1px solid #e1e9e8; border-radius: 14px;}
div.stButton > button {border-radius: 10px;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## Research Desk")
    st.caption("Tìm hiểu sâu hơn, với nguồn rõ ràng.")
    provider_name = st.selectbox("Provider", list(PROVIDERS), format_func=PROVIDERS.get)
    model_override = st.text_input("Model (tùy chọn)", placeholder="Để trống để dùng model mặc định")
    st.caption("Phiên mới được tạo khi cấu hình agent thay đổi.")
    new_session = st.button("Cuộc trò chuyện mới", use_container_width=True)

provider = make_provider(provider_name)
model = model_override.strip() or getattr(provider, "default_model", None)
identity = build_artifact_version(
    UI_VERSION, ROOT / "artifacts" / "system_prompt.md", ROOT / "artifacts" / "tools.yaml",
)
config = (provider_name, model, identity.artifact_version)
if new_session or "research_session" not in st.session_state or st.session_state.get("research_config") != config:
    st.session_state.research_session = ResearchSession(
        provider_name, model,
        transcripts_dir=Path(os.getenv("UI_TRANSCRIPTS_DIR", str(ROOT / "transcripts"))),
    )
    st.session_state.research_config = config
session: ResearchSession = st.session_state.research_session
key_name = KEYS.get(provider_name)
configured = not key_name or bool(os.getenv(key_name))

with st.sidebar:
    st.divider()
    declarations = load_tool_declarations(ROOT / "artifacts" / "tools.yaml")
    st.markdown(f"**{len(declarations)} công cụ nghiên cứu**")
    st.caption("Web · X/Twitter · arXiv · chính sách nội bộ · bản tin")
    with st.expander("Xem danh sách công cụ"):
        for tool in declarations:
            st.markdown(f"**{tool['name']}**")
            st.caption(tool["description"])
    st.divider()
    st.download_button(
        "Tải transcript JSON", data=session.export_json(),
        file_name=session.transcript_path.name, mime="application/json",
        disabled=not session.transcript["turns"], use_container_width=True,
    )
    st.caption(f"{len(session.transcript['turns'])} lượt trong phiên này")
    with st.expander("Thông tin phiên"):
        st.write("Model:", model)
        st.write("Version:", session.transcript["version"])
        st.code(session.transcript["artifact_version"], language=None)

st.caption("RESEARCH WORKSPACE")
st.title("Từ câu hỏi đến bản tin có nguồn.")
st.markdown("Tìm tin, đọc bài viết và sắp xếp thông tin. Giữ ngữ cảnh qua từng lượt trò chuyện.")
if not configured:
    st.warning(f"Thêm {key_name} vào file .env của bài tập để bắt đầu.")


def show_activity(turn: dict) -> None:
    events = turn.get("tool_events", [])
    if not events:
        return
    names = list(dict.fromkeys(event["tool"] for event in events))
    st.caption("Đã dùng: " + " · ".join(names))
    with st.expander("Nguồn và các bước thực hiện"):
        seen: set[str] = set()
        for event in events:
            result = event.get("result", {})
            if result.get("error"):
                st.warning(f"{event['tool']}: {result.get('message', result['error'])}")
            for item in result.get("items", []):
                url = item.get("url")
                if not isinstance(url, str) or url in seen:
                    continue
                try:
                    parsed = urlsplit(url)
                except ValueError:
                    continue
                if parsed.scheme in {"http", "https"} and parsed.netloc:
                    st.link_button(str(item.get("title") or parsed.netloc), url)
                    seen.add(url)
        st.json(events, expanded=False)


chosen_prompt = None
if not session.transcript["turns"]:
    st.write("")
    starters = [
        ("Tìm tin hôm nay", "Tìm trên web tin AI hôm nay và dẫn nguồn."),
        ("Đọc một bài viết", "Đọc và tóm tắt trang https://www.python.org/about/"),
        ("Loại tin trùng", 'Loại các tin trùng URL, giữ tin đầu tiên: [{"title":"Tin A","url":"https://example.com/a"},{"title":"Bản sao","url":"https://example.com/a"},{"title":"Tin B","url":"https://example.com/b"}]'),
    ]
    for column, (label, text) in zip(st.columns(3), starters):
        with column:
            if st.button(label, use_container_width=True, disabled=not configured):
                chosen_prompt = text
    st.caption("Bạn cũng có thể dán URL, đưa danh sách tin hoặc hỏi về một tài khoản cụ thể.")

for turn in session.transcript["turns"]:
    with st.chat_message("user"):
        st.markdown(turn["user"])
    with st.chat_message("assistant"):
        if turn["status"] == "provider_error":
            st.error(turn["assistant_text"])
            with st.expander("Chi tiết lỗi"):
                st.text(turn["error"])
        else:
            st.markdown(turn["assistant_text"])
        if turn["status"] == "waiting_for_user":
            st.caption("Đang chờ câu trả lời của bạn.")
        elif turn["status"] == "max_tool_rounds":
            st.warning("Đã đạt giới hạn bước xử lý. Bạn có thể chia yêu cầu thành các bước nhỏ hơn.")
        show_activity(turn)

waiting = session.waiting_for_user
if waiting and waiting.get("response_type") == "yes_no":
    yes, no = st.columns(2)
    if yes.button("Đồng ý", use_container_width=True, disabled=not configured):
        chosen_prompt = "Có, tôi xác nhận."
    if no.button("Không, hủy", use_container_width=True, disabled=not configured):
        chosen_prompt = "Không, hủy yêu cầu đó."
elif waiting and waiting.get("response_type") == "choice":
    options = waiting.get("options", [])[:6]
    if options:
        columns = st.columns(min(len(options), 3))
        for index, option in enumerate(options):
            if columns[index % len(columns)].button(option, key=f"choice_{index}", disabled=not configured):
                chosen_prompt = option

user_text = st.chat_input("Bạn muốn tìm hiểu điều gì?", disabled=not configured)
if user_text or chosen_prompt:
    with st.spinner("Đang tìm hiểu yêu cầu của bạn…"):
        try:
            session.reply(user_text or chosen_prompt, provider)
        except OSError:
            st.error("Không lưu được transcript. Kiểm tra quyền ghi của thư mục transcripts rồi thử lại.")
            st.stop()
    st.rerun()
