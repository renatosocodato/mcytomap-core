# mCytoMAP-core

**Reference implementation of the Evidence-Tier Score (ETS) rubric and the two-tier
Bayesian-style prior π_norm(node)** for the cytoskeletal-checkpoint prioritisation
framework *mCytoMAP*, from the Perspective:

> *From Molecular Markers to Architectural Control: Cytoskeletal Checkpoints as the
> Decisive State-Access Layer of the Aging Microglial Targetome* (Target-S2026-0032,
> *Targetome*).

This is the component of mCytoMAP that **requires no new experimental data** — it is
populated entirely from the published causal-perturbation literature and is
re-computable at every revision. Running it reproduces **every per-node value** in
Tables 1A/1B and Figure 3C of the paper, and the per-cell values in Supplementary
Table S1.

[![CI](https://github.com/renatosocodato/mcytomap-core/actions/workflows/ci.yml/badge.svg)](https://github.com/renatosocodato/mcytomap-core/actions)
[![DOI](https://zenodo.org/badge/DOI/PLACEHOLDER.svg)](https://doi.org/PLACEHOLDER)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> Replace `ORG` and the DOI badge after the GitHub push and Zenodo deposit (see
> **Release & archiving** below).

## Contents

| File | Purpose |
|---|---|
| `mcytomap_ets.py` | ETS rubric, two-tier `pi_norm(node)`, posterior priority, and per-cell `ETS(node \| sex, context)` |
| `reproduce_values.py` | Prints the Tables 1A/1B + Figure 3C table and **asserts** the published numbers |
| `tests/test_reproduce.py` | Pytest mirror of the published-value assertions |
| `LICENSE` | MIT |

## Run

No dependencies beyond the Python ≥ 3.10 standard library.

```bash
python3 reproduce_values.py
# expected to end with: ALL PUBLISHED VALUES REPRODUCED  ✓
```

Or install and test:

```bash
pip install .
pytest -q          # requires pytest (dev only)
```

## What it reproduces

- **ETS** per node: Pfn1 2.5, Rho GTPase 4.0, Cdk1/MT 2.0 (Validated); Arp2/3 1.5,
  Piezo1 1.0, actomyosin–podosome 1.0 (Candidate).
- **Two-tier prior** `pi_norm` (within-tier normalisation, applied up to
  proportionality): 0.29 / 0.47 / 0.24 (Validated, sum = 1.00) and 0.09 / 0.06 / 0.06
  (Candidate, sum = 0.21); six weights total 1.21 by construction.
- **Per-cell** `ETS(node | sex, context)` (Suppl. Table S1), e.g. Piezo1 = 0.5 across
  all sex × context cells; Rho GTPase = 3.5; Pfn1 = 2.0 (aging) / 1.5 (AD).

ETS rubric: `ETS = N_causal + B_cascade + B_strat − P_dev`, where `B_cascade = +1.0`
if three or more downstream mechanistic layers are documented, `B_strat = +0.5` if a
sex-/stage-stratified causal readout exists, and `P_dev = 0.5` is subtracted for a
constitutive Cx3cr1-Cre driver. Validated if `ETS ≥ 2.0`.

## Scope

The data-dependent layers of mCytoMAP — the CytoState token, cyto-state gap,
susceptibility index, module drift, and conditional entropy — are **not** included
here: they require the snRNA-seq atlas training described in Box 5 and are the subject
of the Minimum Viable Product (MVP) validation study. A full research framework that
extends this core with those layers and a reduced-order biophysical forward model is
developed separately (**mCytoMAP-mvp**). This repository deliberately covers only the
literature-derived prior, which is the single component fully specified and
reproducible today.

## Release & archiving (to mint the citable DOI)

1. **Public repo:** create `github.com/renatosocodato/mcytomap-core` and push this directory.
2. **Version tag:** `git tag -a v1.0.0 -m "mCytoMAP-core v1.0.0" && git push --tags`.
3. **Citable DOI:** enable the GitHub↔Zenodo integration for the repo, then publish
   the `v1.0.0` release on GitHub — Zenodo archives the exact snapshot and mints a DOI.
   (`figshare`/`OSF` are alternatives.) Metadata is pre-filled in `.zenodo.json`.
4. **Bind into the paper:** replace the *Data and Code Availability* placeholder
   *"…with a citable DOI and a version/commit tag assigned at acceptance"* with the
   concrete triplet, e.g.
   *"…at https://github.com/renatosocodato/mcytomap-core (release v1.0.0, commit `<hash>`),
   archived at https://doi.org/10.5281/zenodo.&lt;NNNNN&gt;."*

> Note: this is a brand-new archive of the literature-derived rubric only; its DOI is
> independent of any other deposit and must not be cross-referenced with unrelated
> archives.

## How to cite

See `CITATION.cff` (GitHub renders a "Cite this repository" button). Please cite both
the software (this DOI) and the *Targetome* Perspective.
