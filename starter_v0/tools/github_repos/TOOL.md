---
name: github_repos
track: bonus
kind: live_api
provider: GitHub Search API
requires_env: []
inputs: [query, sort, limit]
outputs: [items]
side_effect: false
---
# github_repos

Tìm repository mã nguồn mở công khai trên GitHub, không cần key (giới hạn ~10 request/phút khi không xác thực; vượt giới hạn sẽ trả error dict `HTTPError`).

- `sort="stars"`: repo nhiều sao nhất (phổ biến).
- `sort="updated"`: repo mới cập nhật gần đây.
- Mỗi item có full_name, url, description, stars, language, updated_at.

Dùng khi user muốn tìm thư viện / framework / project open-source về một chủ đề. Không dùng để đọc nội dung một repo cụ thể (dùng `fetch` với URL).
