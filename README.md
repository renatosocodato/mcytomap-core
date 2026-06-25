# mCytoMAP-core

**Reference implementation of the Evidence-Tier prior layer of mCytoMAP** — the
cytoskeletal-checkpoint prioritisation framework of the *Targetome* Perspective:

> *From Molecular Markers to Architectural Control: Cytoskeletal Checkpoints as the
> Decisive State-Access Layer of the Aging Microglial Targetome* (Target-S2026-0032).

[![CI](https://github.com/renatosocodato/mcytomap-core/actions/workflows/ci.yml/badge.svg)](https://github.com/renatosocodato/mcytomap-core/actions)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20848905.svg)](https://doi.org/10.5281/zenodo.20848905)
[![Python ≥3.10](https://img.shields.io/badge/python-%E2%89%A53.10-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Dependencies: stdlib only](https://img.shields.io/badge/runtime%20deps-none%20(stdlib)-success.svg)](#environment-and-dependencies)

This archive computes the layer of mCytoMAP that is **fully determined by the published
causal-perturbation literature and requires no new experimental data**. One command
regenerates — and *asserts* — every per-node value the manuscript reports, so a reviewer
can audit the framework's quantitative core end-to-end in under a minute.

---

## Contents

- [What this reproduces](#what-this-reproduces)
- [Quickstart](#quickstart)
- [Computational architecture](#computational-architecture)
- [Reproducibility workflow](#reproducibility-workflow)
- [Generated outputs and provenance](#generated-outputs-and-provenance)
- [Validation and quality control](#validation-and-quality-control)
- [Environment and dependencies](#environment-and-dependencies)
- [Repository layout](#repository-layout)
- [Documentation](#documentation)
- [Scope](#scope)
- [How to cite](#how-to-cite)
- [License](#license)

---

## What this reproduces

Running the package regenerates and verifies, against the values printed in the
manuscript:

| Output | Manuscript location | Guarded by |
|---|---|---|
| Per-node Evidence-Tier Score (ETS) | Tables 1A / 1B | `reproduce_values.py`, `tests/` |
| Two-tier prior `π_norm(node)` | Figure 3C | `reproduce_values.py`, `tests/` |
| Validated / Candidate tier sums (1.00 / 0.21) | Figure 3C | `reproduce_values.py`, `tests/` |
| Per-cell `ETS(node | sex, context)` | Supplementary Table S1 | `reproduce_values.py`, `tests/` |

Concretely: ETS = **2.5 / 4.0 / 2.0** (Validated: Pfn1, Rho GTPase, Cdk1/MT) and
**1.5 / 1.0 / 1.0** (Candidate: Arp2/3, Piezo1, actomyosin–podosome); `π_norm` =
**0.29 / 0.47 / 0.24** (sum 1.00) and **0.09 / 0.06 / 0.06** (sum 0.21); the six weights
total 1.21 by construction (the two tiers are normalised separately — see
[ARCHITECTURE](docs/ARCHITECTURE.md)).

## Quickstart

```bash
git clone https://github.com/renatosocodato/mcytomap-core
cd mcytomap-core

python3 reproduce_values.py          # no install, no dependencies
# … prints the ETS / pi_norm table and exits with:
#    ALL PUBLISHED VALUES REPRODUCED  ✓        (exit code 0; non-zero on any mismatch)
```

One-command equivalents are provided via `make` (see [Reproducibility
workflow](#reproducibility-workflow)):

```bash
make reproduce      # run reproduce_values.py
make test           # run the assertion test-suite (needs pytest)
make provenance     # regenerate outputs/ (machine-readable values + checksums)
make verify         # reproduce + provenance + checksum check, in one step
```

## Computational architecture

mCytoMAP ranks cytoskeletal checkpoints by combining a literature-derived **prior** with
a data-driven likelihood. **This archive implements the prior layer**, which is fully
specified from published evidence:

```
 published causal-perturbation evidence per node
        │
        ▼
 ┌──────────────────────────┐   ETS = N_causal + B_cascade + B_strat − P_dev
 │  Evidence-Tier Score      │   (Validated if ETS ≥ 2.0, else Candidate)
 └──────────────────────────┘
        │
        ▼
 ┌──────────────────────────┐   Validated tier: π_norm = ETS / Σ_validated ETS   (Σ = 1.00)
 │  two-tier prior π_norm    │   Candidate tier: π_norm = ETS / (2 · Σ_validated) (Σ = 0.21)
 └──────────────────────────┘
        │
        ├─▶ posterior priority   P(node) ∝ π_norm(node) · L(node | data)
        └─▶ per-cell             ETS(node | sex, context) = ETS_base − 0.5·δ_sex − 0.5·δ_stage  (floor 0.5)
```

The full derivation, the meaning and justification of every rubric term, and the data
structures are documented in **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**.

## Reproducibility workflow

The reproduction is **deterministic and self-contained**: no randomness, no network
access, no external data files, no third-party runtime dependencies. The exact step-by-
step workflow, expected console output, exit-code semantics, and the execution
environment are documented in **[docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md)**.

## Generated outputs and provenance

`make provenance` (or `python3 provenance.py`) writes the reproduced values to
`outputs/` as machine-readable artifacts with SHA-256 checksums, each row annotated with
its manuscript source and the function that computes it:

```
outputs/published_values.json     # values + per-value provenance (source table/figure, function)
outputs/published_values.csv      # the same table, flat
outputs/CHECKSUMS.sha256          # checksums of the above (audit / regression anchor)
```

These artifacts are committed so a reviewer can diff a fresh run against the canonical
lineage without executing anything. The provenance model is documented in
**[docs/PROVENANCE.md](docs/PROVENANCE.md)**.

## Validation and quality control

Every published number is guarded by an assertion, both in `reproduce_values.py` and in
the `tests/` suite, which runs in CI across Python 3.10–3.12. The assertion-to-value
mapping and the QC philosophy are documented in **[docs/VALIDATION.md](docs/VALIDATION.md)**.

```bash
pip install ".[dev]" && pytest -q
```

## Environment and dependencies

| | |
|---|---|
| Language | Python ≥ 3.10 |
| Runtime dependencies | **none** (standard library only) |
| Dev/test dependencies | `pytest` (see `requirements-dev.txt`) |
| Operating system | platform-independent (no OS-specific calls) |
| Determinism | no RNG, no clock-dependent output, no network, no data files |

A pinned developer environment is provided in `requirements-dev.txt` and
`environment.yml` for exact recreation; the runtime itself needs nothing beyond a
standard Python interpreter.

## Repository layout

```
mcytomap-core/
├── mcytomap_ets.py          # the ETS rubric, two-tier prior, posterior, per-cell ETS
├── reproduce_values.py      # entry point: prints + asserts every published value
├── provenance.py            # emits outputs/ (values + checksums) for auditing
├── outputs/                 # committed, regenerable canonical outputs + checksums
├── tests/                   # assertion suite mirroring the published values
├── docs/                    # ARCHITECTURE · REPRODUCIBILITY · VALIDATION · PROVENANCE
├── Makefile                 # reproduce | test | provenance | verify
├── pyproject.toml           # packaging (stdlib-only runtime)
├── CITATION.cff             # machine-readable citation
└── CHANGELOG.md
```

## Documentation

| Document | Purpose |
|---|---|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Design, rubric terms, assumptions, data structures |
| [docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md) | Workflow, expected output, environment, determinism |
| [docs/VALIDATION.md](docs/VALIDATION.md) | Testing, QC, assertion-to-value mapping |
| [docs/PROVENANCE.md](docs/PROVENANCE.md) | Lineage of generated outputs |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to audit, run, and verify the package |

## Scope

This repository implements the **literature-derived prior layer** of mCytoMAP — the
single component that is fully specified and reproducible from published data alone. The
data-dependent components of the framework (the CytoState token, cyto-state gap,
susceptibility index, module drift, and conditional entropy) require experimental data
described in the manuscript and are **outside the scope of this archive**; this package
therefore covers exactly, and only, the prior layer whose values appear in Tables 1A/1B,
Figure 3C, and Supplementary Table S1.

## How to cite

See [`CITATION.cff`](CITATION.cff) (GitHub renders a "Cite this repository" button).
Please cite both this software (via its DOI) and the *Targetome* Perspective.

## License

MIT — see [`LICENSE`](LICENSE).
