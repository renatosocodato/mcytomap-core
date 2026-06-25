# Changelog

All notable changes to **mCytoMAP-core** are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/); versioning: [SemVer](https://semver.org/).

## [1.1.0] — 2026-06-25

Documentation, reproducibility-tooling, and provenance release. **No change to the
computation or to any reproduced value** — `mcytomap_ets.py` and the reproduced numbers
are identical to 1.0.0.

### Added
- `docs/` — `ARCHITECTURE.md`, `REPRODUCIBILITY.md`, `VALIDATION.md`, `PROVENANCE.md`.
- `provenance.py` — emits `outputs/` (machine-readable values + per-value provenance +
  SHA-256 checksums) and a `--check` mode that confirms the committed lineage matches a
  fresh deterministic run.
- `outputs/` — committed canonical values (`published_values.json` / `.csv`) and
  `CHECKSUMS.sha256`, auditable without executing code.
- `Makefile` (`reproduce` / `test` / `provenance` / `verify`), `CONTRIBUTING.md`,
  `requirements.txt`, `requirements-dev.txt`, `environment.yml`.
- Expanded test suite (decomposition reconciliation; per-cell formula and floor).

### Changed
- README rewritten as a navigable, reviewer-oriented document with explicit reproducibility,
  architecture, provenance, validation, and environment sections.

## [1.0.0] — 2026-06-25

First public release: the literature-derived prior layer of mCytoMAP, as published in the
*Targetome* Perspective Target-S2026-0032.

### Included
- `mcytomap_ets.py` — Evidence-Tier Score rubric, two-tier `pi_norm(node)` prior,
  posterior priority, and per-cell `ETS(node | sex, context)`.
- `reproduce_values.py` — regenerates and asserts every published per-node value
  (Tables 1A/1B, Figure 3C) and the per-cell Supplementary Table S1 spot-checks.
- `tests/`, packaging (standard-library-only runtime), CI, `CITATION.cff`, `.zenodo.json`.
