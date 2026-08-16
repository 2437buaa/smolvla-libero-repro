# Public Release Checklist

- [x] No model weights, datasets, raw videos, logs, tokens, or private keys.
- [x] Original scripts and documentation use Apache-2.0.
- [x] Third-party components are linked and not redistributed.
- [x] Exact LeRobot commit and verified environment are documented.
- [x] Negative and statistically non-significant results are retained.
- [x] Figures are generated from tracked CSV files.
- [ ] Choose the public author name to add to a future `CITATION.cff`.
- [ ] Optionally upload the adapter to Hugging Face using `MODEL_CARD.md`.
- [ ] Add one representative success/failure GIF only after checking its size.
- [ ] Change GitHub visibility from Private to Public.
- [ ] Create a `v1.0.0` GitHub release after the public README is verified.

Before changing visibility, run:

```bash
git status --short
python scripts/make_figures.py
git diff --check
git grep -n -i -E 'token|password|secret|api[_-]?key|/home/' -- ':!docs/release_checklist.md'
```
