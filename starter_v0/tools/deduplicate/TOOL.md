---
name: deduplicate
track: core
kind: local_formatter
provider: local
requires_env: []
inputs: [items]
outputs: [items, input_count, item_count, removed_count]
side_effect: false
---
# deduplicate

Loại các tin trùng URL trong danh sách đã có. Không gọi mạng hoặc cần API key.

- Dùng khi người dùng muốn loại bản tin trùng hoặc gộp danh sách mà bỏ URL trùng.
- Nếu chưa có danh sách trong yêu cầu hoặc lịch sử, dùng `clarify` để xin dữ liệu.
- Giữ tin đầu tiên của mỗi URL và giữ thứ tự ban đầu.
- Chỉ bỏ khoảng trắng ở hai đầu URL khi so sánh. Không bỏ query string,
  fragment hoặc đổi chữ hoa/thường: các URL đó có thể chỉ tới nội dung khác nhau.
- Tin thiếu URL, URL `null` hoặc rỗng được giữ riêng. Không gộp theo tiêu đề.
- Không sửa dữ liệu đầu vào hoặc tự bổ sung URL.
- `items=[]` hợp lệ. Input không phải list, item không phải object hoặc URL
  sai kiểu trả về dict `error`/`message`, không trả kết quả thành công một phần.

Ví dụ: ba tin có URL lần lượt `https://example.com/a`,
`https://example.com/a`, `https://example.com/b` trả hai tin đầu tiên theo
mỗi URL, `input_count=3`, `item_count=2`, `removed_count=1`.
