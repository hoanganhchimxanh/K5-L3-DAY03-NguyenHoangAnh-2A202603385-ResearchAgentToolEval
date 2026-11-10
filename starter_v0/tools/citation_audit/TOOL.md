---
name: citation_audit
track: bonus
kind: local_formatter
requires_env: []
inputs: [items]
outputs: [valid, item_count, citations, issues]
side_effect: false
---
# citation_audit

Checks whether collected research items have a title and an HTTP(S) source URL,
then formats the complete entries as citations. It checks citation metadata only;
it does not verify that a source is trustworthy or supports a claim.
