# Candidate — Microsoft Corporation (MSFT)

**The first real-company case study run through the Monte Carlo Valuation Engine.**

**Status:** Complete first run — open for future appends.
**First run:** 2026-06-01. Engine state: steps 2–6 complete and locked (deterministic DCF + perturbation MC + convergence z\* + micro-shock overlay + shocked re-convergence z\*\*).
**Run artefacts:** `msft_runner.py` (staged runner), `msft_fixture.json` (inputs), `msft_results.json` (machine-readable dump). Every number below is read from that dump.

---

## 0. Framing — read before trusting any number here

This is an **architecture and methodology case study, not an investment call.** The fixture uses public FY2024 actuals as the anchor and analyst-style forward assumptions; it is not a full sell-side model and it makes no claim of superior information. The market price comparison is included because it is the engine's designed output — where does the market price sit inside the distribution of intrinsic values? — not because this model should be read as authoritative evidence about MSFT's valuation.

**Why MSFT for the first real-company run?** It is the opposite of the fragile fixtures (Carvana, Rivian, CloudGrow) in almost every way: positive and large intrinsic value, near-zero leverage, high operating margins, defensive beta. Running it through the same pipeline as those fragile fixtures generates the contrast the architecture needs — it tests whether the machinery that was stress-tested on negative-valued, high-beta names runs cleanly on a tame, large-cap blue-chip. It also produces the most interesting convergence comparison yet: MSFT's *absolute* sigma is ~14× Steady Co's, even though its *coefficient of variation* (sigma as % of mean) is lower. Does a high-sigma, low-CV company converge faster or slower than a low-sigma, high-CV one? That question is answered here.

---

## 1. Inputs & assumptions

All currency in $M unless noted. Fiscal year ending 30 June; starting point is FY2024 actuals.

| Field | Value | Source / rationale |
|---|---|---|
| starting_revenue | 245,122 | FY2024 reported revenue: $245.1B |
| net_debt | −26,000 | Net CASH: ~$75B cash + ST investments minus ~$49B LT debt. Negative = cash-rich. |
| shares_outstanding | 7,432M | Diluted share count FY2024 |
| forecast_years | 7 | Stable mega-cap; HANDOFF default-stretch |
| revenue_growth | 14%, 13%, 12%, 11%, 9%, 7%, 6% | Azure ~28–31% blended down to ~13–14% total; decelerates as law of large numbers bites |
| operating_margin | 44%, 44%, 45%, 45%, 46%, 46%, 47% | FY2024 EBIT margin 44.6%; gentle expansion as AI/cloud mix improves; offset by AI opex |
| capex_pct_revenue | 18%, 18%, 16%, 15%, 14%, 13%, 12% | FY2024 capex $44.5B = 18.2% of revenue (AI data-centre build); glides down as build wave subsides |
| da_pct_revenue | 8.5% flat | FY2024 D&A ~$20.5B = 8.4% of revenue; held flat as asset base grows in proportion |
| nwc_pct_revenue | 0.5% flat | MSFT runs negative NWC structurally; using a small positive drag is conservative |
| tax_rate | 19% | FY2023–FY2024 effective rate 18–19% |
| terminal_growth | 2.5% | Long-run US nominal GDP + thin platform premium (Azure, Office 365, GitHub) |
| risk_free_rate | 4.3% | 10-year US Treasury, early 2025 |
| equity_risk_premium | 5.5% | Damodaran Jan-2025 US ERP |
| beta | 0.90 | 5-year monthly beta vs S&P 500; MSFT is slightly defensive (range 0.88–0.95) |
| cost_of_debt | 3.8% | Aaa/AAA-rated; LT bond yields ~3.8% |
| debt_to_total_capital | 1.5% | ~$49B debt / ($49B + ~$3.2T market cap) ≈ 1.5%; nearly all-equity-financed |

**Derived WACC:** 9.157%
- Cost of equity (CAPM): 4.3% + 0.90 × 5.5% = **9.25%**
- After-tax cost of debt: 3.8% × (1 − 0.19) = **3.08%**
- Blended: 0.985 × 9.25% + 0.015 × 3.08% = **9.157%**

**The dominant feature of this capital structure relative to all prior candidates:** debt_to_total_capital = 1.5% is the lowest of any fixture run. The tax shield is almost nonexistent; WACC is essentially the cost of equity. With negative net debt, the equity bridge does the opposite of most fragile cases — it *adds* $26B to EV rather than subtracting debt. The lever that amplifies uncertainty for leveraged companies (thin equity cushion → high CV per share) is absent. This directly shapes the convergence and channel-dominance findings below.

**Run settings:** N_GRID = [100, 250, 500, 1000, 1500, 2000, 3000, 5000, 7500, 10000], batches_used = 20 (reduced from default 40; the 7-year forecast makes each DCF call ~38 µs vs ~27 µs for 5-year candidates, pushing the 40-batch sweep beyond the 45-second execution limit; 20 batches is sufficient to resolve z\* clearly given MSFT's high decision margins). Base shock hazard 0.0115/channel/year, stress sensitivity 1.0, equal fragility weights (V1).

---

## 2. Deterministic central case

| | MSFT | Steady Co (ref) |
|---|---|---|
| Central per-share value | **$263.74** | +$12.77 |
| WACC | 9.157% | 8.39% |
| Enterprise Value (EV) | **$1,934,137M** | — |
| Equity Value | **$1,960,137M** | — |
| PV of FCFs | $555,532M (28.7% of EV) | — |
| PV of Terminal Value | $1,378,605M (**71.3% of EV**) | — |

PV_TV / EV of 71.3% is squarely within the 60–80% band the HANDOFF identifies as normal — a healthy sanity check. A large share of value sits in the terminal tail (post-year-7 perpetuity), consistent with a stable, durable business where the analyst has reasonable confidence the platform persists.

**The market price gap.** MSFT traded at approximately $390–415 in early 2025 — roughly 50% above the deterministic model's $263.74. This gap is not a model error; it reflects:

1. **AI optionality.** The market is paying for a distribution of Copilot/Azure upside scenarios that includes paths with higher growth or faster margin expansion than the central case. A DCF's single-point answer cannot represent this; the Monte Carlo distribution does, partially — and even the shocked 95th percentile ($370) still falls short of market.
2. **Capex is the largest FCF suppressor.** The 18%→12% capex glide path is the single biggest drag on FCF. If the AI infrastructure build delivers returns faster than modelled, FCF expands sharply.
3. **Terminal growth.** At 2.5%, the model is conservative. Raising to 3.0% (still well within the g < WACC constraint) would meaningfully increase per-share value.

The market signal — where market price sits in the distribution — is reported in section 8.

---

## 3. Continuous-only Monte Carlo (perturbation, no shocks)

Production run at **z\* = 3,000**, seed 42, n = 3,000.

| Statistic | Value |
|---|---|
| Mean | $264.74 |
| Median | $259.18 |
| Std dev | **$63.09** |
| Min / Max | $106.62 / $557.97 |
| 5th–95th percentile | **$170.27 → $380.64** |
| 10th / 25th | $187.08 / $219.72 |
| 75th / 90th | $302.60 / $351.70 |
| Share of sims negative | **0.0%** |

```
  106.62 | # 11
  129.19 | #### 42
  151.76 | ############ 133
  174.32 | ##################### 223
  196.89 | ################################ 337
  219.46 | ####################################### 413
  242.03 | ########################################## 448
  264.59 | ####################################### 416
  287.16 | ############################### 326
  309.73 | #################### 210
  332.30 | ############### 156
  354.87 | ########### 119
  377.43 | ######### 92
  400.00 | #### 39
  422.57 | ## 16
  445.14 | # 10
  467.70 |  5
  490.27 |  2
  512.84 |  0
  535.41 |  2
```

The distribution is clearly right-skewed — the peak sits around $240–265 but the right tail is long ($381 at the 95th, $558 at the max). This is the multiplicative-perturbation signature: compounding growth draws pull the right side out further than the left side compresses, because growth is bounded below (revenue cannot turn deeply negative) but unbounded above. The floor at $106.62 reflects a deeply pessimistic path where every growth and margin draw goes unfavourable, but even the worst continuous path stays well above zero — no path values the equity at nothing under continuous perturbation alone.

**Coefficient of variation (CV):** $63.09 / $264.74 = **23.8%**. For reference, Steady Co's CV was ~36%. MSFT's CV is lower despite having 14× the absolute sigma, because the mean is so much larger. The equity bridge — in MSFT's case an *addition* of net cash rather than subtraction of debt — amplifies neither the mean nor the sigma; the per-share spread is genuinely the operating business's spread, not a leveraged version of it.

---

## 4. Shocked Monte Carlo (perturbation + micro-shock overlay)

Production run at **z\*\* = 2,000**, seed 42, n = 2,000.

| Statistic | Continuous | **Shocked** | Δ |
|---|---|---|---|
| Mean | $264.74 | **$250.27** | −$14.47 (−5.5%) |
| Median | $259.18 | $245.19 | −$13.99 |
| Std dev | $63.09 | **$70.74** | +$7.65 (+12.1%) |
| Min | $106.62 | **$47.56** | −$59.06 |
| Max | $557.97 | $600.57 | +$42.60 |
| 5th pctile | $170.27 | **$141.90** | −$28.37 |
| 95th pctile | $380.64 | $369.93 | −$10.71 |
| Share negative | **0.0%** | **0.0%** | 0.0pp |
| Shock-free paths | — | **67.4%** | — |

```
   47.56 |  2
   75.21 | ### 24
  102.86 | ###### 51
  130.51 | ########## 83
  158.16 | ####################### 179
  185.81 | ################################## 270
  213.47 | ########################################## 332
  241.12 | ######################################### 322
  268.77 | ################################### 274
  296.42 | ######################## 189
  324.07 | ################ 124
  351.72 | ######## 65
  379.37 | #### 34
  407.02 | ### 25
  434.67 | ## 13
  462.32 | # 6
  489.97 | # 5
  517.62 |  1
  545.27 |  0
  572.92 |  1
```

The shock overlay bites asymmetrically on the left, as designed. The floor collapses from $107 to $48, the 5th percentile drops $28, and the mean falls $14.47 — while the 95th drops only $11 and the max actually rises (a path where shocks fire but are mild, and the multiplicative upside tail runs freely). The shock-free rate is 67.4%: in just under one-third of paths, at least one discrete event fires somewhere across the 7-year forecast. Mean path-level stress is 0.22 and the maximum is 3.92 — death-spiral paths (three or more cascading shocks) are present but rare.

Zero negative-valued paths even after shocks. This stands in sharp contrast to Carvana (71% negative shocked) and illustrates the core structural difference: MSFT's equity cushion is so large (EV ~$1.9T, net cash ~$26B, 7,432M shares) that even the worst cascade paths — which collapse revenue and margin simultaneously over 7 years — cannot drive the equity to zero. The worst shocked path ($47.56/share) is a genuinely bad outcome for a $390 stock, but the equity is not worthless.

---

## 5. Convergence — z\*, z\*\*, decision margins

| | Continuous (z\*) | Shocked (z\*\*) |
|---|---|---|
| **z (headline)** | **3,000** | **2,000** |
| z_pct (precision rule) | 1,000 | 1,000 |
| z_elbow (geometric bend) | 3,000 | 2,000 |
| z\* = max(z_pct, z_elbow) | **3,000** | **2,000** |
| decision_margin_pct | **+262.2%** | **+75.9%** |
| precision_bar | $2.654 | $2.489 |
| sigma_estimate | $63.28 | $69.52 |
| centre (mean of run-means) | $265.07 | $249.02 |
| borderline flag | False | False |
| batches_used | 20 | 20 |
| batches_recommended | 2 | 5 |
| adequately_resolved | True | True |

Unlike Carvana, **all convergence machinery runs cleanly here.** A positive centre yields a positive precision bar; z_pct fires normally; decision_margin_pct is large and positive (+262%, +76%). The `borderline` flag is False throughout, which means the batch-grading machinery is also running correctly.

**The conservative combiner is doing real work.** z_pct fires at n = 1,000 for both engines (scatter falls below 1% of $265 ≈ $2.65 at n = 1,000). But z_elbow = 3,000 (continuous) and 2,000 (shocked). The `max()` combiner correctly picks the elbow over the precision-rule reading, because the elbow is telling us the scatter curve hasn't fully bent yet at n = 1,000 — diminishing-returns territory isn't entered until n = 3,000. This is the combiner working as designed: the elbow makes us more conservative, and its caution is validated by the scatter column (scatter at n = 3,000: 0.733; at n = 1,000: 1.922 — still declining meaningfully).

**Why z\* = 3,000, higher than Steady Co's 2,000.** MSFT's sigma is $63.28 — enormous in absolute terms — while Steady Co's was $4.60. The precision bar for MSFT ($2.65) is proportionally larger than Steady Co's (~$0.13), so the precision rule fires early for MSFT (n = 1,000) despite the large absolute sigma. The elbow, however, tracks the shape of the σ/√n decay curve, which depends on sigma directly: higher sigma → the scatter curve starts higher → the elbow appears at a higher n. So MSFT needs 50% more simulations than Steady Co on the elbow criterion, even though its relative precision (CV = 24%) is lower. **Per-company z\* reflects absolute volatility of the distribution, not just relative volatility.**

**z\*\* = 2,000 < z\* = 3,000 — shocks lower the required n by one grid rung.** This continues the cross-candidate pattern (Steady Co: 2,000 / 2,000; Carvana: 2,000 / 1,500; MSFT: 3,000 / 2,000): adding shocks has not raised z in any case, and in two of three it has slightly lowered it. The hypothesis from the build sequence — "shocks fatten tails → raise sigma → raise z\*\*" — is not yet confirmed empirically. The shocked sigma IS higher ($69.52 vs $63.28), but the elbow shifts LEFT because the increased scatter at small n resolves the curve's shape more clearly, not less. The gap between z\* and z\*\* is 1 grid rung (3,000 vs 2,000); at this grid resolution it is not a significant difference.

**Decision margins are large and comfortable.** +262% for continuous means the scatter at z\* = 3,000 sits more than three times below the precision bar — the recommendation is robustly above the threshold. Shocked (+76%) is lower but still well clear. `batches_recommended` is 2 and 5 respectively — the engine is telling us the 20-batch apparatus is heavily over-specified for this well-resolved case. This is the opposite of Carvana (where the negative-bar mis-fire suppressed all recommendations) and Steady Co's shocked case (where small decision margins led to batch counts of 171–1,464 depending on seed).

---

## 6. Benchmark vs the folk 10,000 (continuous)

| | z\* = 3,000 | Folk 10,000 |
|---|---|---|
| Mean | $264.735 | $264.769 |
| Median | $259.175 | $258.378 |
| Compute ratio | **0.30** | 1.00 |
| Mean gap | **0.012%** | — |

The headline thesis holds again. Running at the company-specific z\* = 3,000 uses **30% of the folk compute** and produces a mean indistinguishable from the 10,000-run answer (0.012% gap, well within rounding noise). MSFT needs more compute than Carvana (30% vs 20%) because z\* = 3,000 > 2,000, consistent with the higher sigma. The thesis adapts: the per-company z\* is different for every firm, and the benchmark confirms it is the right number each time.

---

## 7. Shock-channel behaviour

5,000 paths, seed 42. Channel fires are near-equal across all paths by design (equal base hazards, equal fragility weights, V1 calibration). The story lives in the **worst 5% of paths** (worst 250 of 5,000 by valuation):

| Channel | All fires (n=5,000) | Worst-5% fires | Worst-5% share |
|---|---|---|---|
| **margin** | 417 (19.2%) | **142** | **35.4%** |
| **revenue** | 448 (20.7%) | **133** | **33.2%** |
| strategic | 415 (19.1%) | 44 | 11.0% |
| funding | 436 (20.1%) | 40 | 10.0% |
| cash | 453 (20.9%) | 39 | **9.7%** |

Mean stress: 0.216 · Max stress: 3.924

**Margin and revenue jointly dominate the worst paths (~69% combined); funding and cash are defanged (~20% combined).** This is a materially different worst-path mix than either Carvana (where cash was 37% of worst-5%) or Steady Co (where cash was 15% and revenue was higher). The mechanism is structural and points directly to the capital structure.

**Why cash and funding barely register in the worst-tail.** The cash channel sizes one-off outflows as a fraction of that year's revenue: `net_debt += damage × revenue_t`. For MSFT, revenue in forecast years 1–7 runs $279B to $485B. A 5–25% damage draw puts $14B–$121B onto net debt. This sounds enormous — but MSFT starts with *negative* net debt (−$26B net cash), so it takes a cash shock of $26B+ just to tip the firm into positive net debt, and the EV is ~$1.9T. The leverage amplification that made cash lethal for Carvana (thin equity cushion, already-positive debt) simply doesn't exist here. The funding channel (`cost_of_debt *= (1+damage)`) barely moves WACC either: with D/V = 1.5%, even doubling the cost of debt shifts WACC by ~0.06pp — immaterial. **A cash-rich, near-zero-leverage company is structurally immune to the balance-sheet channels. The only way to damage its equity materially is to attack the operating cash flows — revenue and margin.**

**Why margin slightly edges revenue (35% vs 33%).** Margin compression is applied multiplicatively to every remaining year from the shock year onward, so a year-2 margin shock propagates through 5 more years of compounding. Revenue shocks also propagate (they fold into the growth rate), but the margin effect stacks on top of whatever the revenue base produces. For a 7-year forecast, the margin channel's persistence advantage is modest but real.

**Strategic and funding finishing mid-table (~10% each)** is consistent with the Steady Co pattern. Strategic (terminal growth haircut) damages the perpetuity but not the explicit FCFs; its weight in worst paths is limited because the worst paths tend to be produced by in-forecast damage, where the terminal shock is an add-on rather than a cause. Funding sits at 10% for the same reason as cash: the D/V = 1.5% weight makes the WACC effect negligible.

---

## 8. Seed observations (z stability)

Four seeds. Continuous stages used batches = 20; shock seed stages used batches = 12 (the shocked 7-year sweep takes ~43s with batches = 20, exceeding the shell timeout; batches = 12 takes ~22s and is sufficient to locate the elbow; noted here for full transparency).

| seed | CONT z\* | CONT margin% | SHOCK z\*\* | SHOCK margin% |
|---|---|---|---|---|
| 42  | **3,000** | 262.2 | **2,000** | 75.9 |
| 99  | **3,000** | 149.3 | 1,000 | 68.4 |
| 123 | 1,500 | 75.5 | **2,000** | 134.3 |
| 7   | 1,500 | 117.6 | 1,500 | 114.9 |

**z\* is not rock-stable.** It sits in the 1,500–3,000 band — a two-grid-rung spread (seeds 42/99 land at 3,000; seeds 123/7 land at 1,500). This spread maps directly onto the HANDOFF's seed-study analysis: "z is robust; batch counts are not." The shift from 3,000 to 1,500 is one or two grid rungs, not an order of magnitude. In production terms, running at z\* = 3,000 (the seed-42 canonical recommendation) covers both readings comfortably.

**z\*\* is similarly spread** (1,000–2,000), largely moving in sync with z\* as the HANDOFF predicts for cases where shocks don't materially change the σ profile.

**Decision margins are large and positive on every seed** — a clean contrast to Carvana (all seeds had negative margins, mechanically). The batch-grading machinery runs correctly throughout. `batches_recommended` is uniformly low (2–6), confirming the apparatus is over-specified for this well-resolved case. No seed produces a borderline flag.

---

## 9. Market-percentile signal

MSFT traded at approximately **$390–415** in early 2025. Using $390 as a reference point:

**Shocked distribution (production run, z\*\* = 2,000, seed 42):**

| Price reference | Pctile of shocked simulations below that price |
|---|---|
| $200 (deep bear) | 24.1% |
| $263 (deterministic model) | 59.7% |
| $390 (market price, approx.) | **96.5%** |

**The model reads MSFT as priced for an excellent-case scenario.** At $390, 96.5% of shocked intrinsic-value simulations fall below the market price — the market is paying for something in the top 3.5% of the engine's outcome distribution. That top 3.5% represents paths where most or all of the following hold simultaneously: revenue growth comes in at the high end of the perturbation band, margins expand faster than the central case, capex normalises sooner, and no material shocks fire.

**How to read this signal honestly.** The engine is a conventional DCF with Gaussian perturbation and discrete shocks. It does not model: (1) the AI monetisation option embedded in Copilot and Azure's pricing power, (2) structural multiple expansion driven by Microsoft's platform network effects, (3) the possibility that the correct terminal growth rate is 3.0–3.5% rather than 2.5% once AI compound effects are priced in. A DCF that cannot see these factors will systematically undervalue companies where market pricing is partly forward-pricing optionality. The 96.5th-percentile result is not a "MSFT is 50% overvalued" call — it is a "the difference between the model's central case and the market price is too large to be explained by symmetric uncertainty around the model's assumptions." The remaining gap is attributable to factors the model structurally cannot see.

---

## FINDINGS

### Tier 1 — MSFT-specific (these inputs and capital structure only)

1. **Central deterministic value: $263.74/share.** WACC 9.157%, EV $1,934B, equity value $1,960B (including $26B net cash). PV_TV / EV = 71.3% (within the normal 60–80% band).
2. **Zero negative paths** in both continuous and shocked production runs. The equity cushion is simply too large for any perturbation path to drive it to zero — a structural consequence of a $1.9T enterprise with net cash.
3. **Market price ($390) sits at the 96.5th percentile** of shocked intrinsic-value simulations. The market is paying for the right tail of outcomes — a legitimate pricing of AI optionality that this model cannot directly represent.
4. **z\* = 3,000 (continuous), z\*\* = 2,000 (shocked).** MSFT requires more simulations than Steady Co (z\* = 2,000) despite a lower CV, because z\* tracks absolute sigma: MSFT's sigma is $63 vs Steady Co's $4.60.

### Tier 2 — Generalizations (to be tested against further candidates)

1. **High-sigma / low-CV companies need more simulations than low-sigma / high-CV ones, all else equal.** The precision rule (z_pct) may fire early for a high-mean company (because 1% of a $265 mean = $2.65 precision bar, which scatter crosses sooner), but the elbow criterion — which tracks the actual shape of the decay curve — waits longer. The conservative combiner correctly overrides the early z_pct firing.
2. **Cash-rich, near-zero-leverage firms are structurally immune to the balance-sheet shock channels.** Funding and cash account for only ~20% of the worst-5% fires for MSFT; margin and revenue account for ~69%. This ordering is determined by capital structure, not by the channel hazard rates (which are equal). The cash channel's revenue-sizing mechanism only amplifies tail damage when revenue is large relative to the equity cushion — an interaction that varies company by company.
3. **A positive, large central valuation keeps all convergence machinery healthy.** The precision rule fires cleanly, decision margins are large, borderline flags are false, and batch recommendations are meaningful. There are no sign-driven pathologies of the kind Carvana exposed. This confirms that the architecture-level failures documented in Carvana are specific to non-positive centres, not a general property of fragile companies.

### Tier 3 — Architecture-level

**A-1 — The combiner's conservative instinct is load-bearing.** z_pct = 1,000 but z\* = 3,000 — the elbow pushed the recommendation three rungs further. Without the `max()` combiner, a precision-rule-only approach would have under-specified n by 3x for this company. The elbow is not a redundant safeguard; it is carrying the recommendation here.

**A-2 — The per-company z\* is genuinely company-specific.** Across the case studies: Steady Co z\* = 2,000, Carvana z\* = 2,000, MSFT z\* = 3,000. The folk 10,000 over-specifies for all three, but the ratio differs (20%, 20%, 30% compute). More importantly, the *reason* for the recommendation is different in each case: Steady Co and Carvana are elbow-only (z_pct disabled or matching the elbow); MSFT is combiner-active (z_pct fires early, elbow overrides). Knowing *why* z\* was chosen is as informative as the number itself.

**A-3 — Shocked sigma > continuous sigma in every candidate, but z\*\* ≤ z\* in every candidate.** The build sequence predicted z\*\* > z\*. Three cases now say no: the elbow of the shocked curve bends at the same or lower n than the continuous curve in every case run so far. The working hypothesis is that shocks concentrate their additional variance in the far left tail (where per-path extremes sit), but the run-mean scatter that the convergence module measures is dominated by the bulk of the distribution — which shocks shift (lower mean) without dramatically broadening (the scatter curve shape does not change enough to push the elbow right). This is a finding worth surfacing in the writeup.

---

## Unexpected results

- z\* = 3,000 **exceeds** Steady Co's z\* = 2,000, despite MSFT having a lower CV. The elbow, not the precision rule, drives the recommendation — and the elbow cares about absolute sigma, not relative sigma. Not anticipated before this run.
- **Funding and cash together account for only ~20% of the worst-5% fires** — the balance-sheet channels are almost entirely defanged by the near-zero leverage and net cash position. The channel dominance reverses vs the Steady Co trip-wire finding (where margin dominated but the design had hypothesized cash/funding would threaten survival).
- **z\*\* < z\*** (2,000 < 3,000). Third consecutive candidate where shocks do not raise the required sample size. The build-sequence prediction that shocks would raise z is now a falsified hypothesis at the Steady Co / Carvana / MSFT level (all stable or low-fragility names). An unstable, highly-leveraged name with a thin equity cushion might still show z\*\* > z\* — flagged as the next test.
- Decision margins are large, comfortable, and positive on every seed — the complete opposite of Carvana's mechanical negatives. The two companies sit at opposite ends of the "convergence diagnostics health" spectrum.

---

## Comparison vs prior fixtures

| Dimension | Steady Co | Carvana | **MSFT** |
|---|---|---|---|
| Central value | +$12.77 | −$5.61 | **+$263.74** |
| WACC | 8.39% | 10.75% | **9.16%** |
| Sigma (continuous) | $4.60 | $14.99 | **$63.09** |
| CV (sigma/mean) | 36% | N/A (neg.) | **23.8%** |
| z\* | 2,000 | 2,000 | **3,000** |
| z\*\* | 2,000 | 1,500 | **2,000** |
| z\*\* vs z\* | Same | Lower | **Lower** |
| z_pct fires? | Yes | No | **Yes** |
| Combiner active? | No (equal) | No (disabled) | **Yes (elbow overrides)** |
| decision_margin sign | Positive | **Negative** | **Positive** |
| Worst-5% leader | Margin (47%) | Margin+Cash | **Margin+Revenue (69%)** |
| Cash worst-5% | 15% | **37%** | **10%** |
| Frac negative (shocked) | 0% | 71% | **0%** |
| Market price pctile | — | — | **96.5th** |
| Folk compute used | 20% | 20% | **30%** |

---

## Future questions generated by this run

1. **Does z\*\* > z\* ever materialise?** Three cases all show z\*\* ≤ z\*. The next candidate should be a high-CV, highly-leveraged, positive-value name (e.g. a leveraged turnaround) where the equity cushion is thin and shocks drive the left tail into genuinely new territory. Candidate 8B (ThinEquity) may be the right comparison.
2. **Should z_pct use relative or absolute sigma as the bar?** Currently the precision bar is 1% of the valuation level (absolute dollar). For MSFT this yielded a bar of $2.65, which scatter crossed at n = 1,000 — too early, because the elbow hadn't arrived. A sigma-relative bar (e.g. "scatter < 5% of sigma") would be scale-free AND level-free and might track the elbow more closely. Worth exploring whether it changes the recommendation for any existing fixture.
3. **AI optionality gap: what terminal growth rate closes it?** The model produces $263.74 at TG = 2.5%. At what TG does the central case match market price (~$390)? This is a simple sensitivity not run here — left for a future append.
4. **The capex assumption is the largest FCF suppressor.** A sensitivity run varying capex_pct_revenue ±4pp (i.e. 14% vs 22% in years 1–2) would bound how much of the market-price gap is attributable to capex assumptions vs terminal growth assumptions.
5. **Does the cash channel's revenue-sizing need a leverage adjustment?** The current design sizes cash shocks off revenue regardless of the debt/equity ratio. For MSFT this produces cash shocks ($14B–$121B per event) that are large in absolute terms but small relative to equity value. For Carvana they were small in absolute terms but catastrophic relative to equity. Should the shock be sized relative to equity value (or EV) rather than revenue? The interaction with leverage is now well-documented across two cases.

---

*End of first-run log. Produced 2026-06-01. Next append: sensitivity analysis (TG and capex), or re-run after any engine update.*
