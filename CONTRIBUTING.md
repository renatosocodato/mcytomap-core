# Auditing, running, and extending this package

This package is small by design and is meant to be read in full. This guide is for
reviewers and developers who want to audit the computation, run the checks, or build their
own analyses on top of the prior layer.

## Layout and reading order

1. `mcytomap_ets.py` — the entire computation: the `Node` dataclass, the `NODES` table of
   six checkpoints with their evidence flags, and the pure functions `pi_norm`,
   `posterior`, `per_cell_ets`. Start here; it is ~150 lines and has no I/O.
2. `reproduce_values.py` — recomputes and asserts every published value.
3. `tests/test_reproduce.py` — the assertion suite (see [docs/VALIDATION.md](docs/VALIDATION.md)).
4. `provenance.py` — emits the `outputs/` lineage.
5. `docs/` — the architecture, reproducibility, validation, and provenance documents.

## Running everything

```bash
python3 reproduce_values.py     # dependency-free reproduction
pip install ".[dev]" && pytest  # full test suite
make verify                     # reproduce + provenance + checksum audit
```

## Building on the prior layer

The public surface is intentionally minimal and stable:

```python
from mcytomap_ets import NODES, pi_norm, posterior, per_cell_ets

pn = pi_norm()                                  # {node: weight}
post = posterior()                              # {node: prior · placeholder-likelihood}
cell = per_cell_ets(NODES[0], sex_stratified_evidence=False, context_evidence=False)
```

To supply your own likelihood `L(node | data)` and compute a posterior, multiply your
per-node likelihood by `pi_norm()` — the prior layer is deliberately decoupled from any
particular likelihood so it can be reused for independent analyses.

## Conventions

- **Determinism is a hard requirement.** No randomness, network, clock, or data-file
  reads in the computation path. Any change that breaks this breaks reproducibility.
- **Assertions track the manuscript.** If a published value changes, update the value, the
  assertion, and `outputs/` together (run `make verify`), so the three never diverge.
- **Standard library only at runtime.** New runtime dependencies are out of scope; `pytest`
  is the only dev dependency.
- **Style.** Pure functions, dataclasses, explicit names; the code is meant to be obvious
  on first read rather than clever.

## Verifying a change

```bash
make verify        # must print the reproduction success line and report matching checksums
pytest -q          # must pass on Python ≥ 3.10
```
