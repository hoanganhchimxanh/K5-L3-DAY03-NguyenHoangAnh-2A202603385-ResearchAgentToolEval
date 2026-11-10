# Source integration on NguyenTuanHieu_2A202603374

The initial source integration preserved `starter_v0/artifacts/REPORT.md` from
the target branch. At the user's subsequent request, REPORT is now updated
with the completed local v7 evidence and the confirmed four-member HTHT team.
The prior REPORT remains available in commit 2ca8def and earlier history.
The report explicitly distinguishes its local v7 evidence from this merged
configuration; no new combined model-evaluation score is claimed.

The existing `citation_audit` tool, its declaration, four tests, group eval case,
run JSON files, transcripts and version-log entries are retained. The new
`deduplicate` tool, Streamlit UI, v0-v7 evidence and completed tests are added.
The combined tool registry has 12 tools, and the combined group dataset has
11 cases (6 single turn, 5 multi turn).

The merged configuration is labeled `v7-integration`. The 20/20 base and
10/10 group results from the original local v7 remain historical evidence
for its 11-tool declaration, not scores for the combined 12-tool version.
The combined version has been checked offline: **115 passed in 1.47s**;
see `starter_v0/analysis/pytest_git_integration.txt`. No new model/API eval
was run for the combined configuration.

The original 10-case group dataset is preserved as
`starter_v0/data/eval_group_v7.json`. To select the original local artifacts:

```text
python run_eval.py --provider openrouter --version v7-recheck --suite group --system-prompt artifacts/system_prompt_v7.md --tools artifacts/tools_v7.yaml --eval-cases data/eval_group_v7.json
```

To evaluate the combined configuration, run from `starter_v0` with a configured
provider and activated Python environment:

```text
python run_eval.py --provider openrouter --version v7-integration --suite base --eval-cases data/eval_base.json
python run_eval.py --provider openrouter --version v7-integration --suite group --eval-cases data/eval_group.json
```

The temporary demo URL in UI-README belongs to the original running local v7;
pushing this branch does not redeploy that local server with the merged source.
Use `python -m streamlit run app.py` in this checkout to run the merged UI.

No `.env`, API key, virtual environment, runtime state or cache is included.
The `.gitattributes` rules preserve prompt/tool snapshot bytes so their recorded
SHA256 hashes survive Git newline conversion.
