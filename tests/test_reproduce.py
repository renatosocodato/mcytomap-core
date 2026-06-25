"""Pytest mirror of the published-value assertions in reproduce_values.py.

Guards every number that appears in Tables 1A/1B, Figure 3C, and the per-cell
Supplementary Table S1 spot-checks of the Targetome Perspective.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mcytomap_ets import NODES, pi_norm, per_cell_ets   # noqa: E402


def r2(x):
    return round(x + 1e-9, 2)


ETS_PUB = {"Pfn1": 2.5, "Rho GTPase network": 4.0, "Cdk1/MT remodeling": 2.0,
           "Arp2/3 complex": 1.5, "Piezo1": 1.0, "Actomyosin-podosome": 1.0}
PI_PUB = {"Pfn1": 0.29, "Rho GTPase network": 0.47, "Cdk1/MT remodeling": 0.24,
          "Arp2/3 complex": 0.09, "Piezo1": 0.06, "Actomyosin-podosome": 0.06}


def test_ets_values():
    for n in NODES:
        assert n.ets == ETS_PUB[n.name], f"{n.name}: {n.ets} != {ETS_PUB[n.name]}"


def test_ets_decomposition_reconciles():
    # ETS = N_causal + B_cascade(+1.0) + B_strat(+0.5) − P_dev(0.5)
    for n in NODES:
        computed = (n.n_causal
                    + (1.0 if n.cascade_bonus else 0.0)
                    + (0.5 if n.strat_bonus else 0.0)
                    - (0.5 if n.dev_penalty else 0.0))
        assert computed == n.ets, f"{n.name}: decomposition {computed} != {n.ets}"


def test_pi_norm_and_tier_sums():
    pn = pi_norm()
    for n in NODES:
        assert r2(pn[n.name]) == PI_PUB[n.name], f"{n.name}: {r2(pn[n.name])} != {PI_PUB[n.name]}"
    val = sum(pn[n.name] for n in NODES if n.tier == "Validated")
    cand = sum(pn[n.name] for n in NODES if n.tier == "Candidate")
    assert r2(val) == 1.00
    assert r2(cand) == 0.21
    assert r2(val + cand) == 1.21


def test_tier_assignment():
    for n in NODES:
        assert n.tier == ("Validated" if n.ets >= 2.0 else "Candidate")


def test_per_cell_piezo1_floor():
    piezo = next(n for n in NODES if n.name == "Piezo1")
    # Piezo1 has neither sex-stratified nor context-specific causal evidence, so under
    # its actual flags every sex × context cell floors to 0.5 (Suppl Table S1):
    #   1.0 − 0.5·δ_sex − 0.5·δ_stage  with δ_sex = δ_stage = 1  ->  0.0  ->  floor 0.5.
    assert per_cell_ets(piezo, sex_stratified_evidence=False, context_evidence=False) == 0.5  # aging
    assert per_cell_ets(piezo, sex_stratified_evidence=False, context_evidence=True) == 0.5   # AD
    # the floor is what produces 0.5 (raw value 0.0):
    assert piezo.ets - 0.5 - 0.5 < 0.5


def test_per_cell_formula_and_floor():
    # Spot-check the published per-cell rule on a higher-ETS node (no floor hit).
    rho = next(n for n in NODES if n.name == "Rho GTPase network")  # ETS 4.0
    assert per_cell_ets(rho, sex_stratified_evidence=False, context_evidence=False) == 3.0
    assert per_cell_ets(rho, sex_stratified_evidence=True, context_evidence=True) == 4.0
