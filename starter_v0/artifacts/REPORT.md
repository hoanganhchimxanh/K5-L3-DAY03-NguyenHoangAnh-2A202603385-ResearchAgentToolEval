# Day 03 Lab v2 Report — Research Agent

Phần A giới thiệu agent để dùng khi demo; Phần B ghi bằng chứng từ run JSON,
transcript và kết quả kiểm thử. Báo cáo này mô tả **source local v7, 11 tool**.
Bản tích hợp trên GitHub có thêm `citation_audit` và được ghi riêng là
`v7-integration`; không dùng điểm v7 dưới đây làm điểm của bản tích hợp.
Mốc hoàn thành Phần A trước 16:30 và thời điểm nộp bài chưa có bằng chứng xác nhận.

## Team

- Team: HTHT
- Members (4 thành viên): Nguyễn Hoàng Anh — 2A202603385;
  Võ Huy Hoàng — 2A202603397; Nguyễn Trung Anh — 2A202603413;
  Nguyễn Tuấn Hiếu — 2A202603374.
- Provider/model thực tế trong log: **OpenRouter / `openai/gpt-4o-mini`**.
- Tác giả version log: `NguyenHoangAnh-2A202603385`; chưa có dữ liệu phân công
  từng vòng cho các thành viên khác nên không tự gán tên.

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Desk tìm tin web và bài đăng X/Twitter theo chủ đề hoặc tài khoản,
đọc URL, loại trùng và trình bày các item thành digest có nguồn. Agent hỏi lại
khi thiếu dữ liệu; gửi Telegram chỉ khi có nội dung và xác nhận rõ ràng của người dùng.

**Link dùng thử (deploy):**

[Mở Research Desk](https://kelkoo-hospitals-hybrid-packets.trycloudflare.com).
Health endpoint local và public trả HTTP 200 lúc **21:53 ngày 10/11/2026
(Asia/Saigon)**. Đây là Quick Tunnel tạm thời, cần giữ Streamlit và cloudflared
chạy; HTTP 200 không tự chứng minh mọi tool/API thành công. Cách chạy:
`python -m streamlit run app.py` từ `starter_v0` với môi trường đã cài dependencies.

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
| timeline | Lấy bài đăng gần đây của một tài khoản X/Twitter | Không |
| social_search | Tìm bài đăng X/Twitter theo từ khóa, Latest hoặc Top | Không |
| lookup | Tìm web/tin tức theo chủ đề và khoảng thời gian | Không |
| fetch | Đọc nội dung URL đã được cung cấp | Không |
| format | Trình bày item đã có thành bullets, sections, brief hoặc thread | Không |
| send | Gửi nội dung đã được xác nhận lên Telegram; cần cấu hình Telegram | Không, tool bonus có sẵn |
| policy | Tìm các đoạn chính sách trong kho Markdown nội bộ | Không, tool bonus có sẵn |
| papers | Tìm metadata và liên kết bài nghiên cứu arXiv | Không, tool bonus có sẵn |
| paper_text | Tải PDF arXiv và trích văn bản cục bộ | Không, tool bonus có sẵn |
| deduplicate | Giữ item đầu tiên cho mỗi URL, giữ thứ tự và metadata gốc | **Có** |

## A3. Câu hỏi mẫu để thử

1. Lấy 3 bài đăng mới nhất của @sama trên X.
2. Tìm tin web về robotics hôm nay.
3. Tóm tắt bài ở URL https://example.com — dùng URL thật khác nếu muốn thử nội dung cụ thể.
4. Loại tin trùng URL giúp mình. Mình chưa gửi danh sách. Sau khi agent hỏi,
   nhập `[{"title":"Tin A","url":"https://example.com/a"},{"title":"Bản sao","url":"https://example.com/a"},{"title":"Tin B","url":"https://example.com/b"}]`.
5. Sau bước 4: Trình bày các tin đã loại trùng thành dạng bullets.

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Số liệu lấy từ các run JSON thật. Metric trong bảng là `case_accuracy` của bộ base.
Cột `author` trong `version_log.csv` đã ghi tác giả được cung cấp ở mục Team.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo routing và arguments của starter. | - | 0.70 | `runs/v0_B_base_openrouter_20261110T100709207015.json` |
| v1 | artifacts/system_prompt.md | Quy tắc hỏi lại thay chỉ dẫn đoán giúp xử lý thiếu dữ liệu. | 0.70 | 0.90 | `runs/v1_B_base_openrouter_20261110T103208612276.json` |
| v2 | artifacts/system_prompt.md | Phân biệt xác nhận hành động với hỏi bổ sung dữ liệu giúp sửa R12. | 0.90 | 0.85 | `runs/v2_B_base_openrouter_20261110T103734383523.json` |
| v3 | artifacts/tools.yaml | Mô tả ranh giới tool và convention args rõ hơn giúp chọn tool/args đúng. | 0.85 | 1.00 | `runs/v3_B_base_openrouter_20261110T110358630745.json` |
| v4 | tools.yaml; tools/deduplicate; run_eval.py | Thêm loại trùng và chấm args list-object, kiểm tra regression base. | 1.00 | 1.00 | `runs/v4_B_base_openrouter_20261110T112823004195.json` |
| v5 | system_prompt.md | Quyết định hủy mới nhất phải chặn gửi; kiểm tra lại base. | 1.00 | 0.95 | `runs/v5_B_base_openrouter_20261110T113828518552.json` |
| v6 | tools.yaml | Làm rõ alias, args bắt buộc và giữ nguyên items; kiểm tra lại base. | 0.95 | 0.95 | `runs/v6_B_base_openrouter_20261110T114919255600.json` |
| v7 | system_prompt.md | Routing tường minh và nguồn mới nhất giúp sửa chuyển Twitter sang web. | 0.95 | 1.00 | `runs/v7_B_base_openrouter_20261110T204448469549.json` |

- Hai lần chạy v1 trước khi sửa prompt có cùng hash với v0. Chúng vẫn có trong version log, được đánh dấu `changed_artifact=none`; không tính là vòng tối ưu.
- v1 đã thay toàn bộ system prompt; kết quả R10/R11 ủng hộ quy tắc hỏi lại, nhưng không quy toàn bộ mức tăng điểm riêng cho một câu.
- v2 sửa R12 nhưng tổng điểm giảm; giữ nguyên kết quả giảm điểm để phân tích.
- v3 đạt 20/20 trong lần chạy ghi ở trên. Đây là độ đúng routing/args; các lần gọi Twitter trong run này vẫn trả HTTP 403.
- Sau khi thêm tool `deduplicate`, cấu hình hiện tại khác v3. Các lần eval tiếp theo dùng nhãn v4; bản v3 được giữ trong `system_prompt_v3.md` và `tools_v3.yaml`.
- Group: v4 **7/10**, v5 **8/10**, v6 **10/10**, v7 **10/10**; các file run được liệt kê trong B3 và version log.
- v6 còn FAIL M06 trên base; v7 sửa routing và đạt **20/20 base, 10/10 group**.
  Cả bốn metric case/routing/argument/multiturn ở hai run v7 đều là **1.0**,
  `provider_error_cases=0`.
- Artifact v7: `v7+p4b3e9de86e64+t4870fd9a37ff`. Prompt SHA256:
  `4b3e9de86e64762632925d3596bb035c1bb9298ad0594f661731d00444f23043`;
  tools SHA256: `4870fd9a37ffcc81f3e240d4365391b162000fccecf12c73af93b99db89d38b8`.
- `analysis/v7_tool_execution.json` ghi cả 10 lần gọi Twitter trong hai run v7
  trả items/URL, không lỗi tool, sau khi quyền RapidAPI được xử lý. Không sửa
  hay xóa lỗi 403 trong lịch sử v0–v6.
- Một số vòng đổi nhiều dòng/description. Đây là các giả thuyết theo nhóm hành vi;
  chưa phải thí nghiệm cô lập từng dòng. 30/30 là kết quả hai run này, không
  bảo đảm độ đúng ở mọi câu hỏi hoặc lần chạy khác.

## B2. Failure Analysis

Phân biệt nhãn lỗi của đề (`case_failure_type`) với lỗi quan sát (`observed_mismatch`).
Các hàng dưới đây lấy từ trường `result` của các run chính trong B1.

| Case ID / Version | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08 / v0 | out_of_scope / unexpected_tool_call | `send` | Mong đợi không gọi tool khi hỏi toán. | v1 bỏ prompt ép một bước; vẫn cần đọc câu trả lời thủ công. |
| R10 / v0 | missing_info / missing_tool_call | `timeline(screenname="sama")` | Tự đoán tài khoản thay vì hỏi. | v1: gọi clarify khi thiếu tài khoản. |
| R11 / v0 | missing_info / missing_tool_call | `fetch(url="https://example.com/article")` | Tự tạo URL thay vì hỏi. | v1: gọi clarify khi thiếu URL. |
| R12 / v0 | wrong_boundary / missing_tool_call | `send` | Gọi gửi thay vì hỏi xác nhận. Code tool chặn với needs_confirmation. | v2: ưu tiên clarify(response_type=yes_no). |
| R13 / v0 | wrong_tool / wrong_arg_value | `lookup(query="AI news", timeframe="day")` và `social_search` | Query khác "AI" và thiếu topic=news. | v3: làm rõ args của lookup. |
| R14 / v0 | out_of_scope / unexpected_tool_call | `send` | Mong đợi không gọi tool khi hỏi viết code. | v1 bỏ prompt ép một bước; vẫn cần đọc câu trả lời thủ công. |
| R12 / v1 | wrong_boundary / wrong_arg_value | `clarify(response_type="text")` | Hỏi xin nội dung; eval yêu cầu xác nhận yes_no. | v2: tách xác nhận hành động khỏi hỏi nội dung. |
| M02 / v1 | wrong_arg_value / missing_tool_call | `social_search(query="robotics")` | Phải dùng lookup cho tin web hôm nay. | v3: mô tả lookup giữ ngữ cảnh news khi đổi chủ đề. |
| R04 / v2 | wrong_tool / missing_tool_call | `clarify(response_type="yes_no")` | Hỏi xác nhận đọc URL dù đã có đủ thông tin. | v3: đọc URL không cần xác nhận xuất bản. |
| R13 / v2 | wrong_tool / wrong_arg_value | `lookup(query="AI", timeframe="day")` và `social_search` | Thiếu topic=news trong args lookup. | v3: yêu cầu truyền rõ topic=news. |
| M02 / v2 | wrong_arg_value / missing_tool_call | `social_search(query="robotics")` | Chọn social_search thay vì lookup. | v3: phân biệt tìm tin web và bài đăng mạng xã hội. |
| G02 / v4 | missing_info / wrong_arg_value | `clarify(question=...)` | Thiếu args response_type dù runtime có default text. | v6: yêu cầu truyền rõ response_type; v6/v7 PASS. |
| G06 / v4 | missing_info / wrong_arg_value | `deduplicate(items=...)` | Tự thêm source/summary/section rỗng vào items từ lịch sử. | v6: giữ đúng trường gốc, không thêm metadata; v6/v7 PASS. |
| G10 / v4 | wrong_boundary / unexpected_tool_call | `send(confirmed=true)` | Gửi thông báo hủy lên Telegram khi user đã hủy; tool trả lỗi thiếu cấu hình. | v5: hủy thì chỉ trả lời trong chat; v5–v7 PASS. |
| M06 / v6 | wrong_tool / missing_tool_call | `social_search(query="OpenAI", search_type="Latest")` | User chuyển sang web nhưng agent giữ nguồn Twitter. | v7: ưu tiên nguồn mới nhất và routing lookup; v7 PASS. |

Các case `no_tool` chỉ tự động kiểm tra không gọi tool; việc trả lời đúng phạm vi cần đọc thủ công. Không suy ra chất lượng nội dung chỉ từ PASS.

## B3. Team Eval Cases

Đã chạy 10 case tự viết: **5 single turn (G01–G05), 5 multi turn (G06–G10)**.
Kết quả dưới đây lấy từ `runs/v7_B_group_openrouter_20261110T204557011651.json`.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_deduplicate_provided_items | Chọn tool mới và truyền nguyên danh sách tin để tool loại trùng. | deduplicate | PASS |
| G02_missing_items_for_deduplicate | Hỏi khi chưa có danh sách, không tự tạo dữ liệu. | clarify(response_type=text) | PASS |
| G03_explicit_handle_and_limit | Bỏ @ khỏi handle, lấy đúng 3 tweet. | timeline | PASS |
| G04_read_known_url_without_confirmation | Đọc URL đã có, không hỏi xác nhận xuất bản. | fetch | PASS |
| G05_capability_answer_without_tools | Giới thiệu khả năng trực tiếp. | no_tool | PASS |
| G06_deduplicate_items_from_history | Lấy items từ lịch sử để gọi tool mới. | deduplicate | PASS |
| G07_latest_limit_overrides_previous | Giữ tài khoản và cập nhật số lượng từ 7 thành 2. | timeline | PASS |
| G08_followup_web_news_timeframe | Đổi chủ đề, giữ news/day trên web. | lookup | PASS |
| G09_url_supplied_after_missing_request | Khi bổ sung URL thì đọc, không hỏi lại. | fetch | PASS |
| G10_declined_publication_does_not_send | Tôn trọng việc hủy đăng, không gọi send. | no_tool | PASS |

| Version | Group case_accuracy | Multiturn | Run file |
|---|---:|---:|---|
| v4 | 0.70 | 0.60 | `runs/v4_B_group_openrouter_20261110T112954847324.json` |
| v5 | 0.80 | 0.80 | `runs/v5_B_group_openrouter_20261110T113609543206.json` |
| v6 | 1.00 | 1.00 | `runs/v6_B_group_openrouter_20261110T114730561716.json` |
| v7 | 1.00 | 1.00 | `runs/v7_B_group_openrouter_20261110T204557011651.json` |

## B4. Live Chat Evidence

Transcript CLI: `transcripts/v6_openrouter_20261110T121632957739.transcript.json`.
Phiên dùng OpenRouter / `openai/gpt-4o-mini`, artifact
`v6+p447112d94ab0+t4870fd9a37ff`. Giữ đúng nhãn **v6**, không đổi thành v7.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | Loại tin trùng URL; chưa gửi danh sách. | clarify(response_type=text) | CLI v6, turn 1 | waiting_for_user; hỏi danh sách, không bịa items. |
| 2 | Cung cấp 3 items, trong đó 2 cùng URL. | deduplicate(items=3 mục gốc) | CLI v6, turn 2 | answered; input_count=3, item_count=2, removed_count=1. |
| 3 | Trình bày các tin đã loại trùng thành bullets. | format(template=bullets, items=2 mục) | CLI v6, turn 3 | answered; giữ Tin A/Tin B và các URL nguồn. |

UI cũng có phiên 3 lượt tương ứng trong
`transcripts/v6_openrouter_ui_20261110T121235287635_3e39cb8e.transcript.json`.
Đây là thử quy trình bằng dữ liệu mẫu `example.com` do user cung cấp;
không coi đó là bằng chứng tìm kiếm web thật. Bằng chứng Twitter thật nằm ở run v7.

Phiên `transcripts/v6_openrouter_ui_20261110T121408986247_f1dea6b1.transcript.json`
cho thấy giới hạn cần review thủ công: câu hỏi “Đọc 5 điều Bác Hồ dạy” được
trả lời trực tiếp, không có nguồn, và danh sách có các mục không đúng văn bản
chuẩn (chẳng hạn “Tôn trọng pháp luật”). Không coi lượt này là nội dung đạt;
eval `no_tool` chỉ đo việc không gọi tool, không chấm độ đúng của câu trả lời.

## B5. Bonus Evidence

Ghi rõ bằng chứng offline, live và phần chưa làm để tránh nhầm phạm vi.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | `tests/test_tools_examples.py`, `tests/test_tools_todo.py`; R12/G10 trong runs | Offline: chưa xác nhận thì không gửi; confirmed=true tạo đúng request giả lập. v7 hỏi xác nhận/hủy đúng. | Chưa có transcript gửi Telegram thật thành công; không nhận bonus gửi live. |
| arXiv/company policy | `tools/papers/`, `tools/paper_text/`, `tools/policy/`; test policy trong `tests/test_tools_todo.py` | Có khai báo/implementation; unit test policy kiểm tra lọc khu vực và tách untrusted_text. | Chưa có run extension/live arXiv; kết quả truy xuất phải được trích nguồn và kiểm chứng. |
| UI | `app.py`, `ui_session.py`, `UI-README.md`, transcript UI ở B4, `analysis/public_demo.json` | Streamlit có lịch sử, tool results, xác nhận, tải transcript; AppTest offline và chat live. | Tunnel tạm thời; tách phiên khi đổi provider/model/hash, key nằm trong .env. |
| Tool unit tests (`tests/`) | `analysis/pytest_v7.txt`, `analysis/pytest_tools.txt` | Toàn suite v7 **106 passed, 0 failed, 0 skipped**. | HTTP trong unit test được mock, không thay thế kiểm tra API thật. |

`tests/test_tools_todo.py` có **22 hàm test, 31 trường hợp sau tham số hóa**;
riêng tool mới `deduplicate` có **8 hàm, 15 trường hợp**: loại trùng giữ item
đầu và thứ tự, list rỗng, không sửa input, URL thiếu/null, URL khác query/fragment,
sai kiểu container/item/URL phải trả error dict. Tool có `TOOL.md`, registry và YAML.

Chưa có bug trong implementation tool có sẵn được xác nhận/sửa ở vòng này
(không tính bug của evaluator). Có **1 bug evaluator** đã phát hiện:
`normalize_value` cố `sorted()` danh sách dict, gây
`TypeError: '<' not supported between instances of 'dict' and 'dict'`.
Hai regression test ở `tests/test_eval_arguments.py` ban đầu FAIL; sau sửa
`run_eval.py` giữ thứ tự list-object, cả hai PASS. Đây là điều kiện cần để
chấm tool mới chính xác; base eval cũ không có args list-object nên không lộ lỗi.

Ví dụ unit test bổ sung điều eval routing không kiểm tra:
`test_timeline_respects_limit_and_skips_items_without_id` giả lập API trả item
không có tweet_id, kiểm tra tool bỏ item đó, giới hạn đúng 3 kết quả và dựng URL
đúng. Một run model chọn đúng `timeline`/args vẫn có thể PASS routing dù code
xử lý response sai. Test hiện PASS; không tuyên bố đã bắt bug mới trong timeline.

Nhóm thêm 1 tool vào source local này; chưa đạt bonus “hơn 3 tool mới + UI”.

## B6. Reflection

- **Sửa trong system_prompt.md:** nguyên tắc hội thoại chung: kiểm tra lịch sử
  trước khi hỏi; không tự tạo account/URL; hỏi xác nhận trước xuất bản; tôn trọng
  hủy và ưu tiên nguồn/ngữ cảnh mới nhất. v7 sửa M06 từ social_search sang lookup.
- **Sửa trong tools.yaml:** ranh giới từng tool và cách truyền args: timeline
  theo tài khoản, social_search theo chủ đề X, lookup cho news; topic=news,
  timeframe, handle không @, enum Top/Latest; truyền rõ response_type và giữ
  nguyên metadata khi gọi deduplicate. v6 sửa G02/G06 trên group.
- **Cần manual review:** no_tool không chấm sự đúng/sai nội dung (ví dụ UI ở B4);
  routing PASS không bảo đảm API runtime thành công (Twitter 403 ở lịch sử).
  Cần đọc tool_results, kiểm chứng nguồn và xem nội dung trước khi xuất bản.
- **Cải thiện tiếp:** thêm case chưa dùng để tối ưu, lặp eval để đo biến động;
  cô lập từng thay đổi để kiểm chứng giả thuyết; bổ sung chấm chất lượng nội dung,
  trích dẫn và xử lý lỗi API. Thử Telegram live chỉ sau khi cấu hình và được user
  xác nhận nội dung/đích gửi. Bản 12-tool tích hợp trên GitHub cần eval riêng.

## B7. Small Local Model Challenge (bonus)

**Chưa thực hiện bonus Ollama.** Không có run local model, hai model nhỏ hay
hai vòng v4-local/v5-local trong dữ liệu hiện có; không điền điểm hoặc số lỗi giả.
Chưa có cơ sở thực nghiệm để kết luận prompt nào giúp model nhỏ nhất hoặc so sánh
cloud/local. Nếu làm tiếp, cần giữ snapshot cloud, chạy ít nhất hai model ≤8B,
phân loại lỗi và thực hiện hai vòng tối ưu riêng theo README.
