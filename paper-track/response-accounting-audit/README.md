# ARC-AGI-3 token-accounting audit: public subset

Read `PAPER.md`, the shorter `WRITEUP.md`, and `METHODS.md`. Released November 9, 2026. See LICENSE.md for MIT-0 original-code and CC-BY 4.0 paper licensing, with upstream terms preserved.

Run `python analyze.py` and `python analyze_public_scalars.py` to recompute aggregate results and the response-token partition using only the bundled scalars. `python render_figures.py` recreates figures with the pinned plotting dependencies. `probe_terminal_cap.py`, `check_terminal_repair.py` and the boundary tests use synthetic CPU cases.

Original `analyze_responses.py` and `replay_saved_caps.py` require privately retained payloads and are not runnable against this public subset alone. Saved model Python was excluded because it contains board-specific constants. Raw logs, boards, competition datasets, weights and account files are not bundled. Population/game identifiers and scalar scores/counters are retained.

The 42 frozen runtime files are unchanged. `EVIDENCE_MANIFEST.json` identifies this public subset and the prior private-package fingerprint; `MANIFEST.json` identifies all staged files. This release adds no new Kaggle execution or score.
