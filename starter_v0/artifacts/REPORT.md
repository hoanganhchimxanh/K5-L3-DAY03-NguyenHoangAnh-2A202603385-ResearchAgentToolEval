# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team:
- Members:
- Provider/model: OpenRouter / `openai/gpt-4o-mini`

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research agent hỗ trợ tìm tin và thông tin trên web, tìm bài đăng theo chủ đề hoặc tài khoản, đọc URL, tra cứu chính sách nội bộ và tìm bài báo khoa học. Agent có thể định dạng digest, kiểm tra metadata trích dẫn và chỉ gửi nội dung qua Telegram sau khi người dùng xác nhận (cần cấu hình Telegram).

**Link dùng thử (deploy):**

Chưa deploy public; hiện chạy local bằng `python chat.py --provider openrouter --version v2`.

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| `clarify` | Hỏi người dùng khi request thiếu thông tin thiết yếu hoặc cần xác nhận gửi. | không |
| `timeline` | Lấy bài đăng gần đây từ một tài khoản cụ thể. | không |
| `social_search` | Tìm bài đăng theo chủ đề hoặc từ khóa trên mạng xã hội. | không |
| `lookup` | Tìm thông tin nền hoặc tin tức trên web theo khoảng thời gian. | không |
| `fetch` | Đọc và trích nội dung từ URL đã biết. | không |
| `format` | Định dạng các kết quả đã thu thập thành digest. | không |
| `send` | Gửi nội dung qua Telegram sau khi người dùng xác nhận. | không |
| `policy` | Tìm nội dung trong tài liệu chính sách nội bộ. | không |
| `papers` | Tìm bài báo khoa học, bao gồm arXiv. | không |
| `paper_text` | Lấy nội dung văn bản của bài báo đã xác định. | không |
| `citation_audit` | Kiểm tra tiêu đề/URL và định dạng metadata trích dẫn; không xác minh độ tin cậy hay nội dung nguồn. | có |

## A3. Câu hỏi mẫu để thử

1. Tin AI hôm nay có gì nổi bật?
2. Tìm các tweet phổ biến nhất về OpenAI.
3. Tóm tắt bài viết này: `https://openai.com/`
4. Tìm 3 bài báo khoa học về ứng dụng AI trong y tế.
5. Kiểm tra và định dạng trích dẫn cho nguồn có tiêu đề “Research paper” và URL `https://example.com/paper`.

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |
| v1 |  |  |  |  |  |
| v2 |  |  |  |  |  |
| v3 |  |  |  |  |  |

## B2. Failure Analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

## B3. Team Eval Cases

List the 10 cases added to `data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

## B4. Live Chat Evidence

Use `transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | What are today's top AI news stories? | `lookup(query="AI", topic="news", timeframe="day")` | v2, OpenRouter `openai/gpt-4o-mini` | Web results returned and summarized. |
| 2 | Summarize the 5 latest tweets for me. | `timeline(screenname="OpenAI", limit=5)` | v2, same transcript | Agent guessed an account instead of clarifying; Twitter API returned an HTTP error. |
| 3 | For Elon Musk. | `timeline(screenname="elonmusk", limit=5)` | v2, same transcript | Agent used the supplied account; Twitter API returned HTTP 403. |

Transcript: `transcripts/v2_openrouter_20261110T112611710992.transcript.json` (3 live turns). Twitter API access returned errors, so live social retrieval was not confirmed working.

## B5. Bonus Evidence

Only fill if your team did bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) |  |  |  |
| arXiv/company policy |  |  |  |
| UI |  |  |  |
| Tool unit tests (`tests/`) | `pytest` output |  |  |

Tool unit tests: số test đã viết, số bug tìm được trong tool có sẵn (nếu có), và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

## B6. Reflection

- Which fixes belonged in `system_prompt.md`?
- Which fixes belonged in `tools.yaml`?
- Which failure needed manual review instead of automatic grading?
- What would you improve next?

## B7. Small Local Model Challenge (bonus)

Only fill if your team did the local model challenge.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-... | (ollama) | v3 |  |  |  |  |  |
| v3-... | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?
