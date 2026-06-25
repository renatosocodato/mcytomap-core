"""Tests for the provenance emitter: determinism and committed-output consistency."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import provenance  # noqa: E402


def test_render_is_deterministic():
    assert provenance.render() == provenance.render()  # byte-identical across calls


def test_committed_outputs_match_fresh_run():
    assert provenance.check() == 0  # committed outputs/ equal a fresh render


def test_records_cover_expected_quantities():
    recs = provenance.build_records()
    quantities = {r["quantity"] for r in recs}
    assert {"ETS", "pi_norm", "pi_norm_tier_sum",
            "per_cell_ETS_aging", "per_cell_ETS_AD"} <= quantities
    assert sum(1 for r in recs if r["quantity"] == "ETS") == 6
    assert all({"node", "value", "function", "source"} <= set(r) for r in recs)
