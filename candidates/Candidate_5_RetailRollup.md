# Candidate #5 — RetailRollup

**A permanent research log for the fifth fragile-company case study run through the Monte Carlo Valuation Engine.**

**Classification:** Positive-Centre Fragile Company — Full Pipeline Run
**Status:** Complete / living document. Append, don't overwrite.
**First run:** 2026-06-01. Engine state: steps 2–6 complete and locked (deterministic DCF + perturbation MC + convergence z\* + micro-shock overlay + shocked re-convergence z\*\*).
**Run artefacts:** `case_study_runner.py` (staged runner), `candidate5_results.json` (machine-readable dump). Every number below is read from that dump.

---

## 0. Framing and experimental purpose — read before trusting any number here

RetailRollup is a **fixture for architecture exploration, not an investment recommendation.** This is a synthetic company. Nothing here is a view on any real entity.

**Why Candidate #5 exists and what question it is designed to answer.**

Two positive-centre fragile companies are now in the register: CloudGrow (central +$5.58, WACC 12.535%, beta 1.9) and MedTechX (central +$6.20, WACC 14.98%, beta 2.4). Both showed the channel ordering margin > cash > revenue > strategic > funding. Cash prominence has tracked the revenue/equity ratio (CloudGrow ~1.1×: cash 25%; MedTechX ~1.6×: cash 32%), but cash has never overtaken margin. The open question from both prior runs:

**Primary architecture question: Can a positive-centre fragile company be pushed to cash-channel dominance in the worst 5% of paths?**

The tracker's design note for Candidate #5 specified: push the revenue/equity ratio further than CloudGrow or MedTechX — heavy per-share revenue on a thin share count — and test whether the capital-structure predictor (F4) ultimately flips the worst-path ordering.

RetailRollup's design achieves this:
- Starting revenue $18,000M is 6× CloudGrow and 4.5× MedTechX
- 250M shares outstanding (thinner than CloudGrow's 500M or MedTechX's 400M)
- $2,500M net debt ($10/share) — modest relative to revenue, but meaningful
- Beta 2.2, WACC 12.845% (between CloudGrow and MedTechX in discount rate)
- Margins thin but ramping (9%→13%), growth decelerating (12%→4%)

**Revenue/equity ratio:**
- Starting revenue: $18,000M
- Central equity: $26.16 × 250M shares = $6,540M
- Ratio: 18,000 / 6,540 ≈ **2.75×** (vs CloudGrow 1.08×, MedTechX 1.61×)

**Secondary questions:**
1. Does z\*\* continue to exceed z\* and grow with sigma?
2. Does F8 hold on a third positive-centre fixture?
3. Does z\*\* continue to grow as beta/sigma rises across fixtures?
4. Does any new positive-centre convergence behaviour emerge at this scale?
5. Does the revenue/equity-ratio predictor remain a clean monotone relationship?

**Pre-run boundary check.** Deterministic DCF run first. Central value = **+$26.16/share**. Gate passed. Full pipeline proceeds.

The governing discipline is the same as every prior candidate: **RetailRollup outputs are not architecture truths.** Findings are filed under candidate-specific, fragile-company-class, or architecture-level tiers, and a finding is only promoted to architecture-level once it reproduces across ≥2 fixtures.

---

## 1. Inputs & assumptions

| Field | Value |
|---|---|
| starting_revenue | 18,000 |
| net_debt | 2,500 |
| shares_outstanding | 250 |
| forecast_years | 5 |
| revenue_growth | 12%, 10%, 8%, 6%, 4% (decelerating, moderate) |
| operating_margin | 9%, 10%, 11%, 12%, 13% (ramping from thin base) |
| capex_pct_revenue | 6%, 6%, 5%, 5%, 5% (declining) |
| da_pct_revenue | 3% flat |
| nwc_pct_revenue | 3% flat |
| tax_rate | 25% |
| terminal_growth | 2.5% |
| risk_free_rate | 4% |
| equity_risk_premium | 5.5% |
| beta | **2.2** |
| cost_of_debt | 7.0% |
| debt_to_total_capital | 30% |

**Derived WACC:**
- Equity weight = 70%; equity cost = 4% + 2.2 × 5.5% = **16.1%**
- After-tax debt cost = 7.0% × 0.75 = **5.25%**
- WACC = 0.70 × 16.1% + 0.30 × 5.25% = 11.27% + 1.575% = **12.845%**

**What makes this fixture distinctive.** Two design choices are doing the real work:

1. **Revenue scale ($18bn) on a thin share count (250M).** This produces the highest revenue/equity ratio (~2.75×) of any positive-centre fixture. A cash shock of 5–25% of year-t revenue, divided by 250M shares, delivers $3.60–$18/share in one-off damage — substantial relative to the $26 central value but not crushing because the central is large. The scale amplifies every channel's per-share damage, not just cash.

2. **Margins are deliberately thin-but-growing (9%→13%).** With $18-25bn revenue, even a 9% margin produces $1.6bn NOPAT in year 1. Margin compression is therefore equally large in absolute dollar terms. Both channels are operating at scale simultaneously.

**Capex note:** capex (5-6%) consistently exceeds D&A (3%), so the net-investment drag is real — FCF is below NOPAT every year. This is typical of a retail rollup still growing its asset base.

**Convergence/run settings:** Same standard: `N_GRID = [100, 250, 500, 1000, 1500, 2000, 3000, 5000, 7500, 10000]`, `BATCHES_PER_N = 40`, base shock hazard 0.0115/channel/year, stress sensitivity 1.0, equal fragility weights (V1). Convergence seeded by default (42); `rerun=False` on all passes.

---

## 2. Deterministic central case

| | RetailRollup | MedTechX (ref) | CloudGrow (ref) | Steady Co (ref) |
|---|---|---|---|---|
| Central per-share | **+$26.16** | +$6.20 | +$5.58 | +$12.77 |
| WACC | **12.845%** | 14.98% | 12.535% | 8.16% |
| Net debt/share | **$10.00** | $0.75 | $1.00 | $3.00 |
| Beta | **2.2** | 2.4 | 1.9 | 1.1 |

RetailRollup's central value (+$26.16) is by far the highest of any fragile candidate — more than 4× CloudGrow and MedTechX. The mechanism: strong revenue ramp from a $18bn base generates substantial FCFs throughout the explicit period, and the terminal value at 2.5% growth remains large enough after the 12.845% WACC discount to produce healthy per-share equity once the $2,500M net debt is deducted ($10/share on 250M shares).

Despite beta 2.2 and a WACC of 12.845%, the fixture is comfortable enough that the central valuation is well above zero. The margin ramp from 9% to 13% on revenues that grow from $18bn to ~$23bn over five years produces FCFs that compound significantly. The positive centre is robust, not "borderline healthy" like CloudGrow ($5.58).

**Year-by-year FCF sketch (approximate):**

| Year | Revenue ($M) | Margin | NOPAT ($M) | D&A ($M) | Capex ($M) | ΔNWC ($M) | FCF ($M) |
|------|-------------|--------|-----------|---------|-----------|----------|---------|
| 1 | 20,160 | 9% | 1,361 | 605 | 1,210 | 65 | ~691 |
| 2 | 22,176 | 10% | 1,663 | 665 | 1,331 | 60 | ~937 |
| 3 | 23,950 | 11% | 1,977 | 719 | 1,197 | 53 | ~1,446 |
| 4 | 25,387 | 12% | 2,288 | 762 | 1,269 | 44 | ~1,737 |
| 5 | 26,402 | 13% | 2,580 | 792 | 1,320 | 31 | ~2,021 |

FCFs rise sharply from ~$691M in year 1 to ~$2,021M in year 5. Terminal value (year-5 FCF scaled by Gordon multiple 1/0.10345 ≈ 9.67× at WACC–g = 12.845%–2.5%) carries the bulk of enterprise value. The equity bridge is comfortable: large EV minus $2.5bn net debt, divided by 250M shares, gives a high per-share intrinsic value.

**Gate confirmed. Full pipeline proceeds.**

---

## 3. Continuous-only Monte Carlo (perturbation, no shocks)

Production run at z\* = 3,000, seed 42, n = 3,000.

| Statistic | Value |
|---|---|
| Mean | **+$26.97** |
| Median | **+$25.94** |
| Std dev | **$14.94** |
| Min / Max | −$15.82 / +$100.07 |
| 5th–95th pctile | **+$4.49 → +$53.17** |
| 10th / 25th | +$9.26 / +$16.83 |
| 75th / 90th | +$35.62 / +$46.86 |
| Share of sims **negative** | **2.63%** |

```
  -15.82 | # 6
  -10.03 | ## 25
   -4.23 | ###### 69
    1.56 | ########### 131
    7.35 | ####################### 274
   13.15 | ################################### 410
   18.94 | ########################################## 485
   24.74 | ########################################## 490
   30.53 | ################################## 400
   36.33 | ##################### 248
   42.12 | ################# 194
   47.92 | ########### 127
   53.71 | ###### 69
   59.51 | ### 36
   65.30 | ## 20
   71.10 |  5
   76.89 | # 6
   82.68 |  2
   88.48 |  2
   94.27 |  1
```

**Three notable features relative to prior candidates:**

**First, the distribution is wide.** Std = $14.94 is by far the largest of any positive-centre fixture (MedTechX: $3.01; CloudGrow: $2.13). The 5th–95th band spans $4.49 to $53.17 — a $48.68 range. This is a direct consequence of the large revenue base interacting with the 12% trajectory perturbation width: a 12% perturbation on $18bn revenue produces per-share swings an order of magnitude larger than on CloudGrow's $3bn base. The volatility is structural, not aberrant.

**Second, 2.63% of continuous paths are already negative** — more than MedTechX's 0.4% and far above CloudGrow's 0.0%. This happens despite a central value of +$26.16: the distribution is wide enough that the left tail reaches well below zero even without shocks. This means the zero boundary is not exclusively a shock phenomenon for large-revenue high-beta companies.

**Third, the right tail is long.** Maximum of $100.07/share, P90 = $46.86, P95 = $53.17. The multiplicative perturbation + DCF convexity asymmetry is clearly visible: upward draws compound through the terminal value and produce very high per-share outcomes; downward draws are partially absorbed by the positive central value floor. This is the most pronounced right-skew of any fixture.

**Sigma comparison across positive-centre fixtures:**

| Fixture | Beta | WACC | Rev ($M) | Cont std | z\* |
|---|---|---|---|---|---|
| CloudGrow | 1.9 | 12.535% | 3,000 | $2.13 | 2,000 |
| MedTechX | 2.4 | 14.98% | 4,000 | $3.01 | 3,000 |
| **RetailRollup** | **2.2** | **12.845%** | **18,000** | **$14.94** | **3,000** |

The jump from $3.01 (MedTechX) to $14.94 (RetailRollup) is not a beta effect — RetailRollup's beta (2.2) is actually lower than MedTechX's (2.4). It is almost entirely a **revenue-scale effect**: the perturbation machinery applies the same relative widths (~12% trajectory, ~4% per-year) to a revenue base that is 4.5× larger, producing per-share dollar swings that are proportionally larger because the share count is thin.

---

## 4. Shocked Monte Carlo (perturbation + micro-shock overlay)

Production run at z\*\* = 7,500, seed 42, n = 7,500.

| Statistic | Continuous | **Shocked** | Δ |
|---|---|---|---|
| Mean | +$26.97 | **+$23.29** | −$3.68 |
| Median | +$25.94 | +$22.95 | −$2.99 |
| Std dev | $14.94 | **$16.21** | +$1.27 |
| Min | −$15.82 | **−$61.53** | −$45.71 |
| Max | +$100.07 | +$106.13 | — |
| 5th pctile | +$4.49 | **−$3.03** | −$7.52 |
| 95th pctile | +$53.17 | +$50.74 | −$2.43 |
| Share negative | 2.63% | **6.76%** | +4.13pp |
| Shock-free paths | — | **75.4%** | — |

```
  -61.53 |  1
  -53.15 |  0
  -44.76 |  4
  -36.38 |  5
  -28.00 | # 33
  -19.61 | ## 86
  -11.23 | ####### 252
   -2.85 | ############# 509
    5.53 | ############################# 1127
   13.92 | ########################################## 1615
   22.30 | ########################################## 1610
   30.68 | ############################## 1140
   39.06 | ############### 579
   47.45 | ######## 315
   55.83 | #### 152
   64.21 | # 49
   72.60 |  14
   80.98 |  6
   89.36 |  2
   97.74 |  1
```

**Three observations stand out.**

**First, the shocked floor collapses dramatically.** Min goes from −$15.82 (continuous) to −$61.53 (shocked) — a $45.71 extension. This is by far the largest floor extension of any candidate (Carvana: ~$36; Rivian: ~$2.40; CloudGrow: $3.48; MedTechX: $5.49). The shocked worst paths reach deep negative territory because cascading shocks on a $18-25bn revenue base, applied to 250M shares, deliver enormous per-share damage. The fat left tail is extreme.

**Second, the P5 crosses zero.** Continuous P5 = +$4.49; shocked P5 = −$3.03. This is the first positive-centre fixture where the 5th percentile is negative. Even with a $26 central value, 5% of shocked paths sit below zero. Shocks alone extend the tail far enough to put the bottom decile firmly in loss territory. This underscores the "positive-centre fragile" classification — the central case is healthy, but the worst paths are genuinely severe.

**Third, the mean shock shift (−$3.68) is the largest of any positive-centre fixture.** Compare: CloudGrow −$0.47, MedTechX −$0.70. The large revenue base means each shock fires at scale, so even the shock-on mean (which averages shock-free paths with hit paths) shows a substantial downward shift. The engine is correctly amplifying shock damage in proportion to the revenue/share-count ratio.

Mean accumulated stress 0.153, max stress 3.12 — identical to all prior fixtures. Stress mechanics invariant to company characteristics, as designed.

---

## 5. Convergence — z\*, z\*\*, decision margins

### 5a. Headline (seed 42)

| | Continuous (z\*) | Shocked (z\*\*) |
|---|---|---|
| **z (headline, seed 42)** | **3,000** | **7,500** |
| **z_pct (precision rule)** | **3,000 ✓** | **7,500 ✓** |
| z_elbow | 2,000 | 2,000 |
| **z\* = max(z_pct, z_elbow)** | **3,000 (precision binds)** | **7,500 (precision binds)** |
| **decision_margin_pct** | **+6.15%** | **+3.25%** |
| precision_bar | +$0.267 | +$0.235 |
| centre (mean of run-means) | +$26.68 | +$23.44 |
| sigma_estimate | $14.96 | $16.33 |
| **borderline flag** | **False** | **True** |
| **batches_recommended** | **530** | **1,891** |
| adequately_resolved | False | True |

**Reading each row:**

**z_pct fires in both passes.** z_pct = 3,000 (continuous) and z_pct = 7,500 (shocked). Both bars are positive. The precision rule is fully operational — consistent with both prior positive-centre fixtures and in contrast to the negative-centre pathology (B1/B2).

**z\*\* = 7,500 > z\* = 3,000.** This is the largest z\*\*−z\* gap of any candidate. Two rungs of the N_GRID separate the continuous and shocked requirements (3,000 → 7,500, skipping 5,000). The mechanism is identical to MedTechX but stronger: shocks widen sigma from $14.96 to $16.33, which is enough to prevent z_pct from clearing the bar at n=3,000 or n=5,000 on the shocked engine. The precision rule correctly detects the additional convergence burden and responds by requiring more paths.

The elbow does NOT move (z_elbow = 2,000 in both passes). The max() combiner picks z_pct on both passes, and the gap between z_pct and z_elbow grows larger under shocks. This reinforces the pattern: the precision rule is the active driver for positive-centre companies; the elbow stays at a lower, stable rung.

**Continuous decision_margin_pct: +6.15%.** Thin but positive. This is the thinnest seed-42 continuous margin of any positive-centre fixture (CloudGrow: +21.4%; MedTechX: +20.4%). The wide sigma ($14.96) makes the scatter harder to keep below the precision bar, even at n=3,000. The bar in dollar terms ($0.267) is actually the largest of any fixture — it scales with centre value ($26.68 × 1%) — but the scatter at 3,000 barely clears it.

**Shocked decision_margin_pct: +3.25%.** Thin, genuinely borderline. `borderline = True` (correct — this is real marginal territory, not a mis-fire). The shocked margin is thin for the same structural reason as CloudGrow (shocked sigma wider → scatter harder to clear the bar), and the magnitude (3.25%) is comparable to CloudGrow's seed-42 shocked margin (3.3%).

**Batch recommendations: 530 (continuous), 1,891 (shocked).** The continuous recommendation of 530 is the largest of any positive-centre fixture (CloudGrow: 45; MedTechX: 50 at seed 42) — a consequence of the 6.15% thin continuous margin, which already sits near borderline territory. The 1/margin² amplification produces 530 on the continuous pass here, even though borderline is False. The shocked recommendation (1,891) is in the same ballpark as MedTechX seed 42 (122) and CloudGrow seed 42 (1,799), but reflects the genuinely thin shocked margin at this fixture's scale.

**adequately_resolved (shock): True.** When borderline=True, this reads "the precision bar is at the boundary — no further refinement will give a crisp verdict." Honest, not false comfort — the same correct behaviour as CloudGrow's shocked borderline.

### 5b. Benchmark vs folk 10,000 (continuous)

| | z\* = 3,000 | Folk 10,000 |
|---|---|---|
| Mean | +$26.972 | +$26.724 |
| Median | +$25.944 | +$25.656 |
| Compute ratio | **0.30** | 1.00 |
| Mean gap | **0.93%** | — |

**The benchmark thesis holds on a fifth candidate.** z\* = 3,000 reproduces the folk-10,000 mean to within 0.93% at 30% of the compute budget. This is the largest benchmark gap of any positive-centre fixture (CloudGrow: 0.12%; MedTechX: 0.68%) — unsurprising given the widest sigma, which means more natural variation between any two production runs. Nevertheless, it remains below 1%, the same practical precision threshold. The thesis is confirmed: company-specific z\* finds the right answer without the full folk budget.

The 0.93% gap is worth noting: as sigma grows (here $14.94), even a matched seed produces more natural run-to-run spread, and the benchmark gap drifts upward. The gap is not evidence that z\*=3,000 is wrong — it is evidence that wide-sigma companies have inherently noisier production runs at any fixed n. The compute savings (70%) remain meaningful.

### 5c. Seed robustness

Four seeds, B = 40, `rerun=False`:

| Seed | CONT z\* | CONT margin% | CONT rec_batches | SHOCK z\*\* | SHOCK margin% | SHOCK rec_batches |
|---|---|---|---|---|---|---|
| 42 | 3,000 | +6.15% | 530 | 7,500 | +3.25% | 1,891 |
| 99 | 3,000 | +1.36% | 10,789 | 5,000 | +9.92% | 205 |
| 123 | 5,000 | +25.69% | 32 | 5,000 | +9.52% | 222 |
| **7** | **5,000** | **+34.06%** | **19** | **5,000** | **+53.02%** | **9** |

**All margins are positive across all seeds and both engines.** B1 and B2 are absent. This is now confirmed on three positive-centre fragile fixtures (CloudGrow, MedTechX, RetailRollup). The binary sign-switch finding (B1/B2 are negative-centre phenomena) grows stronger.

**Seed 99 is the extreme outlier:** continuous margin is only +1.36%, producing a batch recommendation of 10,789 — far beyond the MAX_REFINEMENT_BATCHES cap. This is the 1/margin² formula operating at its most extreme on the continuous pass. The margin is genuine (positive) but is so thin that the grading call requires a batch count the engine caps. The engine reports this honestly as a large rec_batches value rather than silently hiding it. This is NOT a pathology — it is the engine correctly signalling that seed 99's realisation of the scatter curve sits extremely close to the precision bar on the continuous pass at z\*=3,000. The architecture correctly surfaces the measurement uncertainty.

**z\*\* ≥ z\* on all four seeds:**
- Seed 42: z\*\* = 7,500 > z\* = 3,000 (two-rung separation) ✓
- Seed 99: z\*\* = 5,000 > z\* = 3,000 (one-rung separation) ✓
- Seed 123: z\*\* = 5,000 = z\* = 5,000 (tied) ✓
- Seed 7: z\*\* = 5,000 = z\* = 5,000 (tied) ✓

This is the third consecutive positive-centre fixture with z\*\* ≥ z\* on all seeds (CloudGrow: all tied; MedTechX: z\*\*>z\* on all; RetailRollup: z\*\*>z\* on two, tied on two). The direction is consistent: shocks never push z\*\* below z\*.

**Shocked rec_batches swing:** 9 (seed 7) to 1,891 (seed 42) — a 210× range. Seed 7's tiny rec_batches (9) reflects the extremely wide shocked margin (53.0%): at z\*\*=5,000, scatter has decayed far below the bar on that realisation, requiring almost no confirmatory batches. Seed 42's 1,891 reflects the thin shocked margin at z\*\*=7,500. This seed-sensitivity of shocked rec_batches continues to be the structural feature first observed at Steady Co (step 6) and confirmed on every subsequent fixture.

**Seed 99 anomaly — continuous rec_batches 10,789:** The margin at seed 99 continuous (+1.36%) is the thinnest continuous margin of any positive-centre fixture seed. The 1/margin² formula gives ≈10,400 batches. This is a data point about the scatter curve geometry for this seed's realisation — the scatter at z\*=3,000 is barely below the precision bar — rather than a failure. The engine surfaces it honestly. It is not evidence that z\*=3,000 is wrong; z\*=3,000 is still the precision-binding choice for seed 99.

---

## 6. Shock-channel behaviour

5,000 paths, seed 42. Fires by channel and share among worst 5% (worst 250 paths):

| Channel | All fires | All % | Worst-5% fires | Worst-5% share | MedTechX | CloudGrow | Carvana | Rivian | Steady Co |
|---|---|---|---|---|---|---|---|---|---|
| **margin** | 300 | 19.8% | **131** | **42.4%** | 41.4% | 41.2% | 43.3% | 37.1% | 47% |
| **cash** | 329 | 21.7% | **95** | **30.7%** | 32.0% | 24.7% | 37.1% | 45.7% | 15% |
| **revenue** | 301 | 19.9% | **40** | **12.9%** | 13.5% | 20.1% | 5.5% | 4.3% | 21% |
| strategic | 290 | 19.2% | **24** | **7.8%** | 7.8% | 8.2% | 6.5% | 6.7% | 10% |
| funding | 294 | 19.4% | **19** | **6.1%** | 5.3% | 5.8% | 5.9% | 5.2% | 7% |

Total worst-5% fires: 309 (some paths hit multiple channels).
Mean stress 0.153, max stress 3.12.

**The primary architecture question: does cash become the #1 worst-5% channel?**

**No.** Margin (42.4%) retains the lead; cash (30.7%) is second. The channel ordering (margin > cash > revenue > strategic > funding) is identical to CloudGrow and MedTechX — it has now been reproduced on every positive-centre fragile fixture.

**But cash prominence (30.7%) is substantial and the second-highest of any positive-centre fixture.** The trajectory across positive-centre candidates: CloudGrow 25%, MedTechX 32%, RetailRollup 30.7%. The relationship is not monotone — MedTechX (revenue/equity ~1.6×) showed slightly higher cash share than RetailRollup (revenue/equity ~2.75×). This challenges the strict monotone interpretation.

**Why does margin dominate even at revenue/equity 2.75×?** Two reinforcing mechanisms:

1. **Persistence.** A margin shock fires at year t and compresses operating_margin for all remaining years (`operating_margin[k] *= (1 − damage)` for k ≥ t). On $18-25bn revenue, even a 15% margin compression delivers hundreds of millions in annual NOPAT reduction for the remaining horizon plus terminal value. The damage compounds.

2. **Revenue scale amplifies margin damage.** At 9%–13% margins on $18-25bn revenue, the ABSOLUTE margin channel damage is larger than at CloudGrow's (5%–13% on $3bn). Both the cash and margin channels benefit from the large revenue base, but margin's persistence advantage means it accumulates more worst-path damage across a multi-year cascade.

**Cash at 30.7% is meaningful and driven by the revenue/equity ratio mechanism.** Each cash shock delivers (5%–25%) × year-t revenue / 250M shares = $3.60–$18/share in one-off damage. On a $26 central value, this is 14%–69% of equity. Cash shocks are individually more destructive here than on CloudGrow or MedTechX in per-share dollar terms — but margin's persistent cascade still wins the worst-path accumulation race.

**The revenue/equity-ratio predictor (F4):** Three positive-centre data points now (CloudGrow 1.08× → 25%, MedTechX 1.61× → 32%, RetailRollup 2.75× → 30.7%). The relationship is not cleanly monotone: MedTechX's slightly lower ratio produced slightly higher cash share than RetailRollup. The predictor holds directionally (cash > Steady Co baseline of 15% on all positive-centre fragile fixtures, and cash grows with leverage/revenue scale) but the relationship saturates or is non-monotone above ~1.6×. This is a candidate-specific observation; one more fixture would distinguish saturation from noise.

**Revenue channel (12.9%)** continues to appear in the worst-5% mix for positive-centre companies, confirming the two-fixture observation from CloudGrow (20.1%) and MedTechX (13.5%). The revenue share is lower here than on CloudGrow — the larger cash and margin channels displace it — but still meaningfully above the near-zero seen on negative-centre candidates.

---

## 7. Market-percentile signal (shocked distribution)

No market price is a fixture input. Grid over the shocked distribution (n = 7,500):

| Hypothetical price | % of shocked sims below |
|---|---|
| −$5 | 3.9% |
| −$2 | 5.6% |
| $0 | 6.8% |
| +$2 | 8.4% |
| +$5 | 11.5% |
| +$8 | 15.3% |
| +$11 | 20.8% |
| +$15 | 29.5% |

**The percentile grid is interpretable but compresses into the lower tail.** At $15/share (roughly 57% of the central value), only 29.5% of shocked simulations fall below — the distribution is centred well above $15. At $0, 6.8% of simulations are negative. The right tail stretches far (P95 = $50.74); the distribution is wide and right-skewed, making the percentile grid most informative at the lower end.

A hypothetical market price of $26 (near the central DCF value) would sit close to the 50th percentile of the shocked distribution — the shocked mean ($23.29) is slightly below the deterministic central ($26.16), as expected from the net-negative shock overlay.

---

## 8. Architecture questions — answered

**Q1. Does cash become the #1 worst-5% channel?**

No. Margin (42.4%) retains the lead on seed 42. The revenue/equity ratio of 2.75× — the highest of any positive-centre fixture — is insufficient to flip the channel ordering. This null result is itself an architecture finding: there appears to be a structural reason why the margin channel retains dominance regardless of revenue scale. The persistence mechanic (margin compression carries forward through terminal value) may have no straightforward saturation point, whereas the cash channel is inherently a one-time hit.

**Q2. Does F4 strengthen or weaken?**

F4 is the fragile-class finding that cash channel share tracks the revenue/equity ratio. Three positive-centre data points now tell a non-monotone story: 1.08× → 25%, 1.61× → 32%, 2.75× → 30.7%. F4's directional claim (higher ratio → more cash) is partially supported (RetailRollup cash share is above CloudGrow's 25%) but the relationship reverses slightly from MedTechX to RetailRollup. F4 should be refined: rather than a strict monotone predictor, it may capture a threshold effect where cash becomes structurally prominent above some ratio, but the exact share is then determined by margin scale and persistence. F4 remains a fragile-class finding, not challenged at the binary level, but its quantitative precision is limited.

**Q3. Does z\*\* remain above z\*?**

Yes, on all seeds. z\*\* ≥ z\* on seed 42 (7,500 > 3,000), 99 (5,000 > 3,000), 123 (tied at 5,000), and 7 (tied at 5,000). No seed shows z\*\* < z\*. F9 (z\*\*≥z\* on all seeds for positive-centre companies) is now confirmed on a third fixture.

**Q4. Does F8 hold on a third positive-centre fixture?**

Yes — with the same nuanced framing established on MedTechX. The precision rule detects the additional convergence burden of the shocked distribution (sigma rises from $14.96 to $16.33, precision bar tightens from $0.267 to $0.235). It responds with a higher z\*\* (7,500 vs z\*=3,000 on seed 42). The batch machinery correctly grades the thin shocked margin (+3.25%) and correctly triggers borderline=True. The engine is louder on the shocked pass for the right reason.

The thin-margin / large-batches pattern appears on seeds 42 (shocked margin 3.25%, rec_batches 1,891) and 99 (shocked margin 9.92%, though there z\*\*=5,000 and margin less thin). On seeds 123 and 7, shocked margins are 9.5% and 53.0% respectively — wide, with small rec_batches (222 and 9). This seed-conditionality continues to be correct: the margin's value depends on where z\*\* falls on the scatter decay curve for each seed's realisation.

**Q5. Does z\*\* continue to grow with sigma as beta/revenue increases?**

Yes. Cross-fixture comparison on seed 42:

| Fixture | Beta | Cont sigma | z\* (s42) | z\*\* (s42) |
|---|---|---|---|---|
| CloudGrow | 1.9 | $2.13 | 2,000 | 2,000 |
| MedTechX | 2.4 | $3.01 | 3,000 | 5,000 |
| **RetailRollup** | **2.2** | **$14.94** | **3,000** | **7,500** |

z\*\* grows with sigma: 2,000 → 5,000 → 7,500 across the positive-centre candidates. Crucially, RetailRollup's sigma jump from MedTechX is driven by revenue scale, not beta (beta is actually slightly lower at 2.2 vs 2.4). The z\*\* increase therefore captures a revenue-scale effect that beta alone does not predict. This is a new observation: sigma is the true driver of z\*\*, and sigma has two inputs — beta (drives WACC volatility) and revenue scale (drives per-share dollar volatility from the perturbation machinery).

**Q6. Does any new positive-centre convergence behaviour emerge?**

Two new observations:

1. **z\*\* = 7,500 is the first positive-centre fixture to require a sample count in the N_GRID upper range.** Prior positive-centre fixtures had z\*\* ≤ 5,000. RetailRollup's shocked pass requires 7,500 paths — three-quarters of the way to the folk 10,000 that the project thesis challenges. This is not an argument that the folk number is right; the engine still saves 25% of the compute. But it shows that for wide-sigma positive-centre companies with shocked distributions, the required n can approach the upper part of the grid.

2. **The continuous distribution already shows 2.63% negative paths at z\*=3,000, without any shocks.** For wide-sigma companies, the zero boundary is reachable under smooth perturbation alone. This blurs the conceptual line between "shock-only zone" (below zero) and "perturbation zone" (above zero) that was clean on CloudGrow. The two-layer architecture still correctly captures that shocks extend and deepen the left tail, but the perturbation layer itself has non-trivial left-tail exposure when sigma is large.

---

## 9. Comparison vs all prior candidates

| Dimension | Steady Co | Carvana | Rivian | CloudGrow | MedTechX | **RetailRollup** |
|---|---|---|---|---|---|---|
| Central value | +$12.77 | −$5.61 | −$2.35 | +$5.58 | +$6.20 | **+$26.16** |
| WACC | 8.16% | 10.75% | 12.56% | 12.535% | 14.98% | **12.845%** |
| Beta | 1.1 | 2.2 | 2.0 | 1.9 | 2.4 | **2.2** |
| Net debt/share | $3.00 | $22.73 | $0.83 | $1.00 | $0.75 | **$10.00** |
| Rev/equity ratio | — | — | — | ~1.08× | ~1.61× | **~2.75×** |
| Cont std | ~$4.60 | $14.99 | $1.27 | $2.13 | $3.01 | **$14.94** |
| z\* (seed 42) | 2,000 | 2,000 | 1,500 | 2,000 | 3,000 | **3,000** |
| z\*\* (seed 42) | 2,000 | 1,500 | 2,000* | 2,000 | 5,000 | **7,500** |
| Cont margin (s42) | ~+27% | −117% | −207% | +21.4% | +20.4% | **+6.15%** |
| Shock margin (s42) | — | −155% | −165% | +3.3% | +12.9% | **+3.25%** |
| % neg cont | ~0% | 65.3% | 96.6% | 0.0% | 0.4% | **2.63%** |
| % neg shock | ~0% | 71.3% | 97.2% | 0.6% | 3.1% | **6.76%** |
| Shock floor | — | −$89.78 | −$10.24 | −$2.89 | −$6.80 | **−$61.53** |
| Shock floor extension | — | −$36 | −$2.4 | −$3.48 | −$5.49 | **−$45.71** |
| Shock-free % | ~75% | 75.4% | 75.4% | 75.4% | 75.4% | **75.4%** |
| Worst-5% #1 | margin | margin | cash | margin | margin | **margin** |
| Worst-5% #2 | revenue | cash | margin | cash | cash | **cash** |
| Cash share worst-5% | 15% | 37% | 46% | 25% | 32% | **31%** |
| Benchmark gap% | — | 0.92% | 0.67% | 0.12% | 0.68% | **0.93%** |
| Compute ratio | — | 20% | 15% | 20% | 30% | **30%** |
| B1 fires? | — | Yes | Yes | No | No | **No** |
| B2 fires? | — | Yes | Yes | No | No | **No** |
| z\*\* vs z\* (s42)? | tied | z\*\*<z\* | unstable | tied | z\*\*>z\* | **z\*\*>z\*** |

*Rivian z\*\* seed-unstable; reported at seed 42.

---

## 10. Findings — three tiers

### Tier 1: Candidate-specific (RetailRollup inputs only)

**C1.** Central value = **+$26.16/share**, WACC = **12.845%** — the highest central value of any candidate, achieved by combining a large revenue base ($18bn), strong FCF ramp, and negligible net-debt burden relative to revenue. Revenue/equity ratio ~2.75× is the highest of any positive-centre fixture.

**C2.** Continuous std = **$14.94** — the largest of any positive-centre fixture, and essentially equivalent to Carvana's $14.99 (negative-centre). The wide sigma is driven by revenue scale, not beta: beta 2.2 is lower than MedTechX's 2.4, but the revenue base is 4.5× larger, producing proportionally larger per-share dollar swings from the same relative perturbation widths.

**C3.** **2.63% of continuous paths are negative** without any shock overlay. For wide-sigma companies with a large revenue base, the zero boundary is reachable under smooth perturbation alone. The two-layer "perturbation above zero / shocks below zero" conceptual split is blurred at this scale.

**C4.** **z\*\* = 7,500 on seed 42** — the highest z\*\* of any positive-centre fixture. Corresponds to z\*\*−z\* = 2 grid rungs on seed 42. The n=7,500 requirement is not evidence the folk 10,000 is needed — 25% savings are still achieved — but it demonstrates the precision rule can push z\*\* near the upper grid range when sigma is large.

**C5.** **Shocked floor = −$61.53** — the largest negative floor extension of any positive-centre fixture (−$45.71 extension). The deep floor is proportional to the revenue scale: cascading shocks on $18-25bn revenue, applied to 250M shares, produce extreme per-share damage on the worst paths. The shocked distribution's left tail is severe.

**C6.** **Seed 99 continuous rec_batches = 10,789** — the largest batch recommendation of any candidate on any pass, reflecting a thin continuous margin (+1.36%) at z\*=3,000. This is an extreme realisation of the 1/margin² amplification and is correctly surfaced by the engine. It does not invalidate z\*=3,000; it signals that the measurement at seed 99 sits unusually close to the bar.

### Tier 2: Fragile-company class (accumulating across positive-centre fixtures)

**FC1 (update).** The worst-5% channel ordering **margin > cash > revenue > strategic > funding** is now confirmed on three positive-centre fragile fixtures (CloudGrow, MedTechX, RetailRollup). This ordering is stable and does not flip to cash dominance even at revenue/equity ratio 2.75×. Three-fixture confirmation; this is a robust fragile-company pattern.

**FC2 (update).** **z\*\* ≥ z\* on all seeds is now confirmed across three positive-centre fixtures.** CloudGrow (tied), MedTechX (z\*\*>z\* on all seeds), RetailRollup (z\*\*>z\* on 2 seeds, tied on 2). No positive-centre fixture has shown z\*\*<z\* on any seed. The direction (shocks push convergence requirement upward or leave it equal) is robust across six seeds per fixture × three fixtures.

**FC3 (refinement).** The revenue/equity ratio predictor for cash channel share is directionally supported but **non-monotone above ~1.6×**: CloudGrow 1.08× → 25%, MedTechX 1.61× → 32%, RetailRollup 2.75× → 30.7%. Cash prominence clearly exceeds the Steady Co baseline (15%) on all three positive-centre fragile fixtures. The relationship saturates or has some non-linearity at higher ratios. The simpler claim — "higher revenue/equity ratio → structurally elevated cash share relative to a calm company" — remains supported. The strict monotone claim does not.

**FC4.** **Revenue channel share in worst-5% remains elevated for positive-centre companies** relative to negative-centre companies (Carvana 5.5%, Rivian 4.3%). Three positive-centre fixtures: CloudGrow 20.1%, MedTechX 13.5%, RetailRollup 12.9%. Revenue channel share appears to decrease slightly as cash/margin absorb a larger share at higher revenue scale. Three-fixture observation.

### Tier 3: Architecture-level

**F9 (add third fixture).** z\*\*≥z\* on all seeds confirmed on RetailRollup, the third positive-centre fragile fixture. CloudGrow: tied. MedTechX: z\*\*>z\* on all. RetailRollup: z\*\*>z\* on 2, tied on 2. Zero instances of z\*\*<z\* across three fixtures and twelve seeds. The direction is now established on three fixtures — promote to firm architecture-level.

**F8 (add third fixture).** The engine correctly detects that shocked distributions require more paths (higher z\*\*) and reports the additional measurement burden through thin margins and large rec_batches on the seeds where z\*\* lands near the precision bar. Confirmed on three positive-centre fixtures. F8's revised framing (seed-conditional thin margins, NOT universally thin) remains accurate.

**F5 (fifth fixture confirmation).** Benchmark gap 0.93% at 30% compute. Now confirmed on five total fixtures (Steady Co, Carvana, Rivian, CloudGrow, MedTechX, RetailRollup). Even at the widest sigma yet ($14.94), the company-specific z\* finds the right answer within 1% of the folk budget. Architecture-level.

**New architecture observation: sigma is the true driver of z\*\* — and has two inputs.** Across positive-centre fixtures, z\*\* grows with sigma. But sigma is not just a function of beta: RetailRollup has lower beta (2.2) than MedTechX (2.4) yet far higher sigma ($14.94 vs $3.01) and far higher z\*\* (7,500 vs 5,000) because the revenue scale (4.5× larger) amplifies the same relative perturbation widths into much larger per-share dollar swings. **Beta drives WACC/discount-rate volatility; revenue scale drives FCF/equity volatility.** Both feed sigma; sigma drives z\*\*. This is a one-fixture observation — not yet architecture-level — but worth watching on future large-revenue candidates.

---

## 11. Unexpected results

- **Cash did not overtake margin even at revenue/equity ratio 2.75×.** The design hypothesis was that pushing this ratio further might flip the ordering. It did not. Margin's persistence advantage appears structural at the positive-centre fragile company profile. Whether there is a ratio high enough to flip the ordering (perhaps requiring margins thin enough to be nearly zero and cash shocks large enough per share) remains open.

- **The continuous distribution reaches 2.63% negative paths without shocks.** The design anticipated a positive-centre company with a large buffer above zero. Instead, the wide sigma from the large revenue base pushed the continuous left tail below zero more than expected. The zero boundary is not solely a shock phenomenon at this scale.

- **Seed 99 continuous rec_batches = 10,789.** The margin at seed 99 continuous (+1.36%) is thin enough to trigger a recommendation that exceeds practical cap. The engine surfaces this correctly; it is not a failure but it is a strong reminder that the 1/margin² formula is sensitive to thin margins, and that some seed realisations produce genuinely ambiguous grading calls even on the continuous engine.

- **z\*\* = 7,500.** The project's original build-sequence prediction was that z\*\* > z\* and that the gap would be a headline finding. For Steady Co and the first fragile candidates, the gap was invisible. For MedTechX it appeared. For RetailRollup it is two grid rungs (3,000 → 7,500) — the first time z\*\* has pushed near the top of the N_GRID on a positive-centre fixture.

---

## 12. Future questions generated by this run

1. **Is there a revenue/equity ratio at which cash overtakes margin in the worst-5%?** RetailRollup at 2.75× did not achieve this. A fixture with 3–5× ratio might — but it would likely require either even thinner margins (reducing the absolute margin-channel damage) or a revision to the cash damage bands. Understanding whether the flip is achievable under V1 calibration, or requires a recalibration, would clarify F4's long-term architecture claim.

2. **Is the sigma = f(beta, revenue_scale) decomposition stable?** RetailRollup is the first fixture where revenue scale dominates beta as the sigma driver. A future fixture with high beta AND large revenue (e.g. beta 2.4 on $15bn revenue) would test whether the two drivers are additive, multiplicative, or interact in a more complex way.

3. **What happens to z\*\* at even wider sigma?** Seed 42 produced z\*\*=7,500 here. If sigma were 1.5× wider still (through higher revenue scale or higher beta), would z\*\* push to 10,000 — the folk number the project challenges? That would be the strongest possible architecture stress test: a company that genuinely needs the folk sample size.

4. **Why is the continuous margin (seed 99: +1.36%) so thin here but not on MedTechX?** Both have z\*=3,000 on seed 99. MedTechX's continuous margin at seed 99 was +19.3%. RetailRollup's is 1.4% — extreme compression. The wide sigma ($14.94) means scatter at z\*=3,000 is barely below the bar on seed 99's realisation. At narrower sigma, the same n=3,000 gives much more margin. This suggests that for wide-sigma companies, the precision bar is harder to clear cleanly even at the "right" z\*, and batch recommendations will be highly seed-sensitive on the continuous pass.

5. **Does z\*\* = 7,500 produce a reliable production run?** The shocked production is run at 7,500 paths. For a company this wide (sigma $16.21), is 7,500 paths stable enough to quote a precise mean and percentiles? The answer from the benchmark is yes (within 1% of folk mean at 30% compute on the continuous pass), but the shocked benchmark has not been measured. A shocked benchmark (z\*\* = 7,500 vs folk 10,000 shocked) would complete the thesis proof for high-sigma fixtures.

---

*End of first-run log. Next append: after a fourth positive-centre fixture is run to test FC3 (monotone vs saturation for cash channel), or after the B1/B2 fix is implemented.*
