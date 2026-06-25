# Reproducibility

This package is engineered so that reproducing the published values is a single,
deterministic command with an unambiguous pass/fail result.

## 1. Minimal reproduction (no install)

```bash
python3 reproduce_values.py
```

Requires only a Python ≥ 3.10 interpreter — no installation, no third-party packages, no
data download. The script prints the per-node table and terminates with:

```
ALL PUBLISHED VALUES REPRODUCED  ✓
  Tables 1A/1B ETS, Figure 3C pi_norm, tier sums (1.00 / 0.21), and
  Supplementary Table S1 per-cell ETS spot-checks all match.
```

**Exit-code semantics** (suitable for CI / automated checking):

| Exit code | Meaning |
|---|---|
| `0` | every published value reproduced and asserted |
| non-zero | an `AssertionError` — a value did not match the manuscript (the failing assertion names the node and the expected/actual values) |

## 2. One-command workflows (`make`)

| Command | Action |
|---|---|
| `make reproduce` | run `reproduce_values.py` |
| `make test` | run the assertion + provenance test suite (`pytest`) |
| `make provenance` | regenerate `outputs/` (machine-readable values + checksums) |
| `make diff-output` | confirm the live console output matches the committed transcript byte-for-byte |
| `make verify` | `reproduce` → `diff-output` → `provenance --check` (full audit) |
| `make docker-reproduce` | build the pinned container and reproduce inside it |
| `make clean` | remove caches and regenerated artifacts |

`make verify` is the recommended end-to-end audit: it re-derives the values, confirms the
console output is byte-identical to the committed transcript
(`outputs/expected_console_output.txt`), and confirms the machine-readable outputs match
the committed lineage.

## 2b. Containerised reproduction (environment-independent)

A `Dockerfile` pins the interpreter so the reproduction is independent of the host:

```bash
docker build -t mcytomap-core .
docker run --rm mcytomap-core                          # reproduce + assert every value
docker run --rm mcytomap-core python3 provenance.py --check   # audit committed outputs
```

The base image (`python:3.12-slim`) is pinned for definiteness; because the computation is
deterministic and uses only the standard library, any Python ≥ 3.10 produces identical
results. The container is built and run in CI on every change, so the pinned-environment
reproduction is continuously verified.

## 3. Execution environment

| | |
|---|---|
| Python | ≥ 3.10 (tested on 3.10, 3.11, 3.12 in CI) |
| Runtime dependencies | none (standard library only) |
| Test dependencies | `pytest` — `pip install ".[dev]"` or `pip install -r requirements-dev.txt` |
| OS | platform-independent |

A conda specification (`environment.yml`) and a pinned `requirements-dev.txt` are provided
for exact recreation of the developer/test environment. They are **not** required to run
`reproduce_values.py`, which depends on nothing beyond the interpreter.

To record the interpreter actually used:

```bash
python3 --version          # interpreter version
python3 -VV                # build details
```

## 4. Determinism guarantees

The computation path contains:

- **no randomness** — no use of `random`, `numpy.random`, hashing of unordered structures,
  or any stochastic step;
- **no clock dependence** — outputs do not embed timestamps; provenance artifacts are keyed
  to the software version, not the run time;
- **no network access**;
- **no external data files** — the six-node evidence table is encoded in source.

Consequently the printed table, the assertions, and the emitted `outputs/` are identical
on every machine and every run. This is what makes `make verify` a meaningful regression
gate.

## 5. Provenance of generated outputs

`make provenance` writes, to `outputs/`:

- `published_values.json` — every reproduced value with its manuscript source (table /
  figure) and the function that computed it;
- `published_values.csv` — the same, flat;
- `CHECKSUMS.sha256` — SHA-256 of the two files above.

These are committed to the repository as the canonical lineage, so the published numbers
can be audited by inspection or `diff` without executing code. See
[PROVENANCE.md](PROVENANCE.md).

## 6. Reproducing from the archived snapshot

The Zenodo deposition archives the exact tagged source. To reproduce from the archive
rather than the live repository, download the archived `.zip`, unpack it, and run
`python3 reproduce_values.py` inside — the result is identical to the live repository at
the corresponding tag.
