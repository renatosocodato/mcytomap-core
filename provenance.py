"""provenance.py — emit (or verify) the reproduced mCytoMAP prior values under outputs/.

Deterministic by construction: no timestamps, no randomness, no network. Outputs are keyed
to the package version, so a fresh run on the same source is byte-identical.

Usage:
    python3 provenance.py            # (re)write outputs/ : json + csv + CHECKSUMS.sha256
    python3 provenance.py --check    # regenerate in memory and compare to committed outputs/
                                     #   exit 0 if identical, 1 on any mismatch
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import sys
from pathlib import Path

from mcytomap_ets import NODES, pi_norm, per_cell_ets

VERSION = "1.1.0"
OUT = Path(__file__).resolve().parent / "outputs"
COLS = ["quantity", "node", "tier", "value", "function", "source"]


def _r2(x: float) -> float:
    return round(x + 1e-9, 2)


def build_records() -> list[dict]:
    """Every reproduced value, each with its manuscript source and computing function."""
    pn = pi_norm()
    recs: list[dict] = []
    for n in NODES:
        recs.append({"quantity": "ETS", "node": n.name, "tier": n.tier, "value": n.ets,
                     "function": "mcytomap_ets.Node.ets", "source": "Tables 1A/1B"})
    for n in NODES:
        recs.append({"quantity": "pi_norm", "node": n.name, "tier": n.tier, "value": _r2(pn[n.name]),
                     "function": "mcytomap_ets.pi_norm", "source": "Figure 3C"})
    for tier in ("Validated", "Candidate"):
        recs.append({"quantity": "pi_norm_tier_sum", "node": tier, "tier": tier,
                     "value": _r2(sum(pn[n.name] for n in NODES if n.tier == tier)),
                     "function": "mcytomap_ets.pi_norm", "source": "Figure 3C"})
    # per-cell ETS under no sex-stratified evidence (delta_sex = 1): aging (delta_stage = 1) and AD (delta_stage = 0)
    for n in NODES:
        recs.append({"quantity": "per_cell_ETS_aging", "node": n.name, "tier": n.tier,
                     "value": per_cell_ets(n, sex_stratified_evidence=False, context_evidence=False),
                     "function": "mcytomap_ets.per_cell_ets", "source": "Supplementary Table S1"})
        recs.append({"quantity": "per_cell_ETS_AD", "node": n.name, "tier": n.tier,
                     "value": per_cell_ets(n, sex_stratified_evidence=False, context_evidence=True),
                     "function": "mcytomap_ets.per_cell_ets", "source": "Supplementary Table S1"})
    return recs


def render() -> dict[str, bytes]:
    """Return the canonical file contents (deterministic) without touching disk."""
    recs = build_records()
    payload = {
        "software": "mcytomap-core",
        "version": VERSION,
        "description": "Reproduced literature-derived prior values of mCytoMAP "
                       "(ETS, two-tier prior, per-cell ETS). See docs/PROVENANCE.md.",
        "records": recs,
    }
    js = (json.dumps(payload, indent=2, ensure_ascii=False) + "\n").encode()
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLS, lineterminator="\n")
    w.writeheader()
    for r in recs:
        w.writerow({k: r[k] for k in COLS})
    csvb = buf.getvalue().encode()
    checks = "\n".join(f"{hashlib.sha256(b).hexdigest()}  {name}"
                       for name, b in (("published_values.json", js),
                                       ("published_values.csv", csvb))) + "\n"
    return {"published_values.json": js, "published_values.csv": csvb,
            "CHECKSUMS.sha256": checks.encode()}


def write() -> None:
    OUT.mkdir(exist_ok=True)
    files = render()
    for name, content in files.items():
        (OUT / name).write_bytes(content)
    print(f"wrote {len(build_records())} records to outputs/ "
          f"(published_values.json, published_values.csv, CHECKSUMS.sha256)")


def check() -> int:
    files = render()
    problems = []
    for name, content in files.items():
        path = OUT / name
        if not path.exists():
            problems.append(f"missing committed output: {name}")
        elif path.read_bytes() != content:
            problems.append(f"committed output differs from a fresh run: {name}")
    if problems:
        print("PROVENANCE CHECK FAILED:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("provenance check OK — committed outputs/ match a fresh, deterministic run ✓")
    return 0


if __name__ == "__main__":
    if "--check" in sys.argv[1:]:
        raise SystemExit(check())
    write()
