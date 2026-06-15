# Amazon.com, Inc. (AMZN)
## Real-World Valuation Case Study — Monte Carlo DCF Engine

**Purpose:** A production application of the finished engine to a real, large-cap company that is mid-way through an extraordinary capital-investment cycle. No engine, convergence, N_GRID, or shock-calibration logic was modified. Amazon was chosen deliberately because its current heavy capex regime stresses the engine's 'capex as a % of revenue' assumption — exactly the fragility the DCFInputs documentation flags — making it a useful real-world test of the inputs, not the architecture.

**Base fixture:** FY2025 actuals (revenue $716.9B, net income $77.7B, D&A $41.9B, capex >$100B, long-term debt $65.7B, cash+marketable securities ~$123B, ~10.73B shares). 7-year explicit horizon, engine seed = 42 throughout.

---

## 1. Assumptions Used (DCFInputs Fixture)

| Input | Value | Rationale |
|---|---|---|
| Starting revenue | $716,900M | FY2025 actual net sales (+12% YoY) |
| Net debt | -$57,400M | Net cash: long-term debt $65.7B minus cash $86.8B and marketable securities $36.2B. Operating-lease liabilities excluded (treated as operating, not financing). |
| Shares outstanding | 10,730M | Approx. diluted share count, FY2025 |
| Forecast horizon | 7 years | Explicit-forecast window before terminal value |
| Revenue growth | 11% -> 6% | Fades from low-double-digit (AWS + ads led) toward mature large-cap single digits |
| Operating margin | 12% -> 15% | Gradual expansion as higher-margin AWS and advertising grow as a share of mix |
| Capex % revenue | 16% -> 9% | Elevated AI/datacenter buildout now (FY2025 capex >$100B; management guided ~$200B for 2026), normalising over the horizon. This is the fixture's most aggressive and most uncertain assumption. |
| D&A % revenue | 5.8% -> 7.0% | Rising as the AI-era asset base grows and server useful lives shorten |
| NWC % revenue | 0.0% flat | Conservatively neutral; Amazon historically runs negative working capital (supplier-financed), so this understates a genuine cash advantage |
| Tax rate | 15% | Near recent effective rate |
| Terminal growth | 2.5% | Long-run nominal GDP-like |
| Risk-free rate | 4.3% | Long Treasury |
| Equity risk premium | 5.5% | Standard equity premium |
| Beta | 1.30 | Above-market systematic risk; published readings ranged ~1.3-1.5, the lower end chosen as a central view |
| Cost of debt | 5.0% | High-grade issuer at current rates |
| Debt / total capital | 2.5% | Minimal financial leverage relative to ~$2.6T market cap |

> These are analyst assumptions derived from FY2025 actuals and a deliberately conservative central view - not a forecast and not investment advice. The capex trajectory in particular smooths over a near-term spike (management's ~$200B 2026 guide implies capex well above the 16% starting point); the Monte Carlo layer widens this band, but the central fixture stays conservative.

---

## 2. Deterministic Central Case

**Forecast window:** base year **FY2025** (reported actuals, not forecast); explicit forecast **FY2026–FY2032** (7 years); terminal value from FY2033 onward.

| Metric | Value |
|---|---|
| WACC | **11.270%** |
| Terminal spread (WACC − g) | 8.77% |
| **Central DCF per share** | **$96.52** |

The deterministic gate **passes** (value positive, terminal growth 2.5% < WACC 11.3%), so the full stochastic pipeline was run.

**Year-by-year assumptions (the trajectory inputs that drive the central case):**

| Year | Revenue growth | Operating margin | Capex % rev | D&A % rev | ΔNWC % rev |
|---|---|---|---|---|---|
| FY2026 | 11% | 12.0% | 16.0% | 5.8% | 0.0% |
| FY2027 | 10% | 12.5% | 15.0% | 6.0% | 0.0% |
| FY2028 | 9% | 13.0% | 14.0% | 6.2% | 0.0% |
| FY2029 | 8% | 13.5% | 12.0% | 6.4% | 0.0% |
| FY2030 | 7% | 14.0% | 11.0% | 6.6% | 0.0% |
| FY2031 | 6% | 14.5% | 10.0% | 6.8% | 0.0% |
| FY2032 | 6% | 15.0% | 9.0% | 7.0% | 0.0% |

**Resulting unlevered free-cash-flow (FCFF) trajectory, all figures in the fixture's currency units (USD millions):**

| Year | Revenue | EBIT | NOPAT | + D&A | − Capex | − ΔNWC | **FCFF** |
|---|---|---|---|---|---|---|---|
| FY2025 | $716,900 | — | — | — | — | — | — |
| FY2026 | $795,759 | $95,491 | $81,167 | $46,154 | ($127,321) | ($0) | **$0** |
| FY2027 | $875,335 | $109,417 | $93,004 | $52,520 | ($131,300) | ($0) | **$14,224** |
| FY2028 | $954,115 | $124,035 | $105,430 | $59,155 | ($133,576) | ($0) | **$31,009** |
| FY2029 | $1,030,444 | $139,110 | $118,243 | $65,948 | ($123,653) | ($0) | **$60,539** |
| FY2030 | $1,102,575 | $154,361 | $131,206 | $72,770 | ($121,283) | ($0) | **$82,693** |
| FY2031 | $1,168,730 | $169,466 | $144,046 | $79,474 | ($116,873) | ($0) | **$106,647** |
| FY2032 | $1,238,854 | $185,828 | $157,954 | $86,720 | ($111,497) | ($0) | **$133,177** |

---

## 3. Continuous Monte Carlo (z*)

**Convergence sweep (20-batch apparatus, seed 42):**

| n | Scatter | 
|---|---|
| 100 | 2.50 |
| 250 | 1.56 |
| 500 | 1.08 |
| 1,000 | 0.87 |
| 1,500 | 0.79 |
| 2,000 | 0.53 |
| 3,000 | 0.38 |
| 5,000 | 0.37 |
| 7,500 | 0.34 |
| 10,000 | 0.36 |

- z_pct (rule 2) = **1,000**, z_elbow (rule 3) = **2,000**
- **z\* = 2,000**, decision margin = **83.2%**, σ ≈ $30.08, adequately resolved = True

**Production run at z\* = 2,000:**

| Statistic | Value |
|---|---|
| Mean | $98.37 |
| Median | $95.82 |
| Std dev | $29.98 |
| Min / Max | $8.36 / $223.71 |
| Fraction negative | **0.0%** |

**Percentiles:** P5 $53.77 · P10 $62.78 · P25 $76.79 · P50 $95.82 · P75 $117.60 · P90 $138.98 · P95 $151.94.

**Benchmark vs. folk number (n = 10,000):** z\* uses **0.2×** the compute yet the mean differs by only **0.9%** ($98.37 vs $97.48). The empirically-derived sample size reproduces the folk-number answer at a fraction of the cost.

---

## 4. Shocked Monte Carlo (z**)

- z_pct = 2,000, z_elbow = 1,000 → **z\*\* = 2,000**
- decision margin = **36.2%**, batches recommended = **17** (vs 20 used), adequately resolved = True

**Production run at z\*\* = 2,000:**

| Statistic | Value |
|---|---|
| Mean | $90.86 |
| Median | $88.64 |
| Std dev | $32.48 |
| Min / Max | $-1.44 / $234.12 |
| Fraction negative | **0.1%** |

**Percentiles:** P5 $40.20 · P10 $52.04 · P25 $68.39 · P50 $88.64 · P75 $110.26 · P90 $132.14 · P95 $146.08.

Shocks shift the whole distribution down (shocked mean ~$90.9 vs continuous ~$98.4) and fatten the left tail (P5 falls from ~$53.8 to ~$40.2, min from $8.36 to slightly negative). A small fraction of shocked paths (0.05%) cross into negative intrinsic value - Amazon's thinner GAAP margins and heavy ongoing investment leave less cushion than a net-cash, high-margin software peer.

---

## 5. Shock Channel Behaviour

| | Revenue | Margin | Funding | Strategic | Cash |
|---|---|---|---|---|---|
| Fires — all paths | 448 | 417 | 436 | 415 | 453 |
| Fires — worst 5% tail | **97** | **127** | **44** | **52** | **85** |

- **Shock-free paths: 67.4%**. Total fires: 2,169; mean cumulative stress 0.216; max stress 3.92.
- In the worst-5% tail, margin (127) and revenue (97) dominate, with cash (85) also elevated, while funding and strategic sit near their base rate. The downside is an operating story - margin compression and demand loss during a heavy-investment phase - rather than a financing story, consistent with the V1 fragility thesis for a company carrying little financial debt but large fixed-investment commitments.

---

## 6. Market Percentile Analysis

Amazon.com, Inc. traded at **$246.03** on 2026-06-05.

- Continuous distribution: the market price sits above the maximum simulated value ($223.71) — beyond the ~100th percentile.
- Shocked distribution: the market price sits above the maximum simulated value ($234.12) — beyond the ~100th percentile.

The market price (~$246) sits ABOVE the entire simulated distribution under both engines - the continuous run never produces a value above ~$224, the shocked run never above ~$234. On this conservative fixture the engine literally cannot manufacture today's price: the central intrinsic value is ~$96.52, roughly 61% below market. The gap is the market's implied bet that capex converts into far higher future cash flow (AI/AWS operating leverage) and/or that margins expand faster than the fixture assumes. The model cleanly isolates 'what these conservative fundamentals support' from 'what the market is paying for the AI build-out story.'

---

## 7. Seed Robustness

| Seed | z* (cont) | cont margin | z** (shock) | shock margin |
|---|---|---|---|---|
| 42 | 2000 | 83.2% | 2000 | 36.2% |
| 99 | 3000 | 101.5% | 1500 | 3.0% |
| 123 | 1500 | 25.0% | 1500 | 61.5% |

Across seeds, z* (continuous) ranges 1,500-3,000 and z** (shocked) 1,500-2,000 - all comfortably within the 10,000 grid. As with MSFT, the point estimate of the required sample size is seed-sensitive (an elbow/percentile rule on finite batches), but the qualitative conclusion is stable: Amazon is a tractable convergence problem resolved well below the folk number on every seed. One shocked seed (99) flagged a very tight margin (3.0%) with a large batch recommendation, a reminder that the shocked stage is the harder convergence problem.

---

## 8. Final Interpretation

On a conservative FY2025-base fixture, Amazon's Monte Carlo intrinsic value is a distribution centred near $96/share - continuous mean ~$98.4, shocked mean ~$90.9 - with almost no negative paths (0.0% continuous, 0.05% shocked). The continuous stage resolves cheaply (z* = 2,000, 83% decision margin, reproducing the 10,000-path mean within 0.9% at one-fifth the compute); the shocked stage is harder (z** = 2,000, 36% margin) with an operating-channel-driven tail. The headline result is valuation: at ~$246 the market trades above the engine's entire simulated universe under both engines. The model, on these inputs, simply cannot reach today's price - the market is paying for an AI-capex-to-cash-flow conversion and margin trajectory more optimistic than this fixture encodes. As a real-world test, Amazon also illustrates the documented fragility of the capex-%-of-revenue assumption: a company spending >$100B/year on long-lived assets is precisely the case where that scaling assumption is least comfortable, and where the analyst's judgment on the capex fade does most of the work in the valuation.

---

*Engine applied as-is; no logic modified. Seed 42. Market price as of 2026-06-05.*
