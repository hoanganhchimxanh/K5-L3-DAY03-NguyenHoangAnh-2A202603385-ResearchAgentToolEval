from __future__ import annotations

import argparse
import contextlib
import io
import json
import re
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

from chat import now_iso, run_model_tool_loop, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
MAX_REQUEST_BYTES = 16_384
MAX_MESSAGE_CHARS = 4_000
EXPORT_DIR = ROOT / "exports"
EXPORT_FILENAME_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\.md\Z")
load_lab_env(ROOT)

PAGE = r"""<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#10131b">
  <title>Fieldnotes — Trợ lý nghiên cứu</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #10131b;
      --panel: #171b25;
      --panel-soft: #1d2230;
      --line: #2b3140;
      --text: #eef0f6;
      --muted: #9299aa;
      --accent: #c3f36b;
      --accent-ink: #17200c;
      --user: #252b39;
      --danger: #ff9a9a;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    * { box-sizing: border-box; }
    body { margin: 0; min-height: 100vh; background: var(--bg); color: var(--text); }
    button, textarea { font: inherit; }
    .shell { display: grid; grid-template-columns: 260px minmax(0, 1fr); min-height: 100vh; }
    aside {
      display: flex; flex-direction: column; gap: 28px; padding: 26px 18px;
      background: #141720; border-right: 1px solid var(--line);
    }
    .brand { display: flex; align-items: center; gap: 12px; padding: 2px 6px; }
    .brand-mark {
      display: grid; place-items: center; width: 38px; height: 38px; border-radius: 12px;
      color: var(--accent-ink); background: var(--accent); font-weight: 900; font-size: 19px;
    }
    .brand-name { font-size: 15px; font-weight: 750; letter-spacing: -.02em; }
    .brand-sub { margin-top: 3px; color: var(--muted); font-size: 11px; }
    .side-label { margin: 0 8px 10px; color: #777f91; font-size: 10px; font-weight: 750; letter-spacing: .13em; text-transform: uppercase; }
    .new-chat {
      width: 100%; padding: 11px 12px; border: 1px solid var(--line); border-radius: 10px;
      background: var(--panel); color: var(--text); text-align: left; cursor: pointer;
    }
    .new-chat:hover { border-color: #596173; background: var(--panel-soft); }
    .side-note { margin: auto 8px 0; color: var(--muted); font-size: 12px; line-height: 1.7; }
    .side-note strong { color: #d7dbe5; font-weight: 600; }
    main { display: flex; min-width: 0; min-height: 100vh; flex-direction: column; }
    header {
      display: flex; min-height: 74px; align-items: center; justify-content: space-between;
      padding: 16px clamp(18px, 4vw, 56px); border-bottom: 1px solid var(--line);
    }
    .heading { font-size: 14px; font-weight: 700; }
    .version { margin-top: 4px; color: var(--muted); font-size: 11px; }
    .connection { display: flex; align-items: center; gap: 8px; color: #c1c6d1; font-size: 12px; }
    .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--accent); box-shadow: 0 0 12px #c3f36655; }
    .dot.busy { background: #f3c76b; box-shadow: 0 0 12px #f3c76655; }
    .chat { width: min(860px, 100%); margin: 0 auto; padding: 34px clamp(16px, 4vw, 42px) 24px; flex: 1; }
    .welcome { padding: clamp(24px, 7vh, 76px) 0 30px; }
    .eyebrow { color: var(--accent); font-size: 11px; font-weight: 750; letter-spacing: .16em; text-transform: uppercase; }
    h1 { margin: 14px 0 10px; font-size: clamp(29px, 4vw, 43px); letter-spacing: -.055em; line-height: 1.08; }
    .intro { max-width: 550px; margin: 0; color: #a7adbb; font-size: 14px; line-height: 1.7; }
    .suggestions { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; margin-top: 26px; }
    .suggestion {
      min-height: 58px; padding: 12px 14px; border: 1px solid var(--line); border-radius: 12px;
      background: #151923; color: #d9dce4; text-align: left; cursor: pointer; font-size: 12px; line-height: 1.5;
    }
    .suggestion:hover { border-color: #657147; background: #1a201b; }
    .messages { display: flex; flex-direction: column; gap: 24px; }
    .message { display: flex; gap: 12px; align-items: flex-start; }
    .avatar {
      display: grid; flex: 0 0 30px; place-items: center; width: 30px; height: 30px; border-radius: 10px;
      color: var(--accent-ink); background: var(--accent); font-size: 12px; font-weight: 850;
    }
    .message.user .avatar { color: #e0e4ee; background: #343b4b; }
    .message-body { min-width: 0; flex: 1; }
    .message-label { margin: 1px 0 7px; color: var(--muted); font-size: 11px; font-weight: 650; }
    .message-text { color: #e6e8ee; font-size: 14px; line-height: 1.75; overflow-wrap: anywhere; white-space: pre-wrap; }
    .message.user .message-text {
      display: inline-block; max-width: 100%; padding: 10px 13px; border-radius: 4px 13px 13px 13px;
      background: var(--user); color: #f0f1f5;
    }
    .tool-list { display: grid; gap: 8px; margin-top: 12px; }
    details.tool {
      overflow: hidden; border: 1px solid var(--line); border-radius: 10px; background: #141720;
    }
    details.tool summary { padding: 10px 12px; color: #b7becd; cursor: pointer; font-size: 11px; }
    .tool-name { color: var(--accent); font-family: ui-monospace, SFMono-Regular, Consolas, monospace; }
    .tool-result { max-height: 240px; overflow: auto; margin: 0; padding: 0 12px 12px; color: #aab1bf; font: 11px/1.6 ui-monospace, SFMono-Regular, Consolas, monospace; white-space: pre-wrap; overflow-wrap: anywhere; }
    .download-link { display: inline-flex; margin: 0 12px 12px; color: var(--accent); font-size: 12px; font-weight: 650; text-decoration: none; }
    .download-link:hover { text-decoration: underline; }
    .error { color: var(--danger); }
    .composer-wrap { position: sticky; bottom: 0; padding: 14px clamp(16px, 4vw, 42px) 20px; background: linear-gradient(transparent, var(--bg) 18%); }
    .composer { width: min(776px, 100%); margin: auto; }
    .input-box {
      display: flex; align-items: flex-end; gap: 12px; padding: 12px;
      border: 1px solid #3a4150; border-radius: 16px; background: #1a1e29;
      box-shadow: 0 12px 40px #0003;
    }
    textarea {
      width: 100%; max-height: 180px; min-height: 28px; resize: vertical; border: 0; outline: 0;
      background: transparent; color: var(--text); font-size: 14px; line-height: 1.6;
    }
    textarea::placeholder { color: #777f8f; }
    .send {
      display: grid; flex: 0 0 36px; place-items: center; width: 36px; height: 36px;
      border: 0; border-radius: 11px; background: var(--accent); color: var(--accent-ink);
      cursor: pointer; font-size: 17px; font-weight: 800;
    }
    .send:disabled { opacity: .48; cursor: wait; }
    .hint { margin: 9px 0 0; color: #71798a; text-align: center; font-size: 10px; }
    .notice { margin: 10px auto 0; color: var(--danger); text-align: center; font-size: 12px; }
    @media (max-width: 720px) {
      .shell { grid-template-columns: 1fr; }
      aside { display: none; }
      header { min-height: 64px; }
      .chat { padding-top: 20px; }
      .welcome { padding-top: 34px; }
      .suggestions { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <aside>
      <div class="brand">
        <div class="brand-mark">f.</div>
        <div><div class="brand-name">Fieldnotes</div><div class="brand-sub">Trợ lý nghiên cứu</div></div>
      </div>
      <div>
        <div class="side-label">Không gian làm việc</div>
        <button class="new-chat" id="reset">＋ &nbsp; Cuộc trò chuyện mới</button>
      </div>
      <div class="side-note"><strong>Nghiên cứu có dẫn nguồn.</strong><br>Tìm kiếm web và mạng xã hội, đọc nguồn, tra cứu bài báo và chính sách nội bộ. Hoạt động được lưu trong transcript trên máy này.</div>
    </aside>
    <main>
      <header>
        <div><div class="heading">Trợ lý nghiên cứu</div><div class="version" id="version">Phiên local</div></div>
        <div class="connection"><span class="dot" id="dot"></span><span id="connection">Đã kết nối local</span></div>
      </header>
      <section class="chat" aria-live="polite">
        <div class="welcome" id="welcome">
          <div class="eyebrow">Bàn nghiên cứu của bạn</div>
          <h1>Bắt đầu nghiên cứu<br>từ một câu hỏi.</h1>
          <p class="intro">Tìm kiếm trên web, xem thảo luận mạng xã hội, đọc nguồn hoặc khám phá bài báo khoa học. Hãy mô tả điều bạn cần bằng ngôn ngữ tự nhiên.</p>
          <div class="suggestions">
            <button class="suggestion">Tin AI mới nhất hôm nay có gì?</button>
            <button class="suggestion">Tìm các bài đăng phổ biến về mô hình mã nguồn mở.</button>
            <button class="suggestion">Tìm bài báo gần đây về AI trong y tế.</button>
            <button class="suggestion">Tóm tắt bài viết này: https://example.com</button>
          </div>
        </div>
        <div class="messages" id="messages"></div>
      </section>
      <div class="composer-wrap">
        <form class="composer" id="form">
          <div class="input-box">
            <textarea id="input" rows="1" maxlength="4000" placeholder="Đặt câu hỏi nghiên cứu..." aria-label="Tin nhắn"></textarea>
              <button class="send" id="send" type="submit" aria-label="Gửi tin nhắn">↑</button>
          </div>
          <p class="hint">Enter để gửi · Shift + Enter để xuống dòng · Dữ liệu xử lý trên máy này</p>
          <div class="notice" id="notice" role="status"></div>
        </form>
      </div>
    </main>
  </div>
  <script>
    const form = document.querySelector("#form");
    const input = document.querySelector("#input");
    const messages = document.querySelector("#messages");
    const welcome = document.querySelector("#welcome");
    const send = document.querySelector("#send");
    const notice = document.querySelector("#notice");
    const dot = document.querySelector("#dot");
    const connection = document.querySelector("#connection");

    function addMessage(role, text, events = []) {
      welcome.hidden = true;
      const wrapper = document.createElement("article");
      wrapper.className = `message ${role}`;
      const avatar = document.createElement("div");
      avatar.className = "avatar";
      avatar.textContent = role === "user" ? "Bạn" : "f.";
      const body = document.createElement("div");
      body.className = "message-body";
      const label = document.createElement("div");
      label.className = "message-label";
      label.textContent = role === "user" ? "Bạn" : "Trợ lý nghiên cứu";
      const content = document.createElement("div");
      content.className = "message-text";
      content.textContent = text;
      body.append(label, content);
      if (events.length) {
        const list = document.createElement("div");
        list.className = "tool-list";
        for (const event of events) {
          const details = document.createElement("details");
          details.className = "tool";
          const summary = document.createElement("summary");
          const result = event.result || {};
          details.open = event.tool === "save_markdown" && result.status === "saved";
          const status = result.error ? " · error" : "";
          summary.innerHTML = `<span class="tool-name"></span> · hoạt động${status ? " · lỗi" : ""}`;
          summary.querySelector(".tool-name").textContent = event.tool;
          if (result.error) summary.classList.add("error");
          const pre = document.createElement("pre");
          pre.className = "tool-result";
          pre.textContent = JSON.stringify({args: event.args, result}, null, 2);
          details.append(summary, pre);
          if (event.tool === "save_markdown" && result.status === "saved" &&
              typeof result.file_name === "string" &&
              /^[a-z0-9]+(?:-[a-z0-9]+)*\.md$/.test(result.file_name)) {
            const link = document.createElement("a");
            link.className = "download-link";
            link.href = `/files/${encodeURIComponent(result.file_name)}`;
            link.download = result.file_name;
            link.textContent = `Tải xuống ${result.file_name}`;
            details.append(link);
          }
          list.append(details);
        }
        body.append(list);
      }
      wrapper.append(avatar, body);
      messages.append(wrapper);
      wrapper.scrollIntoView({behavior: "smooth", block: "end"});
    }

    async function sendMessage(text) {
      notice.textContent = "";
      send.disabled = true;
      input.disabled = true;
      dot.classList.add("busy");
      connection.textContent = "Đang xử lý…";
      addMessage("user", text);
      const pending = document.createElement("article");
      pending.className = "message assistant";
      pending.innerHTML = '<div class="avatar">f.</div><div class="message-body"><div class="message-label">Trợ lý nghiên cứu</div><div class="message-text">Đang tìm kiếm nguồn…</div></div>';
      messages.append(pending);
      try {
        const response = await fetch("/api/chat", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({message: text})
        });
        const data = await response.json();
        pending.remove();
        if (!response.ok) throw new Error(data.error || "The request failed.");
        addMessage("assistant", data.text || "", data.tool_events || []);
      } catch (error) {
        pending.remove();
        notice.textContent = error.message || "Could not reach the local chat server.";
      } finally {
        send.disabled = false;
        input.disabled = false;
        input.focus();
        dot.classList.remove("busy");
        connection.textContent = "Đã kết nối local";
      }
    }

    form.addEventListener("submit", event => {
      event.preventDefault();
      const text = input.value.trim();
      if (!text || send.disabled) return;
      input.value = "";
      sendMessage(text);
    });
    input.addEventListener("keydown", event => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        form.requestSubmit();
      }
    });
    document.querySelectorAll(".suggestion").forEach(button => {
      button.addEventListener("click", () => {
        input.value = button.textContent;
        form.requestSubmit();
      });
    });
    document.querySelector("#reset").addEventListener("click", async () => {
      const response = await fetch("/api/reset", {method: "POST"});
      if (response.ok) {
        messages.replaceChildren();
        welcome.hidden = false;
        notice.textContent = "";
        input.focus();
      } else {
        notice.textContent = "Could not reset the conversation.";
      }
    });
    fetch("/api/status").then(response => response.json()).then(data => {
      document.querySelector("#version").textContent = `${data.provider} · ${data.model} · ${data.artifact_version}`;
    }).catch(() => {
      connection.textContent = "Không kết nối được máy chủ local";
    });
  </script>
</body>
</html>
"""


class LocalChatService:
    def __init__(
        self,
        *,
        provider: Any,
        provider_name: str,
        system_prompt: str,
        tools: list[dict[str, Any]],
        model: str | None,
        transcript_path: Path,
        version_info: dict[str, str],
        history_window: int = 5,
        max_tool_rounds: int = 4,
    ) -> None:
        self.provider = provider
        self.provider_name = provider_name
        self.system_prompt = system_prompt
        self.tools = tools
        self.model = model
        self.transcript_path = transcript_path
        self.history_window = history_window
        self.max_tool_rounds = max_tool_rounds
        self.history: list[dict[str, str]] = []
        self.lock = threading.Lock()
        self.transcript: dict[str, Any] = {
            "transcript_id": transcript_path.stem.removesuffix(".transcript"),
            **version_info,
            "provider": provider_name,
            "model": model,
            "system_prompt": str(ARTIFACTS_DIR / "system_prompt.md"),
            "tools": str(ARTIFACTS_DIR / "tools.yaml"),
            "history_window": history_window,
            "max_tool_rounds": max_tool_rounds,
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "turns": [],
        }
        write_transcript(self.transcript_path, self.transcript)

    def status(self) -> dict[str, str | None]:
        return {
            "provider": self.provider_name,
            "model": self.model or "default model",
            "artifact_version": self.transcript["artifact_version"],
        }

    def reset(self) -> None:
        with self.lock:
            self.history.clear()

    def chat(self, message: str) -> dict[str, Any]:
        if not isinstance(message, str) or not message.strip():
            raise ValueError("Message must not be empty.")
        if len(message) > MAX_MESSAGE_CHARS:
            raise ValueError(f"Message must be {MAX_MESSAGE_CHARS} characters or fewer.")

        message = message.strip()
        with self.lock:
            turn: dict[str, Any] = {
                "turn_index": len(self.transcript["turns"]) + 1,
                "started_at": now_iso(),
                "user": message,
                "status": "started",
                "assistant_text": None,
                "rounds": [],
                "tool_events": [],
            }
            messages = [
                {"role": "system", "content": self.system_prompt},
                *trim_history(self.history, self.history_window),
                {"role": "user", "content": message},
            ]
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    result = run_model_tool_loop(
                        provider=self.provider,
                        messages=messages,
                        tools=self.tools,
                        model=self.model,
                        max_tool_rounds=self.max_tool_rounds,
                    )
                turn.update(result)
                self.history.extend([
                    {"role": "user", "content": message},
                    {"role": "assistant", "content": result["assistant_text"]},
                ])
                response = {
                    "status": result["status"],
                    "text": result["assistant_text"],
                    "tool_events": result["tool_events"],
                }
            except Exception as exc:
                print(f"Provider request failed: {type(exc).__name__}: {exc}")
                turn.update({
                    "status": "provider_error",
                    "error": f"{type(exc).__name__}: {exc}",
                })
                response = {
                    "status": "provider_error",
                    "text": "The model request failed. Check the local server output and provider configuration.",
                    "tool_events": [],
                    "error": f"{type(exc).__name__}: {exc}",
                }
            turn["ended_at"] = now_iso()
            self.transcript["turns"].append(turn)
            write_transcript(self.transcript_path, self.transcript)
            return response


def create_handler(service: LocalChatService) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        server_version = "ResearchChat/1.0"

        def log_message(self, format: str, *args: Any) -> None:
            print(f"{self.address_string()} - {format % args}")

        def _send_json(self, status: int, payload: dict[str, Any]) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _origin_is_local(self) -> bool:
            origin = self.headers.get("Origin")
            if not origin:
                return True
            parsed = urlsplit(origin)
            return (
                parsed.scheme == "http"
                and parsed.hostname in {"localhost", "127.0.0.1"}
                and parsed.port == self.server.server_port
            )

        def do_GET(self) -> None:
            path = urlsplit(self.path).path
            if path == "/":
                body = PAGE.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)
            elif path == "/api/status":
                self._send_json(200, service.status())
            elif path.startswith("/files/"):
                file_name = unquote(path[len("/files/"):])
                if not EXPORT_FILENAME_PATTERN.fullmatch(file_name):
                    self._send_json(404, {"error": "File not found."})
                    return
                try:
                    export_root = EXPORT_DIR.resolve()
                    file_path = (export_root / file_name).resolve(strict=True)
                    if file_path.parent != export_root or not file_path.is_file():
                        self._send_json(404, {"error": "File not found."})
                        return
                    body = file_path.read_bytes()
                except FileNotFoundError:
                    self._send_json(404, {"error": "File not found."})
                    return
                self.send_response(200)
                self.send_header("Content-Type", "text/markdown; charset=utf-8")
                self.send_header("Content-Disposition", f'attachment; filename="{file_name}"')
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.end_headers()
                self.wfile.write(body)
            else:
                self._send_json(404, {"error": "Not found."})

        def do_POST(self) -> None:
            if not self._origin_is_local():
                self._send_json(403, {"error": "Requests must come from this local chat page."})
                return

            path = urlsplit(self.path).path
            if path == "/api/reset":
                service.reset()
                self._send_json(200, {"status": "reset"})
                return
            if path != "/api/chat":
                self._send_json(404, {"error": "Not found."})
                return

            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self._send_json(400, {"error": "Invalid Content-Length."})
                return
            if length <= 0 or length > MAX_REQUEST_BYTES:
                self._send_json(413, {"error": "Request body must be between 1 byte and 16 KB."})
                return
            try:
                payload = json.loads(self.rfile.read(length))
            except (json.JSONDecodeError, UnicodeDecodeError):
                self._send_json(400, {"error": "Request body must be valid JSON."})
                return
            if not isinstance(payload, dict):
                self._send_json(400, {"error": "Request body must be a JSON object."})
                return
            try:
                result = service.chat(payload.get("message"))
            except ValueError as exc:
                self._send_json(400, {"error": str(exc)})
                return
            self._send_json(502 if result["status"] == "provider_error" else 200, result)

    return Handler


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local Research Agent chat UI.")
    parser.add_argument("--provider", choices=["openrouter", "openai", "anthropic", "gemini", "ollama"], default="openrouter")
    parser.add_argument("--model", default=None)
    parser.add_argument("--version", default="v3")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--history-window", type=int, default=5)
    parser.add_argument("--max-tool-rounds", type=int, default=4)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")

    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    provider = make_provider(args.provider)
    selected_model = args.model or getattr(provider, "default_model", None)
    artifact_version = build_artifact_version(args.version, system_prompt_path, tools_path)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_path = ROOT / "transcripts" / f"{args.version}_{args.provider}_{timestamp}.transcript.json"
    service = LocalChatService(
        provider=provider,
        provider_name=args.provider,
        system_prompt=system_prompt_path.read_text(encoding="utf-8"),
        tools=to_openai_tools(load_tool_declarations(tools_path)),
        model=selected_model,
        transcript_path=transcript_path,
        version_info=artifact_version_dict(artifact_version),
        history_window=args.history_window,
        max_tool_rounds=args.max_tool_rounds,
    )

    server = ThreadingHTTPServer(("127.0.0.1", args.port), create_handler(service))
    print(f"Research Agent UI: http://127.0.0.1:{server.server_port}")
    print(f"Transcript: {transcript_path}")
    print("Press Ctrl+C to stop the server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping local chat UI.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
