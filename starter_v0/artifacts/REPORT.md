# Day 03 Lab — Research Agent Report

## Team

- Team: HTHT
- Members:
  - Nguyễn Hoàng Anh - 2A202603385
  - Võ Huy Hoàng - 2A202603397
  - Nguyễn Trung Anh - 2A202603413
  - Nguyễn Tuấn Hiếu - 2A202603374
- Provider/model used for recorded runs: OpenRouter / `openai/gpt-4o-mini`

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Agent hỗ trợ tìm kiếm tin tức và thông tin trên web, tìm bài đăng theo chủ đề hoặc tài khoản, đọc URL, tra cứu chính sách nội bộ và tìm bài báo khoa học. Agent có thể định dạng digest, kiểm tra metadata trích dẫn, xuất câu trả lời thành file Markdown để tải trong chat, và chỉ gửi nội dung Telegram sau khi người dùng xác nhận (cần cấu hình Telegram).

**Chạy giao diện chat local** (từ thư mục `starter_v0/`):

```powershell
python local_chat_ui.py --provider openrouter --version v3
```

Mở `http://127.0.0.1:8765`; nhấn `Ctrl+C` trong terminal để dừng server. UI chỉ bind loopback, chưa deploy public. Mỗi phiên được ghi vào `transcripts/*.transcript.json`.

## A2. Tool agent có

| Tool | Chức năng | Tool mới của nhóm? |
|---|---|---|
| `clarify` | Hỏi người dùng khi thiếu thông tin thiết yếu hoặc cần xác nhận. | Không |
| `timeline` | Lấy bài đăng gần đây từ một tài khoản cụ thể. | Không |
| `social_search` | Tìm bài đăng theo chủ đề/từ khóa trên mạng xã hội. | Không |
| `lookup` | Tìm thông tin nền hoặc tin tức trên web theo khoảng thời gian. | Không |
| `fetch` | Đọc nội dung từ URL đã biết. | Không |
| `format` | Định dạng dữ liệu đã thu thập thành digest. | Không |
| `send` | Gửi nội dung qua Telegram sau khi người dùng xác nhận. | Không |
| `policy` | Tìm trong tài liệu chính sách nội bộ. | Không |
| `papers` | Tìm bài báo khoa học, bao gồm arXiv. | Không |
| `paper_text` | Lấy văn bản từ bài báo đã xác định. | Không |
| `citation_audit` | Kiểm tra tiêu đề/URL và định dạng citation metadata; không xác minh độ tin cậy hay nội dung nguồn. | Có |
| `save_markdown` | Lưu câu trả lời thành `.md` vào `exports/`, trả link tải local và không ghi đè file cũ. | Có |
| `save_markdown` | Lưu câu trả lời thành `.md` vào thư mục `exports/` và trả link tải local; không ghi đè file cũ. | Có |

## A3. Câu hỏi mẫu

1. Tin AI hôm nay có gì nổi bật?
2. Tìm các tweet phổ biến nhất về OpenAI.
3. Tóm tắt bài viết này: `https://openai.com/`
4. Tìm 3 bài báo khoa học về ứng dụng AI trong y tế.
5. Xuất câu trả lời thành file Markdown có tên `ai-research`.

---

# PHẦN B — Chi tiết và bằng chứng

## B1. Version evidence

Các metric dưới đây lấy từ run JSON của base eval, 20 cases mỗi run. `v1` là run được ghi trong version log; có nhiều lần chạy cùng version và kết quả có dao động.

| Version | Thay đổi / giả thuyết | Metric trước → sau | Run |
|---|---|---:|---|
| v0 | Baseline; đo hành vi trước tối ưu. | — → 0.75 (15/20) | `runs/v0_B_base_openrouter_20261110T101952785209.json` |
| v1 | Prompt ngừng khuyến khích đoán và yêu cầu `clarify` khi thiếu handle/URL; kỳ vọng giảm gọi tool bằng thông tin bịa. | 0.75 → 0.90 (18/20) | `runs/v1_B_base_openrouter_20261110T105630083903.json` |
| v2 | Thêm quy tắc xác nhận trước khi gửi; bổ sung tool `citation_audit`. Kỳ vọng `clarify` xử lý boundary gửi tốt hơn; tool mới không được đo bởi base eval. | 0.90 → 0.95 (19/20) | `runs/v2_B_base_openrouter_20261110T110808093470.json` |
| v3 | Thêm tool `save_markdown`, prompt rule xuất file theo yêu cầu, và link tải trong UI. | 0.95 → 0.95 (19/20) | `runs/v3_B_base_openrouter_20261110T220359376452.json` |

Metric chi tiết: v0 routing 0.80 / arguments 0.75 / multi-turn 1.00; v1 được chọn routing 1.00 / arguments 0.90 / multi-turn 1.00; v2 routing 1.00 / arguments 0.95 / multi-turn 1.00; v3 routing 1.00 / arguments 0.95 / multi-turn 1.00. Không có provider error trong các base run được ghi ở bảng.

**Giới hạn so sánh:** v3 giữ base accuracy 0.95 so với v2; không tăng điểm base eval vì base suite không kiểm tra xuất Markdown. v3 có prompt/tool hashes riêng trong run JSON; metric group được báo riêng bên dưới.

## B2. Failure analysis

| Run/case | Bằng chứng lỗi | Phân tích và xử lý |
|---|---|---|
| v0 — `R08_out_of_scope` | `unexpected_tool_call`; gọi `send` để trả lời bài tích phân. | Prompt cũ khuyến khích luôn dùng tool/làm một bước. Prompt hiện tại giới hạn tool trong research scope; chưa có run riêng chứng minh sửa này trên phiên bản cuối. |
| v0 — `R10_missing_handle`, `R11_missing_url` | `missing_tool_call`; gọi `timeline(screenname="sama")` và `fetch(url="https://example.com/article")` thay vì `clarify`. | Prompt mới yêu cầu không đoán handle/URL và hỏi khi thiếu dữ liệu. Các case này pass trong run v1 được ghi. |
| v0 — `R12_confirm_before_send` | `missing_tool_call`; gọi `send` trước xác nhận. | Bổ sung quy tắc yêu cầu xác nhận yes/no. Ở run v1 0.90, agent đã gọi `clarify` nhưng sai `response_type="text"` thay vì `yes_no`; lỗi boundary được sửa theo hướng dẫn rõ hơn. |
| v0/v1/v2 — `R13_parallel_web_and_tweets` | v0 thiếu `topic="news"` và query là `AI news`; v1/v2 đã route đúng cả `lookup` và `social_search`, nhưng query lookup vẫn là `tin tức AI` thay vì `AI`. `observed_mismatch=wrong_arg_value`. | Đây là lỗi còn lại trong run v2: tách subject khỏi intent tin tức. Tool description và prompt đã được làm rõ sau run v2; cần eval lại để xác minh. |

Trong v1, các run không đồng nhất: run 10:30 đạt 0.80, còn hai run sau đạt 0.90. Vì vậy không nên diễn giải một lần chạy là bảo đảm kết quả luôn lặp lại.

## B3. Team eval cases

`data/eval_group.json` hiện có **2 cases**, chưa đủ mục tiêu 10 case (5 single-turn và 5 multi-turn). Run v3 group đạt 2/2 (1.00).

| Case | Điều cần kiểm tra | Kỳ vọng | Kết quả |
|---|---|---|---|
| `G01_citation_audit` | Route yêu cầu kiểm tra/định dạng metadata citation tới tool mới. | `citation_audit(items=[{title, url}])` | PASS, v3 group run `runs/v3_B_group_openrouter_20261110T220513363205.json`. |
| `G02_export_markdown` | Chỉ gọi tool xuất file khi user yêu cầu; truyền tên file và nội dung Markdown. | `save_markdown(content=..., filename="ai-research.md")` | PASS, v3 group run `runs/v3_B_group_openrouter_20261110T220513363205.json`. |

## B4. Live chat

| Transcript | Lượt | Request | Tool call | Kết quả |
|---|---:|---|---|---|
| `transcripts/v2_openrouter_20261110T112611710992.transcript.json` | 1 | Hỏi các tin AI nổi bật hôm nay. | `lookup(query="AI", topic="news", timeframe="day")` | Web results được trả về và tóm tắt. |
| Cùng transcript | 2 | Yêu cầu 5 tweet mới nhất nhưng chưa nêu tài khoản. | `timeline(screenname="OpenAI", limit=5)` | Agent tự đoán tài khoản; API trả HTTP error. |
| Cùng transcript | 3 | Bổ sung “For Elon Musk.” | `timeline(screenname="elonmusk", limit=5)` | Dùng tài khoản đã cung cấp; API trả HTTP 403. |
| `transcripts/v2_openrouter_20261110T215020117769.transcript.json` | 2 | Giới thiệu khả năng agent; sau đó hỏi thời tiết. | Câu đầu không gọi tool; câu sau gọi `lookup`. | Transcript UI ghi hai lượt; câu hỏi thời tiết được route thành general web search. |

Social API trả lỗi trong live chat, nên transcript không chứng minh social retrieval hoạt động thành công. Các run live dùng OpenRouter `openai/gpt-4o-mini`, nhãn artifact v2.

## B5. Bonus và kiểm thử

| Hạng mục | Bằng chứng | Kết quả / giới hạn |
|---|---|---|
| `send` / Telegram | Unit tests trong `tests/test_tools_todo.py` và `tests/test_tools_examples.py` | Đã kiểm tra mock gửi khi confirmed và không gửi khi chưa xác nhận. Telegram credentials chưa cấu hình; không thực hiện gửi thật. |
| `policy`, `papers`, `paper_text` | Registry và tool declarations | Có tool; không có bằng chứng live/API eval ở các run được ghi. |
| `citation_audit` | `tools/citation_audit/` và 4 unit tests | Happy path, input sai, entry sai kiểu và citation thiếu URL được kiểm tra. |
| `save_markdown` | `tools/save_markdown/`, `runs/v3_B_group_openrouter_20261110T220513363205.json`, `exports/ai-research-2.md` | Group eval xác nhận model gọi tool và tool tạo file. UI tạo link tải từ tên file; file được lưu UTF-8, tên được slug hóa, file trùng tên không bị ghi đè. |
| Local chat UI | `local_chat_ui.py`, `tests/test_local_chat_ui.py` | UI được mở trên browser và gửi message thành công trong phiên kiểm tra. Local-only; chưa deploy public. |
| Unit tests | Full `pytest -q` sau khi thêm export Markdown | **98 passed, 0 failed, 0 skipped.** Không xác nhận được bug regression mới trong tool có sẵn; đây là kiểm tra hành vi hiện tại. |

## B6. Reflection

- **Nên sửa trong `system_prompt.md`:** routing giữa timeline/search/web/fetch; hỏi lại khi thiếu thông tin; không gọi tool ngoài scope; xác nhận trước hành động gửi; chỉ gọi `save_markdown` khi user yêu cầu xuất file.
- **Nên sửa trong `tools.yaml`:** mô tả chính xác convention args (`screenname` không có `@`, `topic=news`, `timeframe`, `Top|Latest`), boundary `send`, và khi nào dùng `save_markdown`.
- **Cần xem xét thủ công:** HTTP errors/403 từ Twitter là lỗi truy cập provider/API, không phải bằng chứng model route sai. Ngược lại, query `tin tức AI` thay vì subject `AI` là lỗi argument mà metric tự động bắt được.
- **Bước tiếp theo:** còn 8 group cases để đạt mục tiêu 10; base eval v3 còn lỗi xác nhận `yes_no` ở R12; kiểm tra/cấu hình RapidAPI Twitter nếu cần live social data.

## B7. Small Local Model Challenge

Chưa chạy Ollama/local model; không có số liệu hoặc failure pattern để báo cáo. Không suy diễn kết quả local từ các run OpenRouter.
