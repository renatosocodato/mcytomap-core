# Architecture — the Evidence-Tier prior layer

This document specifies the design of the layer implemented in this archive: the
**literature-derived prior** of mCytoMAP. It covers the rubric, the two-tier
normalisation, the posterior coupling, the per-cell rule, the data structures, and the
assumptions behind each — everything needed to audit or re-derive the published values
by hand.

## 1. Position in mCytoMAP

mCytoMAP scores each cytoskeletal-checkpoint node by combining a prior with a data-driven
likelihood:

```
P_posterior(node) ∝ π_norm(node) · L(node | data)
                    └── prior ──┘   └─ data-driven ─┘
                    (this archive)   (not in this archive)
```

The prior `π_norm(node)` is fixed by published causal-perturbation evidence and is the
component reproduced here. The likelihood `L(node | data)` is data-dependent and outside
this archive's scope (see the manuscript). This separation is deliberate: the prior is
auditable today, independently of any new data.

## 2. Evidence-Tier Score (ETS)

For each node, the ETS is an additive, transparent rubric:

```
ETS = N_causal + B_cascade + B_strat − P_dev
```

| Term | Value | Awarded when | Source of the judgement |
|---|---|---|---|
| `N_causal` | integer ≥ 0 | one count per microglia-specific **causal perturbation** study | published studies cited in the manuscript |
| `B_cascade` | +1.0 | **three or more** downstream mechanistic layers are documented for a perturbation | manuscript cascade descriptions |
| `B_strat` | +0.5 | at least one causal study reports **sex- or stage-stratified** readouts | manuscript |
| `P_dev` | −0.5 | causal evidence rests on a **constitutive Cx3cr1-Cre** driver (developmental/adult confound) | manuscript |

A node is **Validated** if `ETS ≥ 2.0`, otherwise **Candidate**. The per-node inputs are
encoded as booleans/counts in `mcytomap_ets.py` (`NODES`), so the score is a pure
function of explicit, inspectable evidence flags — there are no free or fitted parameters.

### Per-node bill of materials (reproduced by the code)

| Node | `N_causal` | `B_cascade` | `B_strat` | `P_dev` | ETS | Tier |
|---|---|---|---|---|---|---|
| Pfn1 | 1 | +1.0 | +0.5 | 0 | **2.5** | Validated |
| Rho GTPase network | 3 | +1.0 | 0 | 0 | **4.0** | Validated |
| Cdk1/MT remodeling | 2 | 0 | 0 | 0 | **2.0** | Validated |
| Arp2/3 complex | 1 | +1.0 | 0 | −0.5 | **1.5** | Candidate |
| Piezo1 | 1 | 0 | 0 | 0 | **1.0** | Candidate |
| Actomyosin–podosome | 1 | 0 | 0 | 0 | **1.0** | Candidate |

## 3. Two-tier prior `π_norm`

The prior is normalised **within each tier**, not across all six nodes — a deliberate
design choice that downweights candidate nodes by construction:

```
Validated tier:  π_norm(node) = ETS(node) / Σ_validated ETS         (Σ_validated = 8.5,  weights sum to 1.00)
Candidate tier:  π_norm(node) = ETS(node) / (2 · Σ_validated ETS)   (= ETS / 17.0,        weights sum to 0.21)
```

Therefore the six displayed weights sum to **1.21 by construction** — this is not an
arithmetic error and not a single probability distribution over all nodes. `π_norm` is a
tiered weighting used **up to proportionality** in the posterior (which is itself a
proportionality, `∝`). Reproduced weights: 0.29 / 0.47 / 0.24 (Validated) and
0.09 / 0.06 / 0.06 (Candidate).

**Assumption / rationale.** The candidate tier is divided by `2 · Σ_validated` so that a
candidate node can never out-weight a validated node of equal ETS; the factor of two is a
fixed structural choice (not fitted), stated so reviewers can vary it and observe that
tier membership is unaffected (the score, not the normalisation, sets the tier).

## 4. Posterior coupling

`posterior()` returns the unnormalised posterior priority `π_norm(node) · L(node | data)`.
Because `L` is data-dependent and not part of this archive, `mcytomap_ets.py` uses an
explicit, documented placeholder likelihood derived from the four qualitative axis bands
(`HIGH=1.00 … LOW=0.00`) only to demonstrate the coupling; **no published value depends on
that placeholder.** The published, reproduced quantities are the ETS scores and the prior
weights, which are independent of `L`.

## 5. Per-cell ETS

The sex × context refinement (Supplementary Table S1) applies fixed penalties when
stratified causal evidence is absent, with a floor:

```
ETS(node | sex, context) = ETS_base − 0.5·δ_sex − 0.5·δ_stage      (floored at 0.5)
  δ_sex   = 1 if no sex-stratified causal study exists for the node, else 0
  δ_stage = 1 if no context-specific causal study exists,            else 0
```

Example (Piezo1, `ETS_base = 1.0`, no stratified evidence → δ_sex = δ_stage = 1):
`1.0 − 0.5 − 0.5 = 0.0`, floored to **0.5** in every sex × context cell.

## 6. Data structures

`mcytomap_ets.py` is intentionally small and declarative:

- `Node` — a frozen dataclass holding the evidence flags (`n_causal`, `cascade_bonus`,
  `strat_bonus`, `dev_penalty`) and the four qualitative axis bands; `ets`, `tier`, and
  `likelihood` are computed properties.
- `NODES` — the list of the six checkpoints with their published evidence flags.
- `pi_norm(nodes)` / `posterior(nodes)` / `per_cell_ets(...)` — pure functions over `NODES`.

There is no hidden state, no configuration file, and no I/O in the computation path — the
entire prior is a deterministic function of the `NODES` table.

## 7. Design principles

- **Auditability over abstraction.** Every number traces to an explicit flag in `NODES`
  and an arithmetic rule above; a reviewer can recompute any value with a calculator.
- **Determinism.** No randomness, clock, network, or data files in the computation path.
- **No free parameters.** The rubric weights and the tier threshold are fixed, documented
  constants, not values fitted to data.
- **Assertions co-located with outputs.** The reproduction script and tests assert the
  published numbers, so a regression is a hard failure, not a silent drift.
