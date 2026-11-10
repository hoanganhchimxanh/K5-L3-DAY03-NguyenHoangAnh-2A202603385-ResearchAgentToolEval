# Rà soát yêu cầu Day 03

Đối chiếu theo `../README.md`, code hiện tại, run JSON và transcript thật.
Kết luận sau v7: các mục kỹ thuật và bằng chứng bắt buộc đã có. Routing tường minh
và quyền RapidAPI đã được xử lý. Còn chốt đúng thông tin nhóm trong REPORT,
giữ link demo hoạt động và loại secrets/môi trường ảo khi đóng gói.

## Các mục đã đạt

| Yêu cầu | Bằng chứng | Kết quả |
|---|---|---|
| Provider thật | Các run OpenRouter và transcript CLI/UI dùng openai/gpt-4o-mini | Đạt |
| Ít nhất 5 tool | 11 tool khai báo và 11 implementation đăng ký | Đạt |
| Baseline và ít nhất 3 vòng tối ưu | Có v0–v7; v1/v2/v3 có thay đổi hash tương ứng | Đạt về run/version evidence |
| Version log | 14 dòng run thật; file, hash và metric_after khớp JSON | Đạt |
| Phân tích lỗi | REPORT B2 ghi case, loại lỗi, actual calls và cách xử lý | Đạt |
| Bỏ chỉ dẫn xấu của starter | Prompt bỏ đoán URL/account, gửi ngay và ép một bước | Đạt |
| Routing trong system prompt | v7 ghi rõ timeline/social_search/lookup/fetch/clarify và ưu tiên nguồn mới nhất | Đạt |
| Tool description và convention args | Đã mô tả khi dùng/không dùng, handle, topic/timeframe, Top/Latest và xác nhận send | Đạt |
| Ít nhất 1 tool mới | deduplicate có tool.py, TOOL.md, registry và YAML | Đạt |
| Ít nhất 3 test/tool mới | 8 hàm test deduplicate, 15 trường hợp khi tham số hóa | Đạt |
| Test xanh và không còn skip | Sau cập nhật UI v7: 106 passed in 12.26s, 0 failed, 0 skipped | Đạt |
| 10 eval case nhóm | Đúng 5 single turn + 5 multi turn; có case cho tool mới | Đạt |
| Chạy eval nhóm | v7: group 10/10; base 20/20 | Đạt |
| Runtime của tool Twitter | Cả 10 lần gọi timeline/social_search trong v7 có items/URL, không lỗi tool | Đã xử lý quyền truy cập |
| Không sửa case base | Input, expect và metadata của 20 case khớp bản ghi v0 | Đạt kiểm tra đối chiếu |
| UI Streamlit | app.py, ui_session.py; AppTest và transcript UI thật | Đạt |
| Link dùng thử | URL trong REPORT A1; kiểm tra lại health/home HTTP 200 | Đạt ở thời điểm rà soát |
| Chat live qua chat.py | Transcript CLI có đúng 3 lượt: clarify, deduplicate, format | Đạt |
| REPORT A/B | Có giới thiệu, tool, câu hỏi mẫu, version, lỗi, eval, live chat và reflection | Đã có nội dung; thông tin nhóm còn thiếu |
| Nguồn nộp không chứa key thật | Quét các file text dự kiến nộp, kết quả trong analysis/final_audit_checks.json | Loại .env/runtime/venv khi đóng gói |

## Các điểm rà soát trước đã xử lý

### 1. Routing trong system_prompt.md

Đã thêm routing cho 5 tool vào `artifacts/system_prompt.md`, bao gồm giữ nguồn
được yêu cầu mới nhất khi người dùng đổi từ Twitter sang web. Hai run v7 có
prompt hash mới và tools hash giữ nguyên v6. M06 đã PASS; base 20/20, group 10/10.

### 2. Quyền truy cập RapidAPI Twitter45

Lần rà soát trước gặp HTTP 403 với thông báo:

> You are not subscribed to this API.

Người dùng đã subscribe đúng API. Hai run v7 có tổng cộng 10 lần gọi Twitter
trả items và URL thật, không có lỗi thực thi tool. Bằng chứng chi tiết trong
`analysis/v7_tool_execution.json`. Các lỗi 403 ở log v0–v6 được giữ nguyên vì
chúng là lịch sử trước khi quyền truy cập được xử lý.

## Còn chốt: thông tin nhóm

REPORT đã có NguyenHoangAnh / MSSV 2A202603385 và tác giả version log đúng thông tin
được cung cấp. Dòng Team và các thành viên khác vẫn ghi chưa được cung cấp;
cần điền đúng thông tin thực tế trước khi nộp.

## Các giới hạn cần giữ trong báo cáo

- M06 FAIL trong v6 và PASS trong v7; giữ cả hai kết quả trong báo cáo.
- 30/30 case của v7 là kết quả trên hai bộ đã chạy, không chứng minh agent
  luôn đúng trong mọi yêu cầu hoặc qua mọi lần chạy.
- v1 thay toàn bộ prompt; v3/v6 đổi nhiều description. Không quy toàn bộ chênh lệch
  điểm cho một dòng riêng lẻ; REPORT đã ghi giới hạn của việc tách tác động.
- PASS no_tool không tự xác nhận tính đúng của nội dung; phiên UI hỏi kiến thức
  không có nguồn cần đọc và kiểm chứng thủ công.
- Link Quick Tunnel là tạm thời: giữ Streamlit/tunnel chạy và cập nhật REPORT
  nếu tạo hostname mới.
- Poster, gửi Telegram live, thêm hơn 3 tool và Ollama là bonus/tùy chọn,
  không tính là phần bắt buộc còn thiếu.
- Việc đạt mốc giờ demo/nộp không được xác nhận chỉ từ kiểm tra code này.

## Khi đóng gói

Nộp source, artifacts, data, tests, runs, transcripts, analysis và cấu hình UI
cần thiết. Loại `.env` (giữ `.env.example`), `.venv/`, `.runtime/`,
`__pycache__/` và `.pytest_cache/`. Không đưa API key vào bản nộp.

Chi tiết kiểm tra tự động: `analysis/final_audit_checks.json`,
`analysis/pytest_v7.txt` và `analysis/v7_tool_execution.json`. Transcript live
hiện có là của v6 và được ghi đúng nhãn; không đổi chúng thành bằng chứng live v7.
Việc nộp bài thực tế và mốc giờ demo/nộp cần người dùng xác nhận riêng.
