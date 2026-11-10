---
name: hackernews
track: bonus
kind: live_api
provider: Hacker News Algolia API
requires_env: []
inputs: [query, sort, limit]
outputs: [items]
side_effect: false
---
# hackernews

Tìm story trên Hacker News (cộng đồng dev/tech) qua Algolia API công khai, không cần key.

- `sort="relevance"`: story liên quan nhất (thường là story nhiều điểm).
- `sort="date"`: story mới nhất.
- Mỗi item có `url` (link bài gốc, hoặc link thảo luận HN nếu là Ask/Show HN), `hn_url`, và `summary` = points · comments · author.

Dùng khi user hỏi dân tech / Hacker News đang bàn gì. Không thay thế `lookup` (tin tức web) hay `social_search` (Twitter).
