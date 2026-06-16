# NVIDIA Corporation (NVDA)
## Real-World Valuation Case Study — Monte Carlo DCF Engine

**Purpose:** A *production application* of the finished engine to NVIDIA, run on a **market-friendly (bullish-but-defensible) operating case** as of **16 June 2026**. No engine, convergence, N_GRID, or shock-calibration logic was modified. The objective is to demonstrate the engine reading a real business at the optimistic end of *defensible* assumptions, and to locate exactly where today's market price sits in the resulting distribution.

**Base fixture:** FY2026 actuals (revenue $215.9B, +65% y/y), 7-year explicit horizon. Engine seed = 42 throughout. The optimism in this fixture lives entirely in the *operating* assumptions (growth, margin, terminal rate); the discount rate was **not** reverse-engineered — beta is held at NVIDIA's defensible historical level of 1.75. The 5,000-path channel diagnostic was recomputed live.

---

## 1. Assumptions Used (DCFInputs Fixture)

| Input | Value | Rationale |
|---|---|---|
| Starting revenue | $215,900M | FY2026 actual total revenue (+65% y/y) |
| Net debt | −$52,000M | Net *cash* position (~$62.6B cash & securities vs minimal debt) |
| Shares outstanding | 24,600M | Diluted, post-2024 10-for-1 split |
| Forecast horizon | 7 years | Explicit-forecast window |
| Revenue growth | 55% → 8% | Bull path: AI/datacenter demand sustained, fading to mature growth |
| Operating margin | 65% → 59% | Holds NVIDIA's elite margins, slight normalization for competition |
| Capex % revenue | 3.0% → 3.5% | Fabless / asset-light model |
| D&A % revenue | 2.0% flat | Low capital intensity |
| NWC % revenue | 2.5% flat | Lean working capital |
| Tax rate | 15% | Near effective rate |
| Terminal growth | 3.0% | Engine's defensible band ceiling (long-run GDP) |
| Risk-free rate | 4.3% | Long Treasury |
| Equity risk premium | 5.5% | Standard equity premium |
| Beta | 1.75 | NVIDIA's defensible historical systematic risk — **not** tuned to hit a target |
| Cost of debt | 4.5% | High-grade issuer |
| Debt / total capital | 5.0% | Minimal leverage |

This is the *market-friendly* case: every operating lever is set to the optimistic edge of what remains defensible, while the cost of capital is left honest. It answers the question "how generous do the fundamentals have to be — without breaking discipline — to approach the market price?"

---

## 2. Deterministic Central Case

| Metric | Value |
|---|---|
| Cost of equity (CAPM) `4.3% + 1.75×5.5%` | **13.925%** |
| After-tax cost of debt `4.5%×(1−0.15)` | 3.825% |
| **WACC** `0.95×13.925% + 0.05×3.825%` | **13.42%** |
| Terminal spread (WACC − g) | 10.42% — very wide |
| PV of explicit FCF | $1,454,550M |
| PV of terminal value | $2,079,743M (**58.8%** of EV) |
| **Enterprise value** | **$3,534,293M (~$3.53T)** |
| (+) Net cash | $52,000M |
| **Equity value** | **$3,586,293M (~$3.59T)** |
| **Central DCF per share** | **$145.78** |

**Revenue trajectory ($M):** 334,645 → 475,196 → 627,259 → 777,801 → 910,027 → 1,019,230 → 1,100,768 (terminal-year revenue ≈ **$1.10T**).

**FCF trajectory ($M):** 173,179 → 241,875 → 313,943 → 382,678 → 435,448 → 479,038 → 508,005.

Even at the bullish operating edge, the 13.42% WACC keeps terminal value to just 58.8% of EV — a notably *un*-stretched DCF for a high-growth name (Microsoft's conservative fixture, by contrast, leans 71% on terminal value). The deterministic gate **passes** (positive value, terminal growth 3.0% < WACC 13.42%), so the full stochastic pipeline was run.

---

## 3. Continuous Monte Carlo (z*)

The continuous engine perturbs inputs without discrete shock events.

- z_pct (rule 2) = **1,000**, z_elbow (rule 3) = **3,000**
- **z\* = max(1000, 3000) = 3,000**
- Decision margin = **160.4%** (clears the precision bar with enormous headroom)
- σ estimate = $44.51; batches recommended = 2; borderline = No; **adequately_resolved = True**

**Production run at z\* = 3,000 (seed 42):**

| Statistic | Value |
|---|---|
| Mean | $147.75 |
| Median | $142.21 |
| Std dev | $44.71 |
| Min / Max | $58.86 / $383.49 |
| Fraction negative | **0.0%** |

**Percentiles:** P5 $84.68 · P10 $95.67 · P25 $115.41 · P50 $142.21 · P75 $172.95 · P90 $206.82 · P95 $231.77.

**Benchmark vs. folk number (n = 10,000):** z\* uses **0.3× the compute** yet the mean differs by only **0.02%** ($147.75 vs $147.79; medians $142.21 vs $141.62). The empirically-derived sample size reproduces the 10,000-path answer at one-third the cost.

**Distribution shape (continuous, z\* = 3,000):**

```
   58.86 | #####  51
   75.09 | ################  178
   91.33 | #############################  324
  107.56 | ######################################  419
  123.79 | ##########################################  463
  140.02 | #########################################  450
  156.25 | ################################  351
  172.48 | #######################  251
  188.71 | #################  190
  204.95 | ############  127
  221.18 | #######  74
  237.41 | ####  47
  253.64 | ###  37
  269.87 | ##  17
  286.10 | #  11
  302.33 |   5
```

---

## 4. Shocked Monte Carlo (z**)

The shocked engine adds five discrete jump channels (revenue, margin, funding, strategic, cash) with severity-weighted damage and stress-accumulation feedback.

- z_pct = 1,000, z_elbow = 1,000 → **z\*\* = 1,000**
- Decision margin = **9.0%**; σ estimate = $46.31; batches recommended = **251** (vs 20 used); **adequately_resolved = False**

The shocked stage is by far the harder convergence problem: the recommended apparatus (251 batches) dwarfs the continuous stage's 2, and the decision margin (9.0%) is razor-thin next to the continuous 160.4%. The fat left tail from shock events demands much more evidence to resolve — the engine reports this honestly rather than assuming convergence.

**Production run at z\*\* = 1,000 (seed 42):**

| Statistic | Value |
|---|---|
| Mean | $139.69 |
| Median | $133.29 |
| Std dev | $46.31 |
| Min / Max | $31.68 / $417.18 |
| Fraction negative | **0.0%** |

**Percentiles:** P5 $73.93 · P10 $87.56 · P25 $107.30 · P50 $133.29 · P75 $166.79 · P90 $198.41 · P95 $217.52.

Shocks shift the whole distribution down (mean $139.69 vs continuous $147.75) and fatten the left tail (P5 falls from $84.68 to $73.93, min from $58.86 to $31.68). Even so, NVIDIA never produces a negative intrinsic value — its net-cash balance sheet and ~60% margins absorb the damage.

---

## 5. Shock Channel Behaviour

Over the 5,000-path diagnostic (seed 42):

| | Revenue | Margin | Funding | Strategic | Cash |
|---|---|---|---|---|---|
| Fires — all paths | 448 | 417 | 436 | 415 | 453 |
| Fires — worst 5% tail | **120** | **123** | 31 | 42 | 36 |

- **Shock-free paths: 67.4%** — two-thirds of simulations see no shock at all.
- Total fires: 2,169; mean cumulative stress 0.216; max stress 3.92.
- **Tail driver:** in the worst-5% outcomes, *margin* (123) and *revenue* (120) channels fire well above their base rate, while funding/strategic/cash (31–42) sit at or below it. This is the V1 fragility thesis in action: for a high-margin, net-cash company, the downside transmits through **operating** shocks (demand loss, margin compression — a competitive-disruption signature), not **financial** ones. NVIDIA's worst cases are about the business being out-competed, not about it running out of money. The engine can't price the *probability* of that event, but it names the **transmission route**.

---

## 6. Market Percentile Analysis

NVIDIA traded at **~$211.93** on 15–16 June 2026 (market cap ~$5.23T).

| Reference price | Continuous CDF | Shocked CDF |
|---|---|---|
| $100 | 13.4% | 19.0% |
| $142 (≈ median) | 49.8% | — |
| $145.78 (central DCF) | 53.3% | — |
| $175 | 76.0% | 79.3% |
| $200 | 87.9% | 90.6% |
| **$211.93 (market)** | **91.3%** | **93.9%** |
| $250 | 97.2% | 97.7% |
| $300 | 99.6% | 99.3% |

On the market-friendly fixture, the market price sits at roughly the **91st percentile** of the continuous distribution and **~94th** of the shocked one — **rich, but inside the distribution**. This is the meaningful contrast with a conservative fixture: under a *defensible bull case*, the engine *can* generate intrinsic values as high as today's price (max draw $383.49), it just does so only ~9% of the time. The market is paying for the upper-decile outcome.

Read plainly: today's $211.93 is ~45% above the bull-case central value of $145.78. Closing that gap on these honest CAPM inputs requires the optimistic tail of the operating assumptions to actually land — sustained 50%+ near-term growth, margins holding near 60%, and growth fading no faster than modeled. That is the precise quantity of optimism embedded in the price.

This is a statement about the *fixture's assumptions*, not a trade recommendation.

---

## 7. Seed Robustness

Re-running continuous convergence under four engine seeds (20-batch apparatus):

| Seed | z* (cont) | cont margin |
|---|---|---|
| 42 | 3,000 | 160.4% |
| 99 | 1,500 | 25.9% |
| 123 | 1,500 | 55.6% |
| 7 | 1,500 | 65.2% |

z\* ranges 1,500–3,000 across seeds — comfortably within the 10,000 grid for every seed. The *point estimate* of the required sample size is seed-sensitive (as expected for an elbow/percentile rule on finite batches), but the *qualitative conclusion is stable*: NVIDIA's continuous stage is an easy convergence problem, resolved well below the folk number on every seed. The shocked stage (seed 42: z\*\* = 1,000 but 251 batches recommended, 9.0% margin) is the genuinely hard one — and the engine flags it as not-yet-resolved rather than papering over it.

---

## 8. Final Interpretation

On a **market-friendly, bullish-but-defensible** fixture, NVIDIA's Monte Carlo intrinsic value is a tight, entirely-positive distribution centered near **$142/share** — continuous mean $147.75, shocked mean $139.69, zero negative paths in either engine. The business is fundamentally robust: net cash, ~60% operating margins, and a 10.4-point WACC-minus-g spread mean even the shocked engine's worst path ($31.68) stays positive.

The engine resolves NVIDIA's continuous stage cheaply (160% margin, 0.02% gap to the 10,000-path answer using only 3,000 sims) and is candid that the shocked stage is not fully resolved (251 batches recommended). Its tail is driven by operating channels — margin and revenue — exactly the fragility model's prediction for a low-leverage, high-margin franchise.

The headline result is valuation: at **$211.93** the market sits at the **~91st percentile** (continuous) / **~94th** (shocked) of the engine's own distribution. Unlike a conservative fixture — under which the same price lands *above the entire distribution* — this generous-but-honest case shows the market price *is* reachable by the model, but only in its optimistic upper decile. The engine cleanly separates "what a defensible bull case supports" (~$146) from "what the market is pricing" (~$212), and quantifies exactly how much of the price is bought-forward optimism: about 45%, carried almost entirely by the growth and margin assumptions, not by any discount-rate sleight of hand.

---

*Engine applied as-is; no logic modified. Seed 42; figures from a single seeded run. Market price as of 15–16 June 2026. Beta held at NVIDIA's defensible historical level — the optimism in this case is operating, not financial.*
