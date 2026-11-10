---
name: wikipedia
track: bonus
kind: live_api
provider: Wikipedia REST API
requires_env: []
inputs: [title, lang]
outputs: [items, status]
side_effect: false
---
# wikipedia

Lấy đoạn tóm tắt mở đầu của **một** bài Wikipedia (`en` hoặc `vi`), không cần key.

- `status="ok"`: có kết quả trong `items[0]` (title, url, summary, description).
- `status="not_found"`: không có bài với tiêu đề đó (HTTP 404), trả `items=[]`, không raise.
- `status="disambiguation"`: tiêu đề mơ hồ (nhiều nghĩa); agent nên hỏi lại hoặc thử tiêu đề cụ thể hơn.

Dùng cho kiến thức nền ổn định (khái niệm, tiểu sử, tổ chức), ví dụ "Transformer là gì". Không dùng cho tin tức mới.
