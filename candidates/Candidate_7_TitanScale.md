# Candidate #7 — TitanScale
## Convergence Stress Test Report

**Design intent:** Revenue-scale amplification stress test. Very large revenue base (30,000), very small share count (50), moderate-to-high beta (2.3), positive-centre economics. Primary question: can a positive-centre company produce evidence that the true convergence requirement lies beyond the current 10,000-simulation grid?

---

## 1. Deterministic Central Case

| Parameter | Value |
|---|---|
| WACC | 13.800% |
| Cost of equity (CAPM) | 16.650% |
| Central per-share DCF | **$459.24** |

WACC derivation: `0.04 + 2.3 × 0.055 = 16.65%` cost of equity; `0.07 × 0.75 = 5.25%` after-tax cost of debt; `0.75 × 16.65% + 0.25 × 5.25% = 13.80%` WACC. Terminal spread = `13.80% − 2.50% = 11.30%` — moderate, but sensitive to perturbation in beta and ERP.

---

## 2. Sigma Survey (n = 40,000 reference run)

| Metric | Value |
|---|---|
| Mean per-share | $468.80 |
| Std dev (σ) | $155.79 |
| Coefficient of variation (CV) | **33.23%** |
| Precision bar (1% of mean) | $4.69 |
| SE at n = 10,000 | $1.56 |
| SE / bar at n = 10,000 | **0.33** (well below bar) |
| Theoretical n for rule-2 clearance | **~1,100** |

**Critical finding:** Revenue-scale amplification raises absolute σ enormously ($155 vs Steady Co's ~$3), but the 1% precision bar scales proportionally with the mean. The ratio σ/mean (CV = 33%) is what governs convergence. The theoretical true requirement is ~1,100 — far within the 10,000 grid ceiling.

---

## 3. z* — Continuous Engine

**10-batch sweep (fast pass):**

| n | Scatter | Bar | Scatter/Bar | Status |
|---|---|---|---|---|
| 100 | 15.68 | 4.69 | 3.34 | ABOVE BAR |
| 250 | 9.86 | 4.69 | 2.10 | ABOVE BAR |
| 500 | 5.81 | 4.69 | 1.24 | ABOVE BAR |
| 1,000 | 6.49 | 4.69 | 1.38 | ABOVE BAR |
| **1,500** | **4.06** | **4.69** | **0.87** | **below bar** |
| 2,000 | 2.31 | 4.69 | 0.49 | below bar |
| 3,000 | 2.86 | 4.69 | 0.61 | below bar |
| 5,000 | 2.41 | 4.69 | 0.51 | below bar |
| 7,500 | 1.46 | 4.69 | 0.31 | below bar |
| 10,000 | 0.96 | 4.69 | 0.20 | below bar |

- **z_pct (rule 2):** 1,500
- **z_elbow (rule 3):** 2,000
- **z\* = max(1500, 2000) = 2,000**
- Borderline: **No**
- z* clears bar by: 102.8%
- Per-simulation σ: $156.98

> z* does **not** reach 10,000. The grid is cleared comfortably from n = 1,500 onward.

---

## 4. z** — Shocked Engine

**23-batch sweep (recommended apparatus):**

| n | Scatter | Bar | Scatter/Bar | Status |
|---|---|---|---|---|
| 100 | 17.18 | 4.35 | 3.95 | ABOVE BAR |
| 250 | 10.22 | 4.35 | 2.35 | ABOVE BAR |
| 500 | 8.64 | 4.35 | 1.99 | ABOVE BAR |
| 1,000 | 5.66 | 4.35 | 1.30 | ABOVE BAR |
| **1,500** | **4.61** | **4.35** | **1.06** | **ABOVE BAR** ← thin margin |
| **2,000** | **3.27** | **4.35** | **0.75** | **below bar** |
| 3,000 | 2.97 | 4.35 | 0.68 | below bar |
| 5,000 | 2.29 | 4.35 | 0.53 | below bar |
| 7,500 | 2.28 | 4.35 | 0.52 | below bar |
| 10,000 | 1.57 | 4.35 | 0.36 | below bar |

- **z_pct (rule 2):** 2,000
- **z_elbow (rule 3):** 2,000
- **z** = 2,000**
- Borderline: **No**
- z** clears bar by: 33.1% (tighter than z*)
- Per-simulation σ: $170.46 (shocks add ~$13.5 in tail width)
- z* moved between passes: **No** — stable at 2,000

**Notable:** At n = 1,500, scatter/bar = 1.06 — the shocked engine is genuinely on the knife-edge. The grid correctly catches this: z** = 2,000, not 1,500. This is the closest TitanScale gets to the thin-margin success criterion.

---

## 5. z* → z** Gap Analysis

| Metric | z* | z** |
|---|---|---|
| Sample size found | 2,000 | 2,000 |
| Per-simulation σ | $156.98 | $170.46 |
| σ increase from shocks | — | +$13.48 (+8.6%) |
| Precision bar | $4.69 | $4.35 |
| Decision margin | 102.8% | 33.1% |

The shock layer widens σ by 8.6%, which tightens the decision margin at z** = 2,000 significantly (from 103% down to 33%). However, neither z* nor z** migrates to a higher grid rung — both settle at 2,000. The z*→z** gap in sample size is zero, though the gap in confidence margin is meaningful.

---

## 6. Benchmark — z* vs Folk-10,000

*(Same seed, n = 2,000 vs n = 10,000)*

| Metric | z* (n=2,000) | Folk (n=10,000) |
|---|---|---|
| Mean | $470.36 | $469.93 |
| Median | $455.10 | $452.52 |
| Std | $154.98 | $157.44 |
| p5 | $245.17 | $242.81 |
| p25 | $360.65 | $359.37 |
| p75 | $560.49 | $561.66 |
| p95 | $746.94 | $748.74 |
| **Mean gap** | — | **0.09%** |
| **Compute used** | — | **20%** |

The benchmark holds cleanly. Running at z* = 2,000 costs 20% of the folk simulation budget and moves the mean by 0.09%. Benchmark quality does **not** deteriorate — this is a well-converged company.

---

## 7. Grid Saturation Assessment

The stress test explicitly asks: **does TitanScale provide evidence that the true requirement lies beyond 10,000?**

The answer is **no**, and the reason is structural:

**Revenue-scale amplification is scale-neutral for convergence.** The 1% precision bar is a relative criterion (1% of the mean). When revenue scale is multiplied by 10×, both σ and the mean scale together, leaving CV unchanged. Convergence is governed by CV alone:

```
n_true = (σ / (0.01 × mean))² = (CV / 0.01)² = (0.33 / 0.01)² = 1,089
```

No matter how large the revenue base or how small the share count, this ratio is invariant to those choices. TitanScale's CV of 33% translates to a true requirement of ~1,100 — well within the grid.

**What would push z* past 10,000?** A CV > 100% (i.e., σ > mean). This requires either: (a) a distribution so dispersed that the standard deviation exceeds the mean — possible only with extreme perturbation widths or a near-zero (negative-centre) company — or (b) a negative-centre company where the 1% bar collapses toward zero while σ stays large. The positive-centre constraint in TitanScale's design explicitly prevents (b), and the standard trajectory widths prevent (a).

---

## 8. Success Criteria Scorecard

| Criterion | Result | Status |
|---|---|---|
| z* reaches 10,000 | z* = 2,000 | ❌ Not met |
| z** reaches 10,000 | z** = 2,000 | ❌ Not met |
| Borderline active near top rung | No borderline, margin = 33% at z** | ❌ Not met |
| Decision margins thin | z** margin at n=1,500: scatter/bar = 1.06 (knife-edge rung below z**) | ⚠️ Partial |
| Benchmark quality deteriorates | 0.09% mean gap, benchmark holds cleanly | ❌ Not met |
| Evidence true requirement exceeds grid | Theoretical n_true ≈ 1,100 | ❌ Not met |

---

## 9. Conclusion

**TitanScale fails the convergence stress test.** Revenue-scale amplification is not a valid mechanism for straining the 10,000 grid because the precision bar is a relative (percentage) criterion that scales with the mean. The absolute magnitude of per-share values is irrelevant to whether the grid is sufficient.

The one partial finding: the shocked engine at n = 1,500 produces scatter/bar = 1.06, placing z** genuinely on the knife-edge between the 1,500 and 2,000 rungs. This thin margin is a real, if modest, stress signal — the shock overlay meaningfully widens the uncertainty band and tightened the decision from 103% to 33% margin. But it does not saturate the grid.

**Candidate #6 (Project Doom)** demonstrated that a negative-centre company fails the positive-centre gate before convergence can be studied. **Candidate #7 (TitanScale)** demonstrates the complementary finding: a positive-centre company with revenue-scale amplification converges well within the grid. The convergence stress test requires a company whose *relative* uncertainty (CV) approaches or exceeds 100%, not one with large absolute values.

For a fixture that could genuinely stress z* toward or past 10,000, the design would need to either: (1) widen trajectory perturbation widths significantly beyond the 12% default, or (2) construct a company whose operating economics are structurally ambiguous — near the boundary between value-destruction and value-creation — such that small parameter perturbations produce qualitatively different DCF outcomes.

---

*Engine: mc_engine.py + mc_convergence.py (unmodified). N_GRID locked at [100, 250, 500, 1000, 1500, 2000, 3000, 5000, 7500, 10000]. Sweeps run at 10–23 batches per grid point. Seed: 42 (default).*
