# Changelog

All notable changes to **mCytoMAP-core** are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/); this project uses
[Semantic Versioning](https://semver.org/).

## [1.0.0] — 2026-06-25

First public release: the literature-derived layer of mCytoMAP, as published in the
*Targetome* Perspective Target-S2026-0032.

### Included
- `mcytomap_ets.py` — Evidence-Tier Score (ETS) rubric
  (`ETS = N_causal + B_cascade + B_strat − P_dev`), two-tier `pi_norm(node)` prior,
  posterior priority, and per-cell `ETS(node | sex, context)`.
- `reproduce_values.py` — regenerates and **asserts** every published per-node value
  (Tables 1A/1B, Figure 3C) and the per-cell Supplementary Table S1 spot-checks.
- `tests/test_reproduce.py` — pytest mirror of the assertions, including the
  ETS-decomposition reconciliation and the 1.21 tier-sum check.
- Packaging (`pyproject.toml`, standard-library only), CI, `CITATION.cff`, `.zenodo.json`.

### Notes
- No dependencies beyond the Python ≥ 3.10 standard library.
- Reproduces: ETS 2.5 / 4.0 / 2.0 (Validated) and 1.5 / 1.0 / 1.0 (Candidate);
  `pi_norm` 0.29 / 0.47 / 0.24 (sum 1.00) and 0.09 / 0.06 / 0.06 (sum 0.21).
