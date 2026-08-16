# Public Release Checklist

- [x] No model weights, datasets, raw videos, logs, tokens, or private keys.
- [x] Original scripts and documentation use Apache-2.0.
- [x] Third-party components are linked and not redistributed.
- [x] Exact LeRobot commit and verified environment are documented.
- [x] Fresh Ubuntu setup, asset/model/data download, and smoke-test helpers are included.
- [x] LIBERO assets and training dataset revisions used by the helpers are fixed.
- [x] First-run scripts allow downloads; offline mode remains an explicit option.
- [x] Negative and statistically non-significant results are retained.
- [x] Figures are generated from tracked CSV files.
- [ ] Choose the public author name to add to a future `CITATION.cff`.
- [x] Adapter published to `marlon777777/smolvla-libero-task3-lora-r4`.
- [ ] Add one representative success/failure GIF only after checking its size.
- [x] GitHub visibility changed from Private to Public.
- [x] `v1.0.0` GitHub release created after the public README was verified.

Before changing visibility, run:

```bash
git status --short
python scripts/make_figures.py
find scripts -type f -name '*.sh' -exec bash -n {} \;
python -m py_compile scripts/*.py
git diff --check
git grep -n -E '(hf_[A-Za-z0-9]{10,}|BEGIN [A-Z ]*PRIVATE KEY|/home/[A-Za-z0-9._-]+|github-proxy)' \
  -- ':!docs/release_checklist.md' || echo "privacy_scan: OK"
```
