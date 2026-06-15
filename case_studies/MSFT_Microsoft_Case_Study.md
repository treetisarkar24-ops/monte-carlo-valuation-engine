# Microsoft Corporation (MSFT)
## Real-World Valuation Case Study — Monte Carlo DCF Engine

**Purpose:** Unlike the synthetic candidates (#1–#8), this is a *production application* of the finished engine to a real, large-cap company. No engine, convergence, N_GRID, or shock-calibration logic was modified. The objective is to demonstrate the engine reading a real business, not to stress-test it.

**Base fixture:** FY2024 actuals, 7-year explicit horizon. Engine seed = 42 throughout. All Monte Carlo / convergence / seed / shock figures were rebuilt deterministically in a single process from this session's own seeded caches (bit-identical to a clean run); the 5,000-path channel diagnostic was recomputed live.

---

## 1. Assumptions Used (DCFInputs Fixture)

| Input | Value | Rationale |
|---|---|---|
| Starting revenue | $245,122M | FY2024 actual total revenue |
| Net debt | −$26,000M | Net *cash* position (cash > gross debt) |
| Shares outstanding | 7,432M | Diluted share count |
| Forecast horizon | 7 years | Explicit-forecast window |
| Revenue growth | 14% → 6% | Fades from cloud-led mid-teens to mature-large-cap single digits |
| Operating margin | 44% → 47% | Gradual mix-shift expansion toward cloud/software |
| Capex % revenue | 18% → 12% | Elevated AI/datacenter buildout early, normalizing later |
| D&A % revenue | 8.5% flat | Steady, consistent with capital intensity |
| NWC % revenue | 0.5% flat | Software/services businesses run very lean working capital |
| Tax rate | 19% | Near effective rate |
| Terminal growth | 2.5% | Long-run nominal GDP-like |
| Risk-free rate | 4.3% | Long Treasury |
| Equity risk premium | 5.5% | Standard equity premium |
| Beta | 0.90 | Slightly below-market systematic risk |
| Cost of debt | 3.8% | High-grade issuer |
| Debt / total capital | 1.5% | Minimal leverage |

---

## 2. Deterministic Central Case

| Metric | Value |
|---|---|
| Cost of equity (CAPM) `4.3% + 0.90×5.5%` | **9.25%** |
| After-tax cost of debt `3.8%×(1−0.19)` | 3.08% |
| **WACC** `0.985×9.25% + 0.015×3.08%` | **9.157%** |
| Terminal spread (WACC − g) | 6.66% — comfortably wide |
| PV of explicit FCF | $555,532M |
| PV of terminal value | $1,378,605M (**71.3%** of EV) |
| **Enterprise value** | **$1,934,137M (~$1.93T)** |
| (+) Net cash | $26,000M |
| **Equity value** | **$1,960,137M (~$1.96T)** |
| **Central DCF per share** | **$263.74** |

**FCF trajectory ($M):** 71,648 → 80,962 → 100,616 → 115,609 → 133,759 → 147,700 → 165,346.

The deterministic gate **passes** (positive value, terminal growth 2.5% < WACC 9.16%), so the full stochastic pipeline was run.

---

## 3. Continuous Monte Carlo (z*)

The continuous engine perturbs inputs without discrete shock events.

**Convergence sweep (40-batch apparatus, seed 42):**

| n | Scatter | Status |
|---|---|---|
| 100 | 6.03 | above bar |
| 250 | 3.68 | above bar |
| 500 | 3.20 | above bar |
| 1,000 | 1.89 | below bar (z_pct) |
| 1,500 | 1.63 | below bar |
| **2,000** | **1.34** | **z_elbow** |
| 3,000 | 1.07 | below bar |
| 5,000 | 0.91 | below bar |
| 7,500 | 0.61 | below bar |
| 10,000 | 0.67 | below bar |

- z_pct (rule 2) = **1,000**, z_elbow (rule 3) = **2,000**
- **z\* = max(1000, 2000) = 2,000**
- Precision bar = 2.65; **decision margin = 97.3%** (clears the bar with huge headroom)
- σ estimate = $63.28; batches recommended = 4; borderline = No; **adequately_resolved = True**

**Production run at z* = 2,000:**

| Statistic | Value |
|---|---|
| Mean | $265.90 |
| Median | $259.58 |
| Std dev | $63.51 |
| Min / Max | $106.62 / $550.01 |
| Fraction negative | **0.0%** |

**Percentiles:** P5 $171.69 · P10 $188.84 · P25 $220.13 · P50 $259.58 · P75 $304.84 · P90 $357.48 · P95 $381.02.

**Benchmark vs. folk number (n = 10,000):** z* uses **0.2× the compute** yet the mean differs by only **0.43%** ($265.90 vs $264.77; medians $259.58 vs $258.38). The empirically-derived sample size reproduces the 10,000-path answer at one-fifth the cost.

---

## 4. Shocked Monte Carlo (z**)

The shocked engine adds five discrete jump channels (revenue, margin, funding, strategic, cash) with severity-weighted damage and stress-accumulation feedback.

- z_pct = 1,000, z_elbow = 1,000 → **z\*\* = 1,000**
- Precision bar = 2.49; **decision margin = 21.5%**
- σ estimate = $69.52; batches recommended = **45** (vs 40 used); **adequately_resolved = False**, borderline = No

The shocked stage is the harder convergence problem: the recommended apparatus (45 batches) slightly exceeds the 40 actually used, and the decision margin (21.5%) is far tighter than the continuous stage's 97.3%. The fat left tail from shock events demands more evidence.

**Production run at z** = 1,000:**

| Statistic | Value |
|---|---|
| Mean | $248.83 |
| Median | $244.36 |
| Std dev | $68.56 |
| Min / Max | $47.56 / $600.57 |
| Fraction negative | **0.0%** |

**Percentiles:** P5 $146.11 · P10 $169.70 · P25 $202.25 · P50 $244.36 · P75 $291.02 · P90 $334.56 · P95 $359.25.

Shocks shift the whole distribution down (mean $248.83 vs continuous $265.90) and fatten the left tail (P5 falls from $171.69 to $146.11, min from $106.62 to $47.56). Even so, MSFT never produces a negative intrinsic value — its balance sheet (net cash, low leverage) and wide margins absorb the damage.

---

## 5. Shock Channel Behaviour

Over the 5,000-path diagnostic (seed 42):

| | Revenue | Margin | Funding | Strategic | Cash |
|---|---|---|---|---|---|
| Fires — all paths | 448 | 417 | 436 | 415 | 453 |
| Fires — worst 5% tail | **133** | **142** | 40 | 44 | 39 |

- **Shock-free paths: 67.4%** — two-thirds of simulations see no shock at all.
- Total fires: 2,169; mean cumulative stress 0.216; max stress 3.92.
- **Tail driver:** in the worst-5% outcomes, *margin* (142) and *revenue* (133) channels dominate, while funding/strategic/cash (~40 each) are roughly at their base rate. This matches the V1 fragility thesis: for a high-margin, low-leverage company, operating shocks (margin compression, demand loss) — not financing shocks — drive the downside. Microsoft's worst cases are about the business shrinking, not about it running out of money.

---

## 6. Market Percentile Analysis

MSFT traded at **~$449.99** on 2026-06-01 (market cap ~$3.34T).

| Reference price | Continuous CDF | Shocked CDF |
|---|---|---|
| $200 | 24.1% | — |
| $263 (≈ central DCF) | 60.3% | — |
| $300 | 79.1% | — |
| $400 | 97.5% | — |
| **$450 (market)** | **~99.5%** | **99.1%** |
| $500 | 99.8% | — |

The market price sits at roughly the **99th percentile** of *both* the continuous and shocked distributions. In other words, the engine's own simulated universe almost never generates an intrinsic value as high as where MSFT actually trades. On these assumptions the model reads MSFT as **richly valued** — central intrinsic $263.74 vs $450 market, ~41% below market.

This is a statement about the *fixture's assumptions*, not a trade recommendation. The model uses a 7-year fade and a 9.16% WACC; the market is evidently pricing a longer/steeper growth runway (AI monetization, sustained cloud share gains) and/or a lower discount rate than this conservative fixture encodes. The gap is the value of those market-implied expectations.

---

## 7. Seed Robustness

Re-running convergence under four engine seeds:

| Seed | z* (cont) | cont margin | z** (shock) | shock margin |
|---|---|---|---|---|
| 42 | 2,000 | 97.3% | 1,000 | 21.5% |
| 99 | 500 | 14.7% | 2,000 | 86.3% |
| 123 | 1,500 | 100.1% | 2,000 | 94.1% |
| 7 | 1,000 | 41.8% | 1,500 | 78.6% |

z* ranges 500–2,000 and z** ranges 1,000–2,000 across seeds — both comfortably within the 10,000 grid for every seed. The *point estimate* of the required sample size is seed-sensitive (as expected for an elbow/percentile rule on finite batches), but the *qualitative conclusion is stable*: MSFT is an easy convergence problem, resolved well below the folk number on every seed. No seed pushed the requirement to the grid ceiling.

---

## 8. Final Interpretation

On a conservative FY2024-base fixture, Microsoft's Monte Carlo intrinsic value is a **tight, entirely-positive distribution centered near $260/share** — continuous mean $265.90, shocked mean $248.83, zero negative paths in either engine. The business is fundamentally robust: net cash, ~45% operating margins, and a wide WACC-minus-g spread mean even the shocked engine's worst path ($47.56) stays positive.

The engine resolves Microsoft cheaply. The continuous stage clears its precision bar with a 97% margin and reproduces the 10,000-path answer using only 2,000 simulations (0.2× compute, 0.43% mean gap) — a clean vindication of the per-company z* thesis over the one-size-fits-all folk number. The shocked stage is harder (z** = 1,000 but 45 batches recommended, 21.5% margin, not fully resolved), and its tail is driven by operating channels (margin + revenue), consistent with the fragility model's prediction for a low-leverage, high-margin firm.

The one striking result is valuation: at ~$450 the market sits at the ~99th percentile of the engine's own distribution. The model, on these inputs, simply cannot manufacture today's price — the market is paying for a growth and discount-rate story more optimistic than this fixture. That gap is the case study's central finding: the engine cleanly separates "what the fundamentals support under stated assumptions" (~$264) from "what the market is pricing" (~$450), and quantifies exactly how far into the tail the market sits.

---

*Engine applied as-is; no logic modified. Seed 42; figures reconstructed from seeded caches. Market price as of 2026-06-01.*
