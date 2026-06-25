# Validation and quality control

Every quantity the manuscript reports is guarded by an explicit assertion. Validation is
therefore not a separate report but an executable property of the package: if a value
drifts, reproduction fails loudly.

## 1. Two layers of guarding

| Layer | File | Role |
|---|---|---|
| Reproduction script | `reproduce_values.py` | recomputes and asserts every published value; the canonical one-command check |
| Test suite | `tests/test_reproduce.py` | the same assertions plus structural invariants, run in CI across Python 3.10–3.12 |

Both import the **same** `mcytomap_ets.py`, so they validate the identical code path the
manuscript values come from.

## 2. Assertion-to-published-value mapping

| Test | Asserts | Manuscript source |
|---|---|---|
| `test_ets_values` | ETS = 2.5 / 4.0 / 2.0 / 1.5 / 1.0 / 1.0 | Tables 1A / 1B |
| `test_ets_decomposition_reconciles` | `N_causal + B_cascade + B_strat − P_dev` equals each node's ETS | Section III rubric |
| `test_pi_norm_and_tier_sums` | `π_norm` = 0.29 / 0.47 / 0.24 and 0.09 / 0.06 / 0.06; tier sums 1.00 / 0.21; total 1.21 | Figure 3C |
| `test_tier_assignment` | Validated iff ETS ≥ 2.0 | Tables 1A / 1B |
| `test_per_cell_piezo1_floor` | Piezo1 per-cell ETS = 0.5 under its (no-evidence) flags; the floor is what produces 0.5 | Supplementary Table S1 |
| `test_per_cell_formula_and_floor` | the per-cell rule on a higher-ETS node (Rho: 3.0 and 4.0; no floor hit) | Supplementary Table S1 |

## 3. What the checks defend against

- **Silent numerical drift** — any change to a node's evidence flags or the rubric that
  would alter a published value triggers a hard failure.
- **Normalisation errors** — the tier-sum assertions (1.00 / 0.21, total 1.21) pin the
  two-tier prior's defining property.
- **Decomposition inconsistency** — `test_ets_decomposition_reconciles` ensures the
  per-node "bill of materials" (Tables / Supplementary) is internally consistent with the
  scores.
- **Floor / boundary mistakes** — the per-cell tests pin both the floor (0.5) and the
  unfloored arithmetic.

## 4. Continuous integration

`.github/workflows/ci.yml` runs on every push and pull request:

- a **reproduce** job on a Python 3.10 / 3.11 / 3.12 matrix that (i) executes
  `reproduce_values.py` with no dependencies, (ii) checks the console output byte-for-byte
  against the committed transcript, (iii) runs `provenance.py --check` (committed outputs
  match a fresh deterministic run), and (iv) installs the package and runs `pytest`
  (assertions **and** provenance-determinism tests);
- a **container** job that builds the `Dockerfile` and reproduces inside the pinned image.

A green badge therefore certifies that the published values reproduce on three interpreter
versions from a clean environment **and** in a pinned container, with the console output
and machine-readable outputs both matching their committed lineage.

## 5. Running validation locally

```bash
# dependency-free check
python3 reproduce_values.py

# full suite
pip install ".[dev]"   # or: pip install -r requirements-dev.txt
pytest -q

# end-to-end audit (reproduce + provenance + checksum match)
make verify
```
