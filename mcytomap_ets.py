"""
mcytomap_ets.py — Evidence-Tier Score (ETS) rubric and two-tier Bayesian-style
prior pi_norm(node) for the mCytoMAP cytoskeletal-checkpoint framework.

This module is the reference implementation of the *literature-derived prior*
layer of mCytoMAP (Section III preamble + Box 4, row 6 of the manuscript
"From Molecular Markers to Architectural Control: Cytoskeletal Checkpoints as
the Decisive State-Access Layer of the Aging Microglial Targetome").

It is fully self-contained, requires no new data, and reproduces every
published per-node value in Tables 1A/1B and Figure 3C. Run reproduce_values.py
to print the table and assert the published numbers.

ETS rubric (per node):
    ETS = N_causal + B_cascade + B_strat - P_dev
      N_causal  : number of causal microglia-specific perturbation studies
      B_cascade : +1.0 if >=3 mechanistic layers documented downstream
      B_strat   : +0.5 if >=1 causal study reports sex- or stage-stratified readouts
      P_dev     : -0.5 if causal evidence rests on a constitutive Cx3cr1-Cre driver
    Tier: Validated if ETS >= 2.0, else Candidate.

Two-tier normalisation of the prior pi_norm(node):
    Validated tier : pi_norm = ETS / sum(ETS over validated nodes)   (sums to 1.0)
    Candidate tier : pi_norm = ETS / (2 * sum(ETS over validated nodes))

Posterior priority:
    P_posterior(node) ∝ pi_norm(node) * L(node | data)
where L(node | data) is the equal-weighted mean of the four Box-1 axis scores
mapped onto {HIGH:1.00, MOD-HIGH:0.75, MOD:0.50, LOW-MOD:0.25, LOW:0.00}.

Per-cell, sex/context-conditional ETS (Supplementary Table S1):
    ETS(node | sex, context) = ETS_base - 0.5*delta_sex - 0.5*delta_stage   (floor 0.5)
"""
from __future__ import annotations
from dataclasses import dataclass, field

VALIDATED_THRESHOLD = 2.0

# Qualitative Box-1 axis bands -> numeric L contribution
BAND = {"HIGH": 1.00, "MOD-HIGH": 0.75, "MOD": 0.50, "LOW-MOD": 0.25, "LOW": 0.00}


@dataclass(frozen=True)
class Node:
    name: str
    n_causal: int            # causal microglia-specific perturbation studies
    cascade_bonus: bool      # >=3 downstream mechanistic layers documented
    strat_bonus: bool        # >=1 causal study with sex-/stage-stratified readout
    dev_penalty: bool        # causal evidence rests on constitutive Cx3cr1-Cre
    box1_axes: tuple = field(default=())  # (reversibility, dissipation, specificity, circuit)

    @property
    def ets(self) -> float:
        return (self.n_causal
                + (1.0 if self.cascade_bonus else 0.0)
                + (0.5 if self.strat_bonus else 0.0)
                - (0.5 if self.dev_penalty else 0.0))

    @property
    def tier(self) -> str:
        return "Validated" if self.ets >= VALIDATED_THRESHOLD else "Candidate"

    @property
    def likelihood(self) -> float | None:
        """L(node|data) = equal-weighted mean of the four Box-1 axis bands."""
        if not self.box1_axes:
            return None
        return sum(BAND[a] for a in self.box1_axes) / len(self.box1_axes)


# --- The six checkpoints, scored exactly as in the manuscript -----------------
NODES = [
    Node("Pfn1",                 n_causal=1, cascade_bonus=True,  strat_bonus=True,  dev_penalty=False,
         box1_axes=("MOD", "HIGH", "MOD", "HIGH")),
    Node("Rho GTPase network",   n_causal=3, cascade_bonus=True,  strat_bonus=False, dev_penalty=False,
         box1_axes=("HIGH", "HIGH", "MOD", "HIGH")),
    Node("Cdk1/MT remodeling",   n_causal=2, cascade_bonus=False, strat_bonus=False, dev_penalty=False,
         box1_axes=("MOD", "MOD-HIGH", "MOD-HIGH", "MOD")),
    Node("Arp2/3 complex",       n_causal=1, cascade_bonus=True,  strat_bonus=False, dev_penalty=True,
         box1_axes=("HIGH", "HIGH", "MOD-HIGH", "HIGH")),
    Node("Piezo1",               n_causal=1, cascade_bonus=False, strat_bonus=False, dev_penalty=False,
         box1_axes=("MOD", "MOD", "HIGH", "MOD-HIGH")),
    Node("Actomyosin-podosome",  n_causal=1, cascade_bonus=False, strat_bonus=False, dev_penalty=False,
         box1_axes=("HIGH", "MOD", "HIGH", "MOD-HIGH")),
]


def pi_norm(nodes=NODES) -> dict[str, float]:
    """Two-tier normalised prior weight pi_norm(node)."""
    sigma_validated = sum(n.ets for n in nodes if n.tier == "Validated")
    out = {}
    for n in nodes:
        if n.tier == "Validated":
            out[n.name] = n.ets / sigma_validated
        else:
            out[n.name] = n.ets / (2.0 * sigma_validated)
    return out


def posterior(nodes=NODES) -> dict[str, float]:
    """Unnormalised posterior priority P ∝ pi_norm * L(node|data)."""
    pn = pi_norm(nodes)
    return {n.name: pn[n.name] * n.likelihood for n in nodes if n.likelihood is not None}


def per_cell_ets(node: Node, sex_stratified_evidence: bool, context_evidence: bool,
                 floor: float = 0.5) -> float:
    """ETS(node | sex, context) = ETS_base - 0.5*delta_sex - 0.5*delta_stage (floored)."""
    delta_sex = 0 if sex_stratified_evidence else 1
    delta_stage = 0 if context_evidence else 1
    return max(floor, node.ets - 0.5 * delta_sex - 0.5 * delta_stage)
