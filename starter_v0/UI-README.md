# Research Desk — Streamlit

Chạy các lệnh sau từ `starter_v0/`. Dùng môi trường `.venv` ở thư mục gốc
workspace đã được tạo để tránh lỗi đường dẫn dài trên Windows.

```powershell
# Khi terminal đã kích hoạt môi trường ảo:
python -m streamlit run app.py

# Nếu chưa kích hoạt, gọi trực tiếp:
..\..\.venv\Scripts\python.exe -m streamlit run app.py
```

Mở `http://localhost:8501`. UI đọc `.env` trong `starter_v0/`; không nhập key
trên giao diện. Chọn provider, để trống model nếu muốn dùng mặc định.

UI có lịch sử hội thoại, câu hỏi mẫu, trả lời xác nhận bằng nút hoặc chat,
nguồn tham khảo và phần xem tool calls/results. Transcript thật được ghi
vào `transcripts/*.transcript.json` sau mỗi lượt và tải được từ sidebar.
Phiên mới không xóa các transcript đã ghi. UI dùng phiên bản v7 và tự tạo
phiên mới khi provider/model hoặc hash prompt/tools thay đổi. Tải lại trang
để dùng cấu hình mới nhất.

## Thử live và lấy bằng chứng

Thử ít nhất ba lượt thật, ví dụ:

1. `Loại tin trùng URL giúp mình. Mình chưa gửi danh sách.`
2. `Danh sách đây: [{"title":"Tin A","url":"https://example.com/a"},{"title":"Bản sao","url":"https://example.com/a"},{"title":"Tin B","url":"https://example.com/b"}]`
3. `Trình bày các tin đã loại trùng thành dạng bullets.`

Kiểm tra rằng lượt 1 hỏi lại, lượt 2 gọi `deduplicate`, lượt 3 dùng dữ liệu
đã có để gọi `format`, và transcript có đủ tool events cùng hash phiên bản.

README của đề còn yêu cầu live qua `chat.py`; chạy riêng:

```powershell
python chat.py --provider openrouter --version v7-integration
```

Nhập ba lượt ở trên, rồi `/exit`. Ghi đường dẫn transcript thật vào REPORT B4.
Các transcript do unit test tạo nằm trong thư mục tạm, không dùng làm bằng chứng live.

## Link dùng thử

Link đang được mở cho phiên demo hiện tại:

https://kelkoo-hospitals-hybrid-packets.trycloudflare.com

Đã kiểm tra trang chủ/health HTTP 200 và WebSocket. Streamlit cần tiếp tục
chạy ở cổng 8501; cloudflared đang chạy nền. Khi đóng máy, dừng UI hoặc
tắt tunnel, link sẽ ngừng hoạt động.

Từ `starter_v0/`, bật lại tunnel hoặc xem lại link đang chạy:

```powershell
powershell -NoProfile -ExecutionPolicy RemoteSigned -File .\scripts\start_public.ps1
```

Tắt riêng tunnel sau demo (giữ UI local):

```powershell
powershell -NoProfile -ExecutionPolicy RemoteSigned -File .\scripts\stop_public.ps1
```

Bản portable đã kiểm SHA256 nằm ở `.tools/cloudflared.exe` tại gốc workspace.
Script cũng hỗ trợ `cloudflared` đã cài trong PATH hoặc tham số
`-CloudflaredExe`. Tạo tunnel mới sẽ có URL mới; cập nhật URL đó vào REPORT A1.
Thông tin tiến trình/log nằm trong `.runtime/`, được bỏ qua khi commit.

Sau khi UI chạy, nếu đã cài Cloudflare Tunnel thì mở terminal thứ hai:

```powershell
cloudflared tunnel --url http://localhost:8501
```

Dán URL được trả về vào REPORT A1. Link tạm hoạt động khi cả Streamlit và
tunnel còn chạy. Không đưa `.env` vào repo nộp bài.

## Kiểm tra offline

```powershell
python -m pytest -q
```

Nếu Windows báo không truy cập được thư mục tạm `pytest-of-Admin`, dùng
thư mục tạm trong môi trường ảo ở gốc workspace:

```powershell
New-Item -ItemType Directory -Force ..\..\.venv\.test-tmp | Out-Null
python -m pytest -q --basetemp ..\..\.venv\.test-tmp\ui-local
```

Test UI dùng Streamlit AppTest và provider giả lập, không gọi API thật.
PASS ở unit test hoặc eval routing không tự chứng minh các API nguồn hoạt động.
Trong hai run v7 đã đối chiếu, cả 10 lần gọi timeline/social_search đều trả
items có URL và không có lỗi tool. Lỗi RapidAPI 403 ở các run trước là lịch sử
trước khi tài khoản được subscribe đúng API; xem `analysis/v7_tool_execution.json`.

Tham khảo: [Streamlit chat](https://docs.streamlit.io/develop/api-reference/chat/st.chat_input)
và [AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest).
