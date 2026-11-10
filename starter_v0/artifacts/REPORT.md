# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team:
- Members:
- Provider/model: openai / gpt-4o-mini

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL, tổng hợp thành digest, và gửi lên Telegram khi được xác nhận."

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL: 

## A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
|  |  |  |
|  |  |  |

## A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi của prompt/tools starter chưa tối ưu |  | 0.65 | `runs/v0_B_base_openai_20261110T102025581585.json` |
| v1 | system_prompt.md | 5 case FAIL (R08/R10/R11/R12/R14) do chỉ dẫn xấu trong prompt: bỏ chúng, thêm rule clarify / yes_no trước khi gửi / không gọi tool khi ngoài phạm vi | 0.65 | 0.90 | `runs/v1_B_base_openai_20261110T105238320919.json` |
| v2 | tools.yaml | Description + convention args rõ ràng; `clarify.response_type` bắt buộc → sửa R11/R12 | 0.90 | 1.00 | `runs/v2_B_base_openai_20261110T110603397674.json` |
| v3 | tools.yaml | Thêm 4 tool mới (hackernews, wikipedia, github_repos, hf_papers); base giữ 1.00, group 1.00, nhưng extension E06 regression (bản tin AI → hf_papers) | 1.00 | 1.00 | `runs/v3_B_base_openai_20261110T111145279017.json` |
| v4 | system_prompt.md | Thêm routing rules → không sửa được E06, còn gây M02/M06 regression | 1.00 | 0.90 | `runs/v4_B_base_openai_20261110T111927623244.json` |
| v5 | system_prompt.md | Rule lookup nêu cả timeframe + rule multi-turn → sửa M02/M06/E06/E08, nhưng R01 hỏi thừa | 0.90 | 0.95 | `runs/v5_B_base_openai_20261110T112057602802.json` |
| v6 | tools.yaml | Mô tả map câu hỏi → policy_area → sửa E01 (extension 1.00) | 0.95 | 0.95 | `runs/v6_B_base_openai_20261110T112307584606.json` |
| v7 | system_prompt.md | Chỉ clarify khi thiếu thông tin bắt buộc → sửa R01; base/group/extension đều 1.00 | 0.95 | 1.00 | `runs/v7_B_base_openai_20261110T112540805267.json` |

## B2. Failure Analysis

Use actual failures from `results[*].result.failures`.

### v0 baseline — openai / gpt-4o-mini

Run: `runs/v0_B_base_openai_20261110T102025581585.json` (artifact `v0+pf0c107a9d7a1+t8db0ba629f52`)

| Metric | v0 |
|---|---:|
| case_accuracy | 0.65 (13/20) |
| tool_routing_accuracy | 0.75 |
| argument_accuracy | 0.65 |
| multiturn_accuracy | 1.00 |

`failure_counts`: wrong_tool 2, out_of_scope 2, missing_info 2, wrong_boundary 1 · `observed_mismatch_counts`: wrong_arg_value 2, unexpected_tool_call 2, missing_tool_call 3

Failure Type = loại lỗi case được thiết kế để bắt (`failure_type` trong eval) / lỗi thực tế quan sát được (`observed_mismatch`).

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | wrong_tool / wrong_arg_value | `lookup(query="AI news", topic="news", timeframe="day", max_results=5)` | `query: expected 'AI', got 'AI news'`: model nhét chữ "news" vào query thay vì để `topic` lo | (dự kiến v2, `tools.yaml`) mô tả `query` chỉ chứa chủ đề; tin tức → `topic=news`, "hôm nay" → `timeframe=day` |
| R08_out_of_scope | out_of_scope / unexpected_tool_call | `send(text="Nguyên hàm của x^2 là x^3/3 + C…")` | Expected no tool call. Prompt ép "luôn chọn một tool" nên model dùng `send` để chứa câu trả lời; tool trả `needs_confirmation`, không gửi thật | (dự kiến v1, `system_prompt.md`) bỏ "Always … pick one tool"; câu ngoài phạm vi research → trả lời text, không gọi tool |
| R10_missing_handle | missing_info / missing_tool_call | `timeline(screenname="sama")` | Missing `clarify`, extra `timeline`: model đoán bừa Sam Altman đúng như prompt bảo | (dự kiến v1) bỏ "pick a well-known account like Sam Altman"; thiếu tài khoản → `clarify(response_type="text")` |
| R11_missing_url | missing_info / missing_tool_call | `fetch(url="https://example.com/article")` | Missing `clarify`, extra `fetch`: model bịa URL | (dự kiến v1) bỏ "assume a likely URL"; thiếu link → `clarify(response_type="text")` |
| R12_confirm_before_send | wrong_boundary / missing_tool_call | `send(text="Bản tin này")` | Missing `clarify`, extra `send`: gửi luôn không hỏi xác nhận | (dự kiến v1) bỏ "just go ahead and do it"; trước khi gửi/đăng → `clarify(response_type="yes_no")` |
| R13_parallel_web_and_tweets | wrong_tool / wrong_arg_value | `lookup(query="AI news", timeframe="day", max_results=5)`, `social_search(query="AI", search_type="Latest", limit=5)` | `query: expected 'AI', got 'AI news'`; `topic: expected 'news', got None`. Routing hai nguồn đúng, sai arg của `lookup` | (dự kiến v2) cùng fix với R03 |
| R14_out_of_scope_coding | out_of_scope / unexpected_tool_call | `send(text="def fibonacci(n): …")` | Expected no tool call. Cùng cơ chế với R08 | (dự kiến v1) cùng fix với R08 |

Nhận xét:
- 5/7 lỗi (R08, R10, R11, R12, R14) đến trực tiếp từ các chỉ dẫn xấu trong `system_prompt.md` → sửa ở prompt (v1).
- 2/7 lỗi (R03, R13) là quy ước arg của `lookup` chưa được khai báo → sửa ở `tools.yaml` (v2).
- Guardrail trong code của `send` (chỉ gửi khi `confirmed=true`) đã chặn cả 3 lần gọi `send` sai → không có tin nhắn nào bị gửi thật. Đây là bằng chứng cần cả guardrail ở code, không chỉ dựa vào prompt.
- Các run v0 `runs/v0_B_base_openrouter_20261110T095049372627.json` và `runs/v0_B_base_openai_20261110T095318273668.json` không dùng làm baseline: 20/20 case `provider_error` do thiếu API key lúc chạy.

## B3. Team Eval Cases

List the 10 cases added to `data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

## B4. Live Chat Evidence

Use `transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

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
| v3 | (cloud) | v3 | tools.yaml | Thêm 4 tool mới (hackernews, wikipedia, github_repos, hf_papers); base giữ 1.00, group 1.00, nhưng extension E06 regression (bản tin AI → hf_papers) | 1.00 | 1.00 | `runs/v3_B_base_openai_20261110T111145279017.json` |
| v4 | system_prompt.md | Thêm routing rules → không sửa được E06, còn gây M02/M06 regression | 1.00 | 0.90 | `runs/v4_B_base_openai_20261110T111927623244.json` |
| v5 | system_prompt.md | Rule lookup nêu cả timeframe + rule multi-turn → sửa M02/M06/E06/E08, nhưng R01 hỏi thừa | 0.90 | 0.95 | `runs/v5_B_base_openai_20261110T112057602802.json` |
| v6 | tools.yaml | Mô tả map câu hỏi → policy_area → sửa E01 (extension 1.00) | 0.95 | 0.95 | `runs/v6_B_base_openai_20261110T112307584606.json` |
| v7 | system_prompt.md | Chỉ clarify khi thiếu thông tin bắt buộc → sửa R01; base/group/extension đều 1.00 | 0.95 | 1.00 | `runs/v7_B_base_openai_20261110T112540805267.json` |
| v3-... | (ollama) | v3 | tools.yaml | Thêm 4 tool mới (hackernews, wikipedia, github_repos, hf_papers); base giữ 1.00, group 1.00, nhưng extension E06 regression (bản tin AI → hf_papers) | 1.00 | 1.00 | `runs/v3_B_base_openai_20261110T111145279017.json` |
| v4 | system_prompt.md | Thêm routing rules → không sửa được E06, còn gây M02/M06 regression | 1.00 | 0.90 | `runs/v4_B_base_openai_20261110T111927623244.json` |
| v5 | system_prompt.md | Rule lookup nêu cả timeframe + rule multi-turn → sửa M02/M06/E06/E08, nhưng R01 hỏi thừa | 0.90 | 0.95 | `runs/v5_B_base_openai_20261110T112057602802.json` |
| v6 | tools.yaml | Mô tả map câu hỏi → policy_area → sửa E01 (extension 1.00) | 0.95 | 0.95 | `runs/v6_B_base_openai_20261110T112307584606.json` |
| v7 | system_prompt.md | Chỉ clarify khi thiếu thông tin bắt buộc → sửa R01; base/group/extension đều 1.00 | 0.95 | 1.00 | `runs/v7_B_base_openai_20261110T112540805267.json` |
| v3-... | (ollama) | v3 | tools.yaml | Thêm 4 tool mới (hackernews, wikipedia, github_repos, hf_papers); base giữ 1.00, group 1.00, nhưng extension E06 regression (bản tin AI → hf_papers) | 1.00 | 1.00 | `runs/v3_B_base_openai_20261110T111145279017.json` |
| v4 | system_prompt.md | Thêm routing rules → không sửa được E06, còn gây M02/M06 regression | 1.00 | 0.90 | `runs/v4_B_base_openai_20261110T111927623244.json` |
| v5 | system_prompt.md | Rule lookup nêu cả timeframe + rule multi-turn → sửa M02/M06/E06/E08, nhưng R01 hỏi thừa | 0.90 | 0.95 | `runs/v5_B_base_openai_20261110T112057602802.json` |
| v6 | tools.yaml | Mô tả map câu hỏi → policy_area → sửa E01 (extension 1.00) | 0.95 | 0.95 | `runs/v6_B_base_openai_20261110T112307584606.json` |
| v7 | system_prompt.md | Chỉ clarify khi thiếu thông tin bắt buộc → sửa R01; base/group/extension đều 1.00 | 0.95 | 1.00 | `runs/v7_B_base_openai_20261110T112540805267.json` |
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
