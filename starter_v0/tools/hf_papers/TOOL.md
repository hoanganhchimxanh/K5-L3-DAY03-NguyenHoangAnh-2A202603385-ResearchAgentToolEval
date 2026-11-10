---
name: hf_papers
track: bonus
kind: live_api
provider: Hugging Face Daily Papers API
requires_env: []
inputs: [date, limit]
outputs: [items]
side_effect: false
---
# hf_papers

Lấy danh sách **Daily Papers** của Hugging Face: các paper AI được cộng đồng chọn/upvote mỗi ngày. Không cần key.

- `date=""`: danh sách mới nhất. `date="YYYY-MM-DD"`: danh sách của ngày đó; sai format trả error dict, không gọi API.
- Mỗi item có title, url (trang HF), summary (cắt 600 ký tự), `arxiv_id` (đưa tiếp vào `paper_text` để đọc full text), upvotes.

Dùng khi user hỏi "paper AI nổi bật / trending hôm nay". Tìm paper theo từ khoá thì dùng `papers` (arXiv).
