# NVDA Case Study — Architecture Investigation Log

**Date:** 2026-06-01  
**Trigger:** z\*\* < z\* observed for the first time on a real-company fixture.

---

## Observation: z\*\* = 1,500 < z\* = 2,000 (Shocked elbow lands earlier than continuous elbow)

### What happened

The NVIDIA case study produced the following convergence readings:

| Pass | z | σ estimate | Precision bar |
|---|---|---|---|
| Continuous (z\*) | 2,000 | $17.71/share | $0.660 |
| Shocked (z\*\*) | 1,500 | $18.50/share | $0.625 |

The shocked pass converged at a *smaller* sample size than the continuous pass, despite the shocked σ being higher ($18.50 vs $17.71). This is unusual. The standard expectation — well-established in earlier candidates — is that shocks fatten the left tail, raise effective variance, and require a larger n to stabilise the run-mean scatter. The gap z\*\* − z\* is normally positive and is considered a headline finding in its own right: it quantifies what the discrete-event risk costs in required sample size. Here, z\*\* − z\* = −500 (negative).

### Scatter curves

The raw scatter values (standard deviation of 40 run-means at each n) are:

| n | Continuous | Shocked |
|---|---|---|
| 100 | 1.556 | 1.722 |
| 250 | 1.026 | 1.454 |
| 500 | 0.896 | 0.789 |
| 1,000 | 0.523 | 0.576 |
| **1,500** | **0.454** | **0.457** |
| **2,000** | **0.379** | **0.466** |
| 3,000 | 0.307 | 0.317 |
| 5,000 | 0.253 | 0.229 |
| 7,500 | 0.168 | 0.173 |
| 10,000 | 0.172 | 0.187 |

Two features stand out:

**Feature 1: Non-monotone bump in the shocked scatter at n = 2,000.** The shocked scatter at n = 2,000 (0.466) is *higher* than at n = 1,500 (0.457). The scatter increased from n = 1,500 to n = 2,000 rather than decreasing. This local non-monotonicity is within the expected noise band for 40-batch estimates — it is a finite-sample fluctuation, not a structural property of the distribution. But it has a direct mechanical consequence: the elbow algorithm, which identifies where the scatter curve transitions from steep to flat, reads the curve as having elbowed at n = 1,500 because the subsequent value at n = 2,000 did not continue the descent. The elbow is at the right place given the data; the data itself is noisy at this segment of the curve.

**Feature 2: Convergence of the continuous and shocked curves below n = 1,500.** At n = 1,500, the two scatter values are nearly identical: 0.454 (continuous) vs 0.457 (shocked). For larger n — 5,000, 7,500 — the shocked scatter runs slightly above the continuous scatter, as expected. The large-sample asymptotic behaviour is consistent with the prior: shocked σ > continuous σ, so the shocked scatter is higher in the limit. The elbow artefact only affects the n = 1,500 vs n = 2,000 range.

### Root cause

The non-monotone bump at n = 2,000 in the shocked scatter is a finite-batch sampling artefact, not an architectural signal. With 40 batches per n, each scatter estimate carries a standard error of approximately σ_scatter / √(2 × 39) ≈ σ_scatter / 8.8. A local reversal of the size seen here (0.457 → 0.466, a 2% increase) is easily explained by sampling noise at this batch count.

The consequence: the elbow detection algorithm reads the curve correctly (elbow at the point where descent stopped) but the descent stopped due to noise rather than the curve genuinely flattening. If the sweep were repeated at 80 batches per n, the bump would likely smooth out and the shocked elbow would fall at n = 2,000 or 3,000 — consistent with the theoretical expectation.

### Implication for NVIDIA's result

The shocked production run at z\*\* = 1,500 is not *wrong* — the distribution it produces is correctly characterised (mean $62.65, 0% negative, tail behaviour consistent with the channel diagnostics). But the convergence determination carries a lower confidence than typical: the 36.6% decision margin (vs 74.1% for continuous) and the 16-batch recommendation signal that the apparatus itself recognises the elbow call is less certain than usual.

A conservative practitioner would note that z\*\* = 1,500 may be an underestimate and that running the shocked production engine at z\*\* = 2,000 or even 3,000 would be prudent for high-stakes decisions. The seed robustness table partially addresses this: three of four seeds (42, 123, 7) agree on z\*\* = 1,500; seed 99 resolves at 2,000. The true z\*\* is plausibly in the 1,500–2,000 range, and the qualitative conclusions of the report are unaffected regardless of which end of that range is correct.

### Architecture note

This observation does not indicate a defect in the engine. The convergence module correctly processes the scatter data it receives. The issue is that 40 batches is occasionally insufficient to smooth the scatter curve in the n = 1,500–2,000 transition zone, causing a noise-driven local reversal to register as a genuine elbow.

The existing `CONVERGENCE_DECISION_SIGMAS = 2.0` and `batches_recommended` mechanism already partially addresses this: the low margin and high batch-count recommendation signal to the user that this determination is borderline. The recommendation of 16 batches (vs 5 for continuous) is the engine's own self-report that it needed more evidence.

**Future consideration (not a change request):** If a candidate exhibits a shocked elbow below its continuous elbow, the engine could optionally flag this as a potential artefact and suggest a re-run at the continuous z\* as a cross-check. This is a reporting enhancement, not a logic change. It is flagged here for potential inclusion in the Step 7 input-validation and reporting layer.

---

## Status

Logged. Does not affect the NVIDIA valuation report conclusions. The shocked distribution, production statistics, and channel diagnostics are all valid. The z\*\* = 1,500 vs z\* = 2,000 inversion is noted with appropriate caveats in Section 8 of the case study report and explained fully here.

*No engine logic was modified in connection with this observation.*
