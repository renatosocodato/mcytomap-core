# Provenance and lineage of generated outputs

The package treats its numerical outputs as a tracked, auditable artifact rather than as
transient console text. `make provenance` (equivalently `python3 provenance.py`)
regenerates the canonical outputs under `outputs/`, and they are committed to the
repository so the published values can be audited by inspection or `diff`.

## 1. Generated artifacts

| File | Content |
|---|---|
| `outputs/published_values.json` | every reproduced value, with per-value provenance: the manuscript source (table / figure), the computing function, and the quantity |
| `outputs/published_values.csv` | the same table in flat form |
| `outputs/CHECKSUMS.sha256` | SHA-256 digests of the two files above |

## 2. Provenance model

Each emitted value carries the chain:

```
node + evidence flags (mcytomap_ets.NODES)
   → function (mcytomap_ets.ets / pi_norm / per_cell_ets)
      → value
         → manuscript location (Table 1A/1B, Figure 3C, Supplementary Table S1)
```

`published_values.json` records this chain explicitly per entry, so any number in the
manuscript can be traced back to the exact source flags and the line of code that
produced it.

## 3. Why the outputs are committed

- **Audit without execution.** A reviewer can read `outputs/published_values.json` and
  confirm it matches the manuscript without running anything.
- **Regression anchor.** `make verify` regenerates the outputs and checks them against the
  committed `CHECKSUMS.sha256`; a mismatch means the code no longer produces the archived
  values — a hard, reviewable signal.
- **Determinism made visible.** Because the computation has no randomness or clock
  dependence (see [REPRODUCIBILITY.md](REPRODUCIBILITY.md)), a fresh `make provenance`
  yields byte-identical files on any machine; the committed checksums are therefore a
  stable lineage, not a per-run snapshot.

## 4. Regenerating

```bash
make provenance     # writes outputs/ and recomputes checksums
make verify         # regenerate and confirm checksums match the committed lineage
```

The artifacts are keyed to the software version (`CHANGELOG.md` / `pyproject.toml`), not to
wall-clock time, so re-running on the same source version reproduces them exactly.
