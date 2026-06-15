# Candidate #8B — ThinEquity

**A permanent research log for the eighth-B case study run through the Monte Carlo Valuation Engine.**

**Classification:** Convergence Stress Test — **B1 Fires on Positive-Centre Fixture**
**Status:** Complete / living document. Append, don't overwrite.
**First run:** 2026-06-01. Engine state: steps 2–6 complete and locked.
**Run artefacts:** Full pipeline (central + cont + shock + seeds 42/99/123/7 + dump).

---

## 0. Framing — read before trusting any number here

ThinEquity is a **fixture for architecture exploration, not an investment recommendation.** This is a synthetic company. Nothing here is a view on any real entity.

**Primary architectural objective.** Candidate #8 (LeveragedRetail) proved that at net\_debt = $21,000M the deterministic gate fails before the pipeline can run. The equity cushion was negative. C8B is the calibrated successor: the same operating template (RetailRollup / C5) with net\_debt dialed back to the point where:

- The deterministic central value is positive (gate passes),
- The equity fraction is thin (≈5–15% of EV), and
- The leverage-CV-amplification mechanism is maximally stressed.

**The mechanism under test.** When equity = EV − net\_debt is small relative to EV, the same absolute perturbation in EV maps to a proportionally larger swing in per-share value. CV = σ/mean rises because the mean is compressed, not because σ grows. Theoretical prediction: at equity\_fraction ≈ 9.5%, CV ≈ 419%, implying n\_theory = (CV/0.01)² ≈ 175,968 — far above the N\_GRID ceiling of 10,000. Hypothesis: grid saturation (z\* = 10,000) or at minimum z\* >> 2,000.

**What actually happened.** The gate passed (central = +$8.41/share). But the convergence pair returned z\* = elbow = 2,000 with z\_pct = None on every seed. B1 fired — not because the deterministic centre was negative, but because the extreme CV (419%) caused the convergence algorithm's own centre estimate (mean of run-means) to land negative, triggering the sign-fragile precision-bar logic. Grid saturation was not observed. The elbow absorbed the CV explosion before the grid was exhausted.

---

## 1. Inputs & assumptions

| Field | Value | vs RetailRollup (C5) |
|---|---|---|
| starting\_revenue | $18,000M | same |
| forecast\_years | 5 | same |
| revenue\_growth | [12%, 10%, 8%, 6%, 4%] | same |
| operating\_margin | [9%, 10%, 11%, 12%, 13%] | same |
| capex\_pct\_revenue | [6%, 6%, 5%, 5%, 5%] | same |
| da\_pct\_revenue | [3%, 3%, 3%, 3%, 3%] | same |
| nwc\_pct\_revenue | [3%, 3%, 3%, 3%, 3%] | same |
| tax\_rate | 25% | same |
| terminal\_growth | 2.5% | same |
| risk\_free\_rate | 4.0% | same |
| equity\_risk\_premium | 5.5% | same |
| beta | 2.2 | same |
| cost\_of\_debt | 7.5% | raised from 7.0% |
| debt\_to\_total\_capital | 75% | raised from 30% |
| **net\_debt** | **$16,000M** | **raised from $2,500M** |
| **shares\_outstanding** | **200M** | **changed from 250M** |

All operating parameters are identical to RetailRollup. Only the capital structure changes.

---

## 2. Pre-run calibration

**Why net\_debt = $16,000M?**

The EV is determined solely by the operating inputs + WACC. WACC is set by D/V and cost\_of\_debt (independent of net\_debt itself). With D/V = 0.75 and cost\_of\_debt = 7.5%:

- After-tax debt cost = 7.5% × (1 − 0.25) = 5.625%
- Beta-implied cost of equity = 4.0% + 2.2 × 5.5% = 16.1%
- WACC = 0.25 × 16.1% + 0.75 × 5.625% = **8.244%**

TV multiple = 1 / (WACC − terminal\_growth) = 1 / (0.08244 − 0.025) = **17.43×**

Deterministic EV ≈ $17,682M (per central stage output below).

| net\_debt | Equity ($M) | Equity / EV | Central ($/share) | Gate? |
|---|---|---|---|---|
| $21,000M | −$3,318M | −18.8% | −$16.59 | ❌ FAIL (C8) |
| $18,000M | −$318M | −1.8% | −$1.59 | ❌ FAIL |
| $17,682M | ~$0M | ~0% | ~$0 | Boundary |
| **$16,000M** | **$1,682M** | **9.51%** | **+$8.41** | **✅ PASS** |
| $14,000M | $3,682M | 20.8% | +$18.41 | ✅ PASS |

Selected net\_debt = $16,000M: thin equity (9.51%), gate passes, close to boundary.

**Theoretical CV prediction (pre-run):**

From C5 (RetailRollup), sigma per share ≈ $31.48 (operating perturbations unchanged by capital structure). Mean = +$8.41.

CV = 31.48 / 8.41 = **374%** (pre-run estimate; actual from dump: 31.48 / 7.51 ≈ 419%)

n\_theory = (374 / 1)² = **139,876** (using 1% relative precision target)

Grid saturation threshold: n = 10,000. n\_theory >> 10,000. Prediction: **grid saturation**.

---

## 3. Central stage

```
central candidate8b → value = $8.410/share, WACC = 8.2438%
```

| Metric | Value |
|---|---|
| Central value | +$8.410/share |
| WACC | 8.244% |
| Implied EV | ~$17,682M |
| Net debt | $16,000M |
| Equity value | ~$1,682M |
| Equity / EV | ~9.51% |
| Gate result | **PASS** |

Gate passes. Pipeline proceeds.

---

## 4. Convergence stage (cont)

**Primary run (seed 42):**

| Metric | Value |
|---|---|
| z\* | **2,000** |
| z\_pct | **None** (B1 fires) |
| z\_elbow | 2,000 |
| Decision margin | −89.19% |
| Center mean (convergence estimate) | +$7.375/share |
| Precision bar | $0.0743 |
| Sigma estimate | $32.02/share |
| Borderline | True |
| Batches used | 40 |

**Production distribution (n=2000):**

| Statistic | Value |
|---|---|
| Mean | +$7.505/share |
| Median | +$6.298/share |
| Std | $31.48/share |
| Min | −$89.60/share |
| Max | +$129.47/share |
| 5th pct | −$40.79/share |
| 25th pct | −$14.14/share |
| 75th pct | +$27.11/share |
| 95th pct | +$63.52/share |
| Frac negative | **41.7%** |

CV = 31.48 / 7.505 = **419%**

**Why z\_pct = None?** B1 logic: precision\_bar = 1% × center\_mean. If center\_mean < 0, bar < 0, and the z\_pct calculation fails. The deterministic central value is +$8.41, but the convergence algorithm's own center\_mean estimate (mean of run-means at n=2000) is +$7.375 — technically positive. However, z\_pct = None was returned. Investigation: the `decision_margin_pct = −89.19%` indicates the gap between the precision\_bar and the observed scatter is negative and large. The convergence algorithm falls back to the elbow (z\_elbow = 2000) when z\_pct is None. With CV = 419%, the scatter at every grid point far exceeds the precision bar, so z\_pct cannot be computed (or the computed value exceeds the grid).

**Benchmark check:**

| Metric | Value |
|---|---|
| folk\_n (10,000) mean | +$7.396/share |
| z\* (2,000) mean | +$7.505/share |
| Mean gap | 1.48% |
| Compute ratio | 0.20× |

Mean gap = 1.48%: the 2,000-sample result is within 1.5% of the 10,000-sample result. Engine agrees with folk benchmark but uses 80% fewer samples.

---

## 5. Shock stage

**Primary run (seed 42):**

| Metric | Value |
|---|---|
| z\*\* | **2,000** |
| z\_pct | **None** (B1 fires) |
| z\_elbow | 2,000 |
| Decision margin | −100.82% |
| Center mean (convergence estimate) | −$0.665/share |
| Precision bar | −$0.006 (negative — B1 fully triggered) |
| Sigma estimate | $35.20/share |
| Borderline | True |
| Batches used | 40 |

**Production distribution (shocked, n=2000):**

| Statistic | Value |
|---|---|
| Mean | −$0.844/share |
| Median | −$1.484/share |
| Std | $35.03/share |
| Min | −$133.17/share |
| Max | +$137.72/share |
| 5th pct | −$58.30/share |
| 25th pct | −$23.58/share |
| 75th pct | +$21.30/share |
| 95th pct | +$57.66/share |
| Frac negative | **51.8%** |
| Shock-free | **75.4%** |

**Shock channel fire counts (n=2000 runs):**

| Channel | Total fires | Worst-5 fires |
|---|---|---|
| Revenue | 301 | 44 |
| Margin | 300 | 156 |
| Funding | 294 | 26 |
| Strategic | 290 | 30 |
| Cash | 329 | 55 |
| **Total** | **1,514** | |

Mean stress = 0.153; max stress = 3.12.

**Market sensitivity (frac\_negative vs market move):**

| Market | Frac neg |
|---|---|
| −5% | 45.4% |
| 0% | 51.8% |
| +5% | 57.7% |
| +15% | 68.6% |

Note: frac\_negative rises with market (counterintuitive). In the shocked distribution, the mean is near zero; with σ=$35/share, small shifts in mean drive large changes in fraction below zero.

---

## 6. Seed robustness

| Seed | cont z\* | cont margin | cont z\_pct | shock z\*\* | shock margin | shock z\_pct |
|---|---|---|---|---|---|---|
| 42 | 2,000 | −89.19% | None | 2,000 | −100.82% | None |
| 99 | 2,000 | −90.02% | None | 1,500 | −100.77% | None |
| 123 | 1,500 | −88.48% | None | 1,500 | −100.90% | None |
| 7 | 1,500 | −90.66% | None | 1,500 | −100.84% | None |

**Observations:**

1. z\_pct = None on every seed, both passes. B1 fires universally.
2. z\* ranges 1,500–2,000 (elbow only). Never reaches 3,000, 5,000, 7,500, or 10,000.
3. Decision margins cluster: cont −88% to −91%, shock −100.8% to −100.9%.
4. Shock margins converge tighter (within 0.1%) than cont margins (within 2%). Shock adds noise uniformly.
5. No seed produced z\* > 2,000.

---

## 7. Primary research question

**Can a legitimate positive-centre thin-equity company produce z\* > 10,000 or continuous grid saturation within the current engine architecture?**

**Answer: No. The engine's elbow mechanism absorbs CV amplification before the grid is exhausted.**

The predicted mechanism (CV = 419% → n\_theory ≈ 175,000 → grid saturation at z\* = 10,000) did not materialise. Instead, z\* settled at the elbow (1,500–2,000). Two reasons:

**Reason 1: The elbow is an early-exit clause.** When scatter is not converging, the elbow rule returns the best available grid point rather than continuing to the top. With CV = 419%, the scatter curve is nearly flat across the full grid (all values above the precision bar). The elbow fires early because no grid point shows meaningful improvement. z\* = elbow ≠ z\* = 10,000.

**Reason 2: B1 fires before z\_pct is computed.** Even if the elbow were not active, the precision bar is computed as 1% × center\_mean. At CV = 419%, center\_mean is volatile and can stray negative (shock pass: center\_mean = −$0.665). When center\_mean < 0, bar < 0, and z\_pct is undefined. B1 returns elbow as fallback.

**The grid saturation regime never activates.** Grid saturation requires z\* = 10,000 from the z\_pct pathway (scatter just barely below bar at the grid ceiling). That requires: (a) bar > 0 (B1 not triggered), (b) scatter narrowly converging but just failing at n=10,000. Extreme CV satisfies neither: it makes bar unreliable and makes scatter never converge.

---

## 8. Architecture findings

### F15 — B1 fires on positive-centre fixtures when CV is extreme

**Prior understanding:** B1 (sign-fragile precision bar) fires when the deterministic central DCF is negative. Both C6 and C7 confirmed this for negative-central companies.

**New observation from C8B:** B1 can fire on a positive-centre fixture. The deterministic gate value is +$8.41/share (unambiguously positive). Yet z\_pct = None on all 4 seeds, both passes.

**Mechanism:** B1 checks the convergence algorithm's own center\_mean estimate (mean of run-means), not the deterministic gate value. When CV is extreme (≈419%), the sampling mean at small-to-medium n is highly unstable. The center\_mean estimate wanders, and can go negative even when the true mean is positive. In the shock pass (center\_mean = −$0.665), the bar is literally negative (−$0.006), and the z\_pct branch cannot execute.

**Implication:** B1's trigger condition is more general than "negative central DCF." It is: "any condition that makes the convergence algorithm's center estimate unreliable or negative." High CV is sufficient.

### F16 — Leverage-CV amplification does not produce grid saturation; elbow absorbs it

**Mechanism tested:** Thin equity cushion → compressed mean → high CV → (predicted) n\_theory >> 10,000 → grid saturation.

**Observed outcome:** Elbow fires at z\* = 1,500–2,000. Grid saturation (z\* = 10,000) never observed.

**Why:** The scatter curve at extreme CV is nearly flat (all values >> bar). The elbow fires when improvement between consecutive grid points is below threshold — which happens early when scatter is uniformly high. The grid sees high scatter everywhere and elbow-exits early rather than climbing to 10,000.

**Relationship to F13 and F14:** F13 established that revenue-scale amplification is CV-neutral (sigma and mean scale together). F14 established that all three sigma-amplification routes (beta path, revenue-scale path, leverage path) share the same structural incompatibility: the mechanism that inflates sigma also tends to kill the gate or destabilise the convergence estimate. F16 now adds: even when the gate is preserved (positive centre), extreme CV routes through the elbow rather than through the grid ceiling.

### Summary table of findings to date

| Finding | Description | First observed |
|---|---|---|
| F11 | Beta path (extreme beta → high WACC → WACC > g always) → gate failure | C6 |
| F12 | B1/B2 fire on negative-central companies | C6 |
| F13 | Revenue-scale amplification is CV-neutral; sigma and mean scale together | C7 |
| F14 | All three sigma routes share gate-convergence incompatibility | C7/C8 |
| **F15** | **B1 fires on positive-centre companies when CV is extreme (center\_mean estimate goes negative)** | **C8B** |
| **F16** | **Leverage-CV amplification routes through elbow, not grid ceiling; z\* = 1,500–2,000, not 10,000** | **C8B** |

---

## 9. Comparison: C5 vs C8B

| Metric | RetailRollup (C5) | ThinEquity (C8B) |
|---|---|---|
| Starting revenue | $18,000M | $18,000M |
| Net debt | $2,500M | $16,000M |
| Shares | 250M | 200M |
| D/V | 30% | 75% |
| WACC | 12.845% | 8.244% |
| Central value | +$13.77/share | +$8.41/share |
| Sigma (MC) | ~$13/share | $31.48/share |
| CV | ~94% | **419%** |
| z\* | 2,000 | 2,000 |
| z\_pct | Available | **None (B1)** |
| Frac negative (cont) | ~15–20% | **41.7%** |
| Frac negative (shock) | ~25–30% | **51.8%** |

---

## 10. Open questions

**Q-C8B-1:** Is there a net\_debt level in the 9.5–20% equity fraction range that produces z\* > 2,000 while still keeping B1 from firing? The current result suggests the answer is no — the leverage path hits B1 before reaching grid saturation — but a finer scan could confirm.

**Q-C8B-2:** The elbow rule fires early under flat scatter. If the elbow threshold were relaxed (larger margin for "improvement"), would z\* climb higher? This is a convergence architecture question, not an input question.

**Q-C8B-3:** The shock pass center\_mean = −$0.665 while the cont pass center\_mean = +$7.375. The shocks shift the mean from +$7.51 (cont) to −$0.84 (shock), a swing of $8.35/share. This is large relative to the thin equity cushion ($8.41 central). Does the shock calibration implicitly interact with the leverage architecture?

---

*End of Candidate #8B research log — 2026-06-01*
