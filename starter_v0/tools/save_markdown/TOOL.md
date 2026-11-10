---
name: save_markdown
track: bonus
kind: local_formatter
requires_env: []
inputs: [content, filename]
outputs: [file_name, download_url, character_count]
side_effect: local_file_write
---
# save_markdown

Writes an assistant answer or user-approved Markdown document into the local
`starter_v0/exports/` directory and returns a localhost download URL. Use only
when the user explicitly asks to export or download an answer as a `.md` file.
It never overwrites an existing file. The filename is reduced to a safe slug.
