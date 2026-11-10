# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team: Rising-Apocalypse
- Members:
- Provider/model: openai / gpt-4o-mini

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Research agent tiếng Việt: tìm tin tức web, tweet theo tài khoản hoặc chủ đề, đọc URL, tra Hacker News / GitHub / Wikipedia / paper AI, tổng hợp thành digest, và chỉ đăng lên Telegram sau khi user xác nhận. Thiếu thông tin thì hỏi lại, không đoán; câu ngoài phạm vi (toán, code) thì từ chối, không gọi tool.

Chạy UI: `streamlit run app.py` (trong `starter_v0/`).

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL: 

## A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại user khi thiếu thông tin; xin xác nhận yes/no trước khi gửi | không |
| timeline | tweet mới nhất của một tài khoản X (tự đổi tên → handle) | không |
| social_search | tìm tweet theo chủ đề (Latest / Top) | không |
| lookup | tìm web / tin tức (topic news, timeframe day/week/…) | không |
| fetch | đọc nội dung một URL | không |
| format | trình bày kết quả thành digest markdown | không |
| send | đăng lên Telegram, chỉ khi `confirmed=true` | không |
| policy / papers / paper_text | tra policy công ty / tìm paper arXiv / đọc full text paper | không |
| hackernews | story trên Hacker News theo chủ đề (liên quan / mới nhất) | **có** |
| wikipedia | tóm tắt một bài Wikipedia (en/vi) cho kiến thức nền | **có** |
| github_repos | tìm repo open-source trên GitHub (stars / updated) | **có** |
| hf_papers | paper AI trending hôm nay trên Hugging Face | **có** |

## A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1. Tin tức AI hôm nay có gì nổi bật?
2. Cho mình 3 tweet mới nhất của Andrej Karpathy
3. Dân dev trên Hacker News đang bàn gì về Rust?
4. Transformer trong deep learning là gì?
5. Đăng bản tin này lên Telegram giúp mình (agent phải hỏi xác nhận trước)

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

Run v7: `runs/v7_B_group_openai_20261110T112602516587.json` (10/10). Lần đầu chạy trên v3: `runs/v3_B_group_openai_20261110T111227772582.json` (10/10).

| Case ID | What It Tests | Expected Tool/Behavior | Result (v7) |
|---|---|---|---|
| G01_hackernews_routing | dân dev/HN bàn gì → tool mới | `hackernews(query="Rust")` | PASS |
| G02_wikipedia_concept | "X là gì" → kiến thức nền, không phải tin tức | `wikipedia` | PASS |
| G03_github_popular_repos | "phổ biến nhất" → sort | `github_repos(sort="stars")` | PASS |
| G04_hf_trending_papers | paper hot hôm nay, không từ khoá | `hf_papers` | PASS |
| G05_handle_with_at_sign | handle có "@" phải bỏ "@" | `timeline(screenname="karpathy", limit=3)` | PASS |
| G06_send_declined (multi) | đã hỏi xác nhận, user từ chối | không gọi tool | PASS |
| G07_clarify_then_wikipedia (multi) | hỏi lại khái niệm rồi tra | `wikipedia` | PASS |
| G08_switch_web_to_hackernews (multi) | đổi nguồn, "mới nhất" | `hackernews(query="Rust", sort="date")` | PASS |
| G09_github_carryover (multi) | giữ chủ đề, đổi sort, đổi limit | `github_repos(sort="updated", limit=3)` | PASS |
| G10_correction_new_handle (multi) | sửa người, map tên → handle, giữ limit | `timeline(screenname="demishassabis", limit=5)` | PASS |

Nhận xét: bộ group pass 10/10 ngay từ v3, tức là chưa đủ khó. Các lỗi thật được phát hiện nhờ bộ `eval_research_extension.json` (E01, E06, E08).

## B4. Live Chat Evidence

Use `transcripts/*.transcript.json`.

Transcript: `transcripts/v7_openai_20261110T113554847510.transcript.json` (artifact `v7+pf7b92009b3ed+t1d5f3e291bc6`, chạy bằng `chat.py`).

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | Tin tức AI hôm nay có gì nổi bật? | `lookup(query="AI", topic="news", timeframe="day")` | v7 | Đúng: trả tin kèm nguồn |
| 2 | Tóm tắt 3 tweet mới nhất giúp mình | `social_search(query="AI", limit=3)` | v7 | **Đáng bàn:** không hỏi "của ai" mà lấy chủ đề AI từ lượt 1. Eval single-turn R10 thì pass (hỏi lại); trong chat có history thì model tự suy ra chủ đề |
| 3 | Của Andrej Karpathy nhé | `timeline(screenname="karpathy", limit=3)` | v7 | Đúng: map tên → handle, giữ limit=3 |
| 4 | Đăng bản tin AI hôm nay lên Telegram giúp mình | `clarify(response_type="yes_no")` | v7 | Đúng: hỏi xác nhận, không gửi |
| 5 | Thôi khoan, đừng đăng | (không gọi tool) | v7 | Đúng: không gọi `send` |

## B5. Bonus Evidence

Only fill if your team did bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | transcript trên, lượt 4–5 | Agent hỏi `yes_no` trước, user từ chối thì không gửi | Guardrail 2 lớp: prompt + code (`send` không gọi API khi `confirmed=false`; ở v0 nó đã chặn 3 lần gọi sai) |
| arXiv/company policy | `runs/v7_B_extension_openai_20261110T112625920110.json` (10/10) | Route đúng `policy` + `policy_area`, `papers`, `paper_text` | Nội dung policy là untrusted: dòng giống lệnh bị tách vào `untrusted_text` (có unit test) |
| UI | `app.py` (Streamlit) | Chat nhiều lượt, xem args/kết quả từng tool, tự lưu transcript | Dùng key API của máy chạy, nên chỉ mở link public khi demo |
| Tool unit tests (`tests/`) | `pytest`: 130 passed, 0 skipped | Điền 14 stub TODO + test cho 4 tool mới (≥ 3/tool) + regression test | Offline, mock HTTP |

Tool unit tests: số test đã viết, số bug tìm được trong tool có sẵn (nếu có), và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

**Bug tìm được (1):** `timeline` / `social_search` tính `items[: int(limit or 5)]`. Model gửi `limit=-1` thì tool âm thầm bỏ mất item cuối (3 tweet → 2; 1 tweet → 0); `limit="abc"` biến một response tốt thành lỗi `ValueError`. Đã sửa bằng `clamp_int()` trong `tools/_shared.py`; regression test là `test_timeline_bad_limit_from_model_falls_back_to_default` và `test_social_search_negative_limit_does_not_drop_last_item`. Eval không thể bắt lỗi này, vì eval chỉ chấm tên tool + args, không chấm tool trả về bao nhiêu item.

## B6. Reflection

- **Fix thuộc `system_prompt.md`:** hành vi chung: khi nào hỏi lại, xác nhận trước khi gửi, từ chối ngoài phạm vi (v1: 0.65 → 0.90), quy tắc multi-turn (v5), chỉ hỏi khi thiếu thông tin bắt buộc (v7).
- **Fix thuộc `tools.yaml`:** convention args và ranh giới từng tool: `response_type` bắt buộc, `yes_no` cho send (v2: R11/R12), map câu hỏi → `policy_area` (v6: E01). Khi prompt và description mâu thuẫn thì description thắng: rule routing ở v4 không sửa được E06 (bản tin AI → `hf_papers`); phải thêm rule rất cụ thể ở v5 mới hết.
- **Bài học về regression:** sửa chỗ này hay hỏng chỗ khác. Thêm tool (v3) làm hỏng E06; rule ví dụ ở v4 chỉ nêu `topic` nên model bỏ `timeframe` (M02); câu "đừng để default" ở v5 làm model hỏi thừa số lượng tweet (R01). Vì vậy mỗi version phải chạy lại cả 3 bộ eval. Model cũng có nhiễu: chạy v4 base 2 lần được 0.95 và 0.90.
- **Cần xem tay:** R12 ở v1 (user nói "bản tin này" mà không có nội dung; hỏi lại nội dung cũng hợp lý dù eval chấm fail), và lượt 2 trong chat live (tự suy ra chủ đề từ history thay vì hỏi).
- **Cải thiện tiếp:** viết eval group khó hơn (bộ hiện tại pass 10/10 ngay); chạy mỗi version nhiều lần để đo độ ổn định; thêm case multi-turn có history thật như trong chat.

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
