"""
reproduce_values.py — reproduce and assert every published mCytoMAP prior value.

Run:  python3 reproduce_values.py
Expected: a Tables-1A/1B + Figure-3C table, then "ALL PUBLISHED VALUES REPRODUCED".
"""
from mcytomap_ets import NODES, pi_norm, posterior, per_cell_ets

def r2(x):  # round to 2 dp as printed in the manuscript
    return round(x + 1e-9, 2)

pn = pi_norm()
print(f"{'Node':22} {'ETS':>4} {'Tier':10} {'pi_norm':>8} {'L':>5}")
print("-" * 54)
for n in NODES:
    L = n.likelihood
    print(f"{n.name:22} {n.ets:>4.1f} {n.tier:10} {r2(pn[n.name]):>8.2f} {L:>5.2f}")

# Tier sums
val_sum = sum(pn[n.name] for n in NODES if n.tier == "Validated")
cand_sum = sum(pn[n.name] for n in NODES if n.tier == "Candidate")
print("-" * 54)
print(f"Validated tier pi_norm sum = {r2(val_sum):.2f}   Candidate tier sum = {r2(cand_sum):.2f}")

# --- assertions against the published numbers (Tables 1A/1B, Figure 3C) -------
ETS_PUB = {"Pfn1": 2.5, "Rho GTPase network": 4.0, "Cdk1/MT remodeling": 2.0,
           "Arp2/3 complex": 1.5, "Piezo1": 1.0, "Actomyosin-podosome": 1.0}
PI_PUB = {"Pfn1": 0.29, "Rho GTPase network": 0.47, "Cdk1/MT remodeling": 0.24,
          "Arp2/3 complex": 0.09, "Piezo1": 0.06, "Actomyosin-podosome": 0.06}

for n in NODES:
    assert n.ets == ETS_PUB[n.name], f"ETS mismatch {n.name}: {n.ets} != {ETS_PUB[n.name]}"
    assert r2(pn[n.name]) == PI_PUB[n.name], f"pi_norm mismatch {n.name}: {r2(pn[n.name])} != {PI_PUB[n.name]}"
assert r2(val_sum) == 1.00, f"validated sum {r2(val_sum)} != 1.00"
assert r2(cand_sum) == 0.21, f"candidate sum {r2(cand_sum)} != 0.21"

# Per-cell ETS spot-checks vs Supplementary Table S1 (delta_sex=1 across all nodes)
piezo = next(n for n in NODES if n.name == "Piezo1")
assert per_cell_ets(piezo, sex_stratified_evidence=False, context_evidence=False) == 0.5   # aging
assert per_cell_ets(piezo, sex_stratified_evidence=False, context_evidence=True) == 0.5    # AD (1.0-0.5)
pfn1 = next(n for n in NODES if n.name == "Pfn1")
assert per_cell_ets(pfn1, sex_stratified_evidence=False, context_evidence=True) == 2.0     # aging
assert per_cell_ets(pfn1, sex_stratified_evidence=False, context_evidence=False) == 1.5    # AD
rho = next(n for n in NODES if n.name == "Rho GTPase network")
assert per_cell_ets(rho, sex_stratified_evidence=False, context_evidence=True) == 3.5

print("\nALL PUBLISHED VALUES REPRODUCED  ✓")
print("  Tables 1A/1B ETS, Figure 3C pi_norm, tier sums (1.00 / 0.21), and")
print("  Supplementary Table S1 per-cell ETS spot-checks all match.")
