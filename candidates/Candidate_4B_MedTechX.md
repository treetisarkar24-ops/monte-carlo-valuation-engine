# Candidate #4B — MedTechX

**A permanent research log for the fourth fragile-company case study run through the Monte Carlo Valuation Engine.**

**Classification:** Positive-Centre Fragile Company — Full Pipeline Run
**Status:** Complete / living document. Append, don't overwrite.
**First run:** 2026-06-01. Engine state: steps 2–6 complete and locked (deterministic DCF + perturbation MC + convergence z\* + micro-shock overlay + shocked re-convergence z\*\*).
**Run artefacts:** `case_study_runner.py` (staged runner), `candidate4b_results.json` (machine-readable dump). Every number below is read from that dump.

---

## 0. Framing and experimental purpose — read before trusting any number here

MedTechX is a **fixture for architecture exploration, not an investment recommendation.** This is a synthetic company. Nothing here is a view on any real entity.

**Why Candidate #4B exists and what question it is designed to answer.**

Candidate #4A (PowerGridCo) was intended as the second positive-centre fragile company but failed the pre-run check (central DCF = −$9.62/share). Four compounding forces — capex persistently exceeding D&A, thin margins, $20/share net debt burden, high WACC at 10.345% — pushed the centre below zero before the pipeline ran. No architecture evidence was gathered.

Candidate #4B (MedTechX) was redesigned to relax the debt force while preserving genuine fragility. Net debt drops to $300m (vs $7,000m for PowerGridCo), making the per-share debt burden negligible ($0.75/share). Beta is elevated to 2.4 — the highest of any candidate — producing a WACC of ~15%, the highest of any positive-centre fixture. Margins ramp from 6% to 14% (thin but positive throughout). Revenue growth is strong but decelerating (28% → 10%).

**Primary architecture question:** Does F8 reproduce on a second positive-centre fragile company?

F8 (pending confirmation from CloudGrow): *When the precision rule is functioning, the shocked pass produces a genuinely thin decision margin on a fragile positive-centre company, and the batch machinery correctly responds with large rec_batches.*

**Secondary questions:**
1. Does z\*\* separate from z\*, and in which direction?
2. Do shocked margins consistently compress relative to continuous margins?
3. Does beta magnitude drive z\* and z\*\* upward?
4. Does cash-channel dominance return for a higher-revenue positive-centre company?
5. Is F8 architecture-level or CloudGrow-specific?

**Pre-run boundary check.** Deterministic DCF run first. Central value = **+$6.20/share**. Gate passed. Full pipeline proceeds.

---

## 1. Inputs & assumptions

| Field | Value |
|---|---|
| starting_revenue | 4,000 |
| net_debt | 300 |
| shares_outstanding | 400 |
| forecast_years | 5 |
| revenue_growth | 28%, 24%, 20%, 15%, 10% (decelerating from high base) |
| operating_margin | 6%, 8%, 10%, 12%, 14% (ramping — thin but positive throughout) |
| capex_pct_revenue | 5% flat |
| da_pct_revenue | 3% flat |
| nwc_pct_revenue | 3% flat |
| tax_rate | 25% |
| terminal_growth | 2.5% |
| risk_free_rate | 4% |
| equity_risk_premium | 5.5% |
| beta | **2.4** (highest of any candidate) |
| cost_of_debt | 6.5% |
| debt_to_total_capital | 18% |

**Derived WACC:**
- Equity weight = 82%; equity cost = 4% + 2.4 × 5.5% = **17.2%**
- After-tax debt cost = 6.5% × 0.75 = **4.875%**
- WACC = 0.82 × 17.2% + 0.18 × 4.875% = **14.98%**

This is the highest WACC of any positive-centre fixture (CloudGrow: 12.535%; Steady Co: 8.16%). Beta 2.4 is the highest of any candidate.

**What makes this fixture distinctive.** Four deliberate design choices, relative to PowerGridCo's failure:

1. **Negligible net debt** ($300m on 400m shares = $0.75/share). Removes the equity-crushing leverage burden. The full enterprise value reaches the equity holders.
2. **Capex below revenue growth — thin capex (5%)** but D&A at 3% means capex > D&A by 2pp. FCF is positive every year because the margin ramp overcomes this modest net-investment drag.
3. **Strong revenue ramp (28% → 10%)** that generates a large terminal value, offsetting the severe WACC headwind.
4. **Beta 2.4 — meaningfully above CloudGrow (1.9)** — producing a wider MC distribution and testing whether z\* and z\*\* both shift upward with sigma.

The fixture is "fragile positive": high WACC compresses every present value, margins are thin in early years, and adverse draws or shocks can push individual paths below zero. But the central case is unambiguously and comfortably positive.

**Convergence/run settings:** Same standard as all prior candidates: `N_GRID = [100, 250, 500, 1000, 1500, 2000, 3000, 5000, 7500, 10000]`, `BATCHES_PER_N = 40`, base shock hazard 0.0115/channel/year, stress sensitivity 1.0, equal fragility weights (V1). Convergence seeded by default (42); `rerun=False` on all passes.

---

## 2. Deterministic central case

| | MedTechX | CloudGrow (ref) | PowerGridCo 4A (ref) | Steady Co (ref) |
|---|---|---|---|---|
| Central per-share | **+$6.20** | +$5.58 | −$9.62 (gate failed) | +$12.77 |
| WACC | **14.98%** | 12.535% | 10.345% | 8.16% |
| Net debt/share | **$0.75** | $1.00 | $20.00 | $3.00 |

MedTechX's central value (+$6.20) is slightly above CloudGrow (+$5.58) despite a substantially higher WACC (14.98% vs 12.535%). The mechanism: MedTechX's revenue growth ramp (28% → 10%) is steeper than CloudGrow's (25% → 10%), generating a larger terminal revenue base and a bigger terminal value. Negligible debt burden means the full enterprise value flows to equity holders. The WACC is a severe headwind, but the stronger revenue trajectory partly offsets it.

**Year-by-year FCF sketch (approximate, from deterministic engine):**

| Year | Revenue ($M) | NOPAT ($M) | D&A ($M) | Capex ($M) | ΔNWC ($M) | FCF ($M) |
|------|-------------|-----------|---------|-----------|----------|---------|
| 1 | 5,120 | 230 | 154 | 256 | 34 | ~94 |
| 2 | 6,349 | 381 | 190 | 317 | 37 | ~217 |
| 3 | 7,619 | 571 | 229 | 381 | 38 | ~381 |
| 4 | 8,762 | 789 | 263 | 438 | 34 | ~580 |
| 5 | 9,638 | 1,012 | 289 | 482 | 26 | ~793 |

Year-1 FCF is thin but positive (~$94m). The margin ramp drives strong FCF growth through the forecast. At 14.98% WACC, early FCFs are steeply discounted; the terminal value (year-5 FCF scaled by the Gordon multiplier at 2.5% growth) carries most of the enterprise value weight — characteristic of high-growth companies at high discount rates.

**Gate confirmed. Full pipeline proceeds.**

---

## 3. Continuous-only Monte Carlo (perturbation, no shocks)

Production run at z\* = 3,000, seed 42, n = 3,000.

| Statistic | Value |
|---|---|
| Mean | **+$6.47** |
| Median | **+$6.17** |
| Std dev | **$3.01** |
| Min / Max | −$1.31 / +$23.84 |
| 5th–95th pctile | **+$2.13 → +$11.85** |
| 10th / 25th | +$2.95 / +$4.38 |
| 75th / 90th | +$8.17 / +$10.50 |
| Share of sims **negative** | **0.4%** |

```
   -1.31 | # 11
   -0.05 | #### 55
    1.21 | ########### 136
    2.46 | ######################## 308
    3.72 | ##################################### 472
    4.98 | ########################################## 541
    6.23 | ####################################### 503
    7.49 | ############################## 384
    8.75 | ################ 212
   10.01 | ################ 178
   11.26 | ####### 90
   12.52 | #### 51
   13.78 | ### 35
   15.04 | # 8
   16.29 |  6
   17.55 |  5
   18.81 |  3
   20.06 |  1
   21.32 |  0
   22.58 |  1
```

**The distribution is roughly bell-shaped with a mild right skew and a mean ($6.47) above the deterministic central ($6.20).** The right skew is the standard multiplicative perturbation + DCF convexity effect, now confirmed on two positive-centre fragile fixtures.

**Two notable features relative to CloudGrow:**

First, the min is **−$1.31** — the continuous distribution already extends slightly below zero at its extreme left. CloudGrow's continuous min was +$0.59. Under correlated adverse draws, MedTechX's higher volatility is sufficient to push a handful of perturbation-only paths below zero (0.4% of paths). No shock overlay is required to touch zero, unlike CloudGrow where zero crossing required the shock layer.

Second, std = **$3.01** vs CloudGrow's $2.13. The wider distribution is a direct consequence of higher beta (2.4 vs 1.9): a larger beta amplifies the equity cost of capital perturbation, and the higher WACC means the discounting is more sensitive to any dial movement. The engine is behaving correctly — more volatile inputs produce a wider distribution.

**Sigma comparison across fixtures:**

| Fixture | Beta | WACC | Cont std | z\* |
|---|---|---|---|---|
| CloudGrow | 1.9 | 12.535% | $2.13 | 2,000 |
| **MedTechX** | **2.4** | **14.98%** | **$3.01** | **3,000** |

Higher beta → wider distribution → higher z\*. The engine responds correctly by placing z\* at 3,000 (vs 2,000 for CloudGrow), driven by the precision rule: z_pct = 3,000, z_elbow = 2,000, z\* = max(3000, 2000) = 3,000.

---

## 4. Shocked Monte Carlo (perturbation + micro-shock overlay)

Production run at z\*\* = 5,000, seed 42, n = 5,000.

| Statistic | Continuous | **Shocked** | Δ |
|---|---|---|---|
| Mean | +$6.47 | **+$5.78** | −$0.70 |
| Median | +$6.17 | +$5.60 | −$0.57 |
| Std dev | $3.01 | **$3.24** | +$0.23 |
| Min | −$1.31 | **−$6.80** | −$5.49 |
| Max | +$23.84 | +$24.05 | — |
| 5th pctile | +$2.13 | **+$0.78** | −$1.35 |
| 95th pctile | +$11.85 | +$11.49 | −$0.36 |
| Share negative | 0.4% | **3.1%** | +2.7pp |
| Shock-free paths | — | **75.4%** | — |

```
   -6.80 |  4
   -5.26 |  8
   -3.71 | # 25
   -2.17 | ## 57
   -0.63 | ######## 185
    0.92 | ############### 365
    2.46 | ################################ 790
    4.00 | ########################################## 1035
    5.54 | ######################################## 986
    7.09 | ############################# 712
    8.63 | ################ 398
   10.17 | ######### 211
   11.71 | ##### 133
   13.26 | ## 50
   14.80 | # 19
   16.34 |  11
   17.88 |  6
   19.43 |  3
   20.97 |  1
   22.51 |  1
```

**Shocks bite asymmetrically, extending the left tail substantially.** Mean drops $0.70 (CloudGrow: −$0.47; Rivian: −$0.21; Carvana: −$3.90). The floor collapses from −$1.31 to −$6.80 — a $5.49 extension. This is larger than CloudGrow's floor extension (−$3.48) and consistent with the higher-sigma fixture producing deeper worst-path outcomes. The P5 shifts from +$2.13 to +$0.78, moving the lower tail boundary close to zero. The right tail barely moves (P95: −$0.36).

**3.1% of shocked paths are negative**, compared to 0.6% for CloudGrow and 0.4% under continuous perturbation alone here. MedTechX's thinner early margins and higher discount rate make the equity more sensitive to compounded shock damage.

**Shock-free fraction: 75.4%** — on the calibration target, consistent with all prior fixtures.

Mean accumulated stress 0.153, max stress 3.12 — identical to all prior fixtures to two decimal places. Stress mechanics are invariant to company characteristics, as designed.

---

## 5. Convergence — z\*, z\*\*, decision margins

### 5a. Headline (seed 42)

| | Continuous (z\*) | Shocked (z\*\*) |
|---|---|---|
| **z (headline, seed 42)** | **3,000** | **5,000** |
| **z_pct (precision rule)** | **3,000 ✓** | **5,000 ✓** |
| z_elbow | 2,000 | 2,000 |
| **z\* = max(z_pct, z_elbow)** | **3,000 (precision binds)** | **5,000 (precision binds)** |
| **decision_margin_pct** | **+20.4%** | **+12.9%** |
| precision_bar | +$0.064 | +$0.058 |
| centre (mean of run-means) | +$6.41 | +$5.79 |
| sigma_estimate | $3.01 | $3.26 |
| **borderline flag** | **False** | **False** |
| **batches_recommended** | **50** | **122** |
| adequately_resolved | False | False |

**Reading each row:**

**z_pct fires in both passes.** z_pct = 3,000 (continuous) and z_pct = 5,000 (shocked). The precision bar is positive and the scatter can be compared against it. The precision rule is fully operational on both passes — consistent with CloudGrow and in sharp contrast to Carvana/Rivian (z_pct = None on every pass).

**z\*\* = 5,000 > z\* = 3,000.** This is new. CloudGrow showed z\*\* = z\* = 2,000 (tied on all seeds). MedTechX shows the shocked pass requiring a higher sample count. The mechanism: shocks widen the distribution (sigma rises from $3.01 to $3.26), so the scatter at n=3,000 is no longer below the precision bar for the shocked engine. The precision rule requires more paths. The elbow does NOT move (z_elbow = 2,000 in both passes) — only the precision arm detects the change. This is the first fixture where z\*\* clearly and unambiguously exceeds z\*.

**decision_margin_pct: +20.4% continuous, +12.9% shocked.** Both are positive, clear, and interpretable. The shocked margin is thinner — the same direction as CloudGrow (cont +21.4%, shock +3.3%) — but the magnitude of compression is smaller on seed 42. At MedTechX's z\*\* = 5,000, scatter has decayed further than at CloudGrow's z\*\* = 2,000, so even though sigma is wider, the margin is not as thin. Section 5c shows this is seed-conditional, not universal.

**borderline is False on both passes.** A 20.4% and 12.9% margin are both clear readings. Contrast with CloudGrow's shocked borderline = True at +3.3%. The engine correctly distinguishes "thin but unambiguous" from "genuinely borderline."

**batches_recommended: 50 (cont) → 122 (shock).** More than doubles — correct, because the shocked margin is thinner and the call needs more batches to confirm. Ratio 2.4×. On CloudGrow, the equivalent ratio was 40× (reflecting CloudGrow's far thinner shocked margin of 3.3%). The batch formula is working in the right direction.

### 5b. Benchmark vs folk 10,000 (continuous)

| | z\* = 3,000 | Folk 10,000 |
|---|---|---|
| Mean | +$6.472 | +$6.428 |
| Median | +$6.175 | +$6.101 |
| Compute ratio | **0.30** | 1.00 |
| Mean gap | **0.68%** | — |

**The benchmark thesis holds on a fourth candidate.** z\* = 3,000 reproduces the folk-10,000 mean to within 0.68% at 30% of the compute budget. This is the first candidate where z\* > 2,000 was warranted — and even at z\* = 3,000, the benchmark gap is sub-1%, confirming that the company-specific sample size finds the right answer without using the full folk budget.

30% compute ratio is the highest of any fragile candidate (Carvana: 20%, Rivian: 15%, CloudGrow: 20%). Higher-sigma companies cost more compute — that is expected and correct. But 0.68% gap at 30% of budget remains inside any meaningful precision requirement. F5 is confirmed on a fourth fixture.

### 5c. Seed robustness

Four seeds, B = 40, `rerun=False`:

| Seed | CONT z\* | CONT margin% | CONT rec_batches | SHOCK z\*\* | SHOCK margin% | SHOCK rec_batches |
|---|---|---|---|---|---|---|
| 42 | 3,000 | +20.4% | 50 | 5,000 | +12.9% | 122 |
| 99 | 3,000 | +19.3% | 55 | 5,000 | +35.5% | 17 |
| 123 | 3,000 | +16.8% | 72 | 5,000 | +33.7% | 19 |
| **7** | **2,000** | **+4.7%** | **914** | **3,000** | **+3.0%** | **2,168** |

**All continuous margins are positive across all seeds.** B1 and B2 are absent. The full convergence machinery is operational. This continues the clean confirmation that B1/B2 are negative-centre phenomena — now confirmed on two positive-centre fragile companies.

**Continuous z\* is stable: three seeds read 3,000, one (seed 7) reads 2,000.** The one-rung wobble is consistent with CloudGrow and Steady Co — a structural feature of grid quantization, not a pathology.

**z\*\* ≥ z\* on every seed.** This is the headline finding of the seed study:
- Seeds 42/99/123: z\*\* = 5,000 > z\* = 3,000 (two-rung separation)
- Seed 7: z\*\* = 3,000 > z\* = 2,000 (one-rung separation)

On no seed does z\*\* fall at or below z\*. This is the first fixture to establish a consistent z\*\* > z\* direction. CloudGrow showed z\*\* = z\* tied on three of four seeds. MedTechX shows clear upward separation on all four.

**Shocked margins vary dramatically across seeds (3.0%–35.5%).** This is the key complexity:
- Seeds 99 and 123: z\*\* = 5,000, shocked margin = 33–35%. Wide. At n=5,000, scatter has decayed well below the precision bar, producing a comfortable margin despite the wider shocked sigma.
- Seed 42: z\*\* = 5,000, shocked margin = 12.9%. Thinner than 99/123 but still comfortable.
- Seed 7: z\*\* = 3,000, shocked margin = 3.0%. Genuinely thin — the full CloudGrow-like signal. rec_batches = 2,168.

**Why the dramatic range?** The margin at z\*\* depends on where z\*\* falls on the scatter decay curve. When z\*\* is pushed to n=5,000 (seeds 42/99/123), scatter at that n is far below the bar — wide margins. When z\*\* stays at n=3,000 (seed 7), scatter is closer to the bar — thin margin. The engine correctly measures the actual scatter on each seed and produces correct output. This is not variance in the engine's judgment; it is variance in what is actually true on each seed's realisation.

**Practical implication for F8.** The "thin shocked margin, large rec_batches" pattern is seed-conditional for MedTechX. It appears fully on seed 7 (margin 3.0%, rec_batches 2,168) and partially on seed 42 (margin 12.9%, rec_batches 122). It does not appear on seeds 99/123. F8 as stated ("shocked margins are consistently thin") requires refinement — see Section 8.

---

## 6. Shock-channel behaviour

5,000 paths, seed 42. Fires by channel and share among worst 5% (worst 250 paths):

| Channel | All fires | All % | Worst-5% fires | Worst-5% share | CloudGrow | Carvana | Rivian | Steady Co |
|---|---|---|---|---|---|---|---|---|
| **margin** | 300 | 19.8% | **132** | **41.4%** | 41.2% | 43.3% | 37.1% | 47% |
| **cash** | 329 | 21.7% | **102** | **32.0%** | 24.7% | 37.1% | 45.7% | 15% |
| **revenue** | 301 | 19.9% | **43** | **13.5%** | 20.1% | 5.5% | 4.3% | 21% |
| strategic | 290 | 19.2% | 25 | 7.8% | 8.2% | 6.5% | 6.7% | 10% |
| funding | 294 | 19.4% | 17 | 5.3% | 5.8% | 5.9% | 5.2% | 7% |

Total worst-5% fires: 319. Mean stress 0.153, max stress 3.12.

**The channel ordering (margin > cash > revenue > strategic > funding) is identical to CloudGrow.** The rank order of all five channels is reproduced on a second positive-centre fragile company. This is a two-fixture observation and qualifies as a fragile-company finding.

**Cash prominence (32%) is higher than CloudGrow (25%) — consistent with MedTechX's higher revenue/equity ratio.** The approximate ratio:
- CloudGrow: $3bn starting revenue / ($5.58 × 500m shares = $2.79bn equity) ≈ 1.1×
- MedTechX: $4bn starting revenue / ($6.20 × 400m shares = $2.48bn equity) ≈ 1.6×

MedTechX's higher ratio correctly predicts higher cash channel weight in worst paths. The mechanism is continuous: more revenue per dollar of equity means each cash shock delivers a larger relative damage per share. Neither fixture approaches the cash dominance of Carvana (37%) or Rivian (46%) because neither has a high revenue/equity ratio by those standards.

**Revenue returns to the worst-5% mix at 13.5%**, confirming the positive-centre observation from CloudGrow (20.1%). On negative-centre companies (Carvana 5.5%, Rivian 4.3%), revenue shocks were nearly absent from worst paths. For positive-centre companies, revenue shocks compound into a terminal value that is positive and substantial — adding damage directly to the tail. Two-fixture confirmation.

---

## 7. Market-percentile signal (shocked distribution)

No market price is a fixture input. The grid maps hypothetical price points onto the shocked distribution:

| Hypothetical price | % of shocked sims below |
|---|---|
| −$5 | 0.08% |
| −$2 | 0.82% |
| $0 | 3.14% |
| +$2 | 9.90% |
| +$5 | 41.88% |
| +$8 | 78.50% |
| +$11 | 93.80% |
| +$15 | 99.26% |

**The percentile grid is fully interpretable.** At $5/share (near the deterministic central of $6.20), 42% of shocked simulations fall below — the shocked distribution is centred slightly below the deterministic point, as expected. At $8/share, 78.5% of paths are below — a price of $8 would reflect meaningful optimism relative to this model's shocked distribution. At $2/share, only 10% of paths are below — a price of $2 would look extremely conservative. The grid spans the full range of plausible prices in a meaningful, informative way. Compare to Rivian, where almost the entire shocked distribution was compressed between −$5 and $0, making the percentile signal nearly useless at any realistic positive price.

---

## 8. Architecture questions — answered

**Q1. Does F8 reproduce?**

Partially, with important nuance.

F8 as stated from the tracker: "When the precision rule is functioning, the shocked pass produces a genuinely thin decision margin on a fragile positive-centre company. The batch machinery correctly responds with large rec_batches."

- The precision rule functions correctly (z_pct active, positive bar, margins interpretable): **Yes, confirmed on all seeds.** ✓
- The batch machinery grades rec_batches correctly (not pinned): **Yes, confirmed on all seeds.** ✓
- A thin shocked margin and large rec_batches appear: **Yes — on seed 7 (margin 3.0%, rec_batches 2,168) fully; on seed 42 (12.9%, 122) partially.** ✓
- Shocked margins are *consistently* thinner than continuous margins across seeds: **No.** Seeds 99 and 123 show shocked margins (33–35%) that are wider than continuous (17–19%). ✗

**Revised F8 statement (proposed):** The precision rule correctly detects that shocked distributions are harder to converge (higher sigma, requiring higher z\*\*) and responds accordingly. The batch machinery correctly grades rec_batches based on the margin at the chosen z\*\*. The thin-margin / large-batches pattern appears on seeds where z\*\* falls at a grid point where scatter is still near the precision bar. Whether any given seed triggers this is determined by the scatter decay curve geometry for that realisation — not a universal consequence of shock presence. The engine is correctly measuring the actual difficulty seed by seed.

The strong-form F8 claim ("shocked margins are consistently thin") is CloudGrow-specific: on that fixture, z\*\* coincidentally landed at n=2,000 on every seed, where scatter was near the bar. On MedTechX, z\*\* is pushed to n=5,000 on most seeds, where scatter has decayed past the bar — producing wide margins. F8's core architecture claim (the engine detects and reports distribution difficulty correctly) is confirmed. Its specific manifestation (always-thin shocked margins) is not universal.

**Q2. Do shocked margins consistently compress relative to continuous?**

No — not across seeds. Seed 42: cont 20.4% → shock 12.9% (compressed). Seed 7: cont 4.7% → shock 3.0% (both thin; modestly compressed). Seeds 99/123: cont 17–19% → shock 34–35% (expanded — z\*\* at higher n means scatter is lower, so margin is wider even though sigma increased). The direction of margin change is not predictable without running the engine and depends on where z\*\* lands on the scatter decay curve.

**Q3. Does z\*\* separate from z\*?**

Yes — clearly and consistently on every seed. z\*\* ≥ z\* on all four seeds:
- Seeds 42/99/123: z\*\* = 5,000 > z\* = 3,000 (two-rung separation)
- Seed 7: z\*\* = 3,000 > z\* = 2,000 (one-rung separation)

This is the first fixture to establish z\*\* > z\* unambiguously. CloudGrow: z\*\* = z\* tied. MedTechX: z\*\* > z\* on all seeds. Both positive-centre fixtures. The direction is established: shocks push z\*\* upward, not downward.

**Q4. Are shocked rec_batches materially larger than continuous?**

Yes — on seeds where the shocked margin is thin. Seed 7: cont 914 → shock 2,168 (2.4×). Seed 42: cont 50 → shock 122 (2.4×). Seeds 99/123: shocked batches (17, 19) are actually *smaller* than continuous (55, 72) — because the shocked margin at z\*\* = 5,000 is wide (33–35%), demanding few confirmatory batches. The batch formula is working correctly in both directions: thin margins → many batches; wide margins → few batches. "Shocked rec_batches always larger" is not a universal rule; it is seed- and margin-conditional.

**Q5. Is F8 architecture-level or CloudGrow-specific?**

F8's core property — the engine correctly detects and reports the additional difficulty of grading a shocked distribution — is architecture-level. Confirmed on both positive-centre fixtures. The specific manifestation (consistently thin shocked margins) is fixture- and seed-conditional. CloudGrow showed it consistently because z\*\* = 2,000 on every seed sat near the scatter bar. MedTechX's z\*\* = 5,000 on most seeds is past the scatter bar — producing wide margins there. F8 should be promoted to architecture tier with the revised framing above.

**Q6. Does channel dominance differ from CloudGrow?**

Same rank ordering (margin > cash > revenue > strategic > funding), modestly different magnitudes. Cash is more prominent on MedTechX (32% vs 25%), consistent with the higher revenue/equity ratio. The capital-structure predictor from F4 continues to operate quantitatively: as revenue/equity rises, cash channel share in worst paths rises. Revenue is less prominent (13.5% vs 20.1%) — partially because a larger share of the worst-path damage is being absorbed by the cash channel.

---

## 9. Comparison vs all prior candidates

| Dimension | Steady Co | Carvana | Rivian | CloudGrow | **MedTechX 4B** |
|---|---|---|---|---|---|
| Central value | +$12.77 | −$5.61 | −$2.35 | +$5.58 | **+$6.20** |
| WACC | 8.16% | 10.75% | 12.56% | 12.535% | **14.98%** |
| Beta | 1.1 | 2.2 | 2.0 | 1.9 | **2.4** |
| Net debt/share | $3.00 | $22.73 | $0.83 | $1.00 | **$0.75** |
| Cont std | — | $14.99 | $1.27 | $2.13 | **$3.01** |
| z\* | — | 2,000 | 1,500 | 2,000 | **3,000** |
| z\*\* | — | 1,500 | 2,000* | 2,000 | **5,000** |
| Cont margin (seed 42) | — | −117% | −207% | +21.4% | **+20.4%** |
| Shock margin (seed 42) | — | −155% | −165% | +3.3% | **+12.9%** |
| % neg cont | — | 65.3% | 96.6% | 0.0% | **0.4%** |
| % neg shock | — | 71.3% | 97.2% | 0.6% | **3.1%** |
| Shock floor | — | −$89.78 | −$10.24 | −$2.89 | **−$6.80** |
| Shock-free % | — | 75.4% | 75.4% | 75.4% | **75.4%** |
| Worst-5% leader | — | margin/cash | cash/margin | margin | **margin/cash** |
| Benchmark gap% | — | 0.92% | 0.67% | 0.12% | **0.68%** |
| Compute ratio | — | 20% | 15% | 20% | **30%** |
| B1 fires? | — | Yes | Yes | No | **No** |
| B2 fires? | — | Yes | Yes | No | **No** |
| z\*\* vs z\*? | — | z\*\*<z\* | Unstable | z\*\*=z\* | **z\*\*>z\* (all seeds)** |

*Rivian z\*\* seed-unstable; reported at seed 42.

---

## 10. Findings — three tiers

### Tier 1: Candidate-specific (MedTechX inputs only)

**C1.** Central value = **+$6.20/share**, WACC = **14.98%** — the highest WACC of any positive-centre fixture and the highest of any candidate. The positive centre is achieved by the combination of negligible leverage ($0.75/share net debt) and a strong revenue ramp that drives a substantial terminal value.

**C2.** z\* = **3,000** — the first fixture where the precision rule drives z\* above 2,000. Higher sigma ($3.01 vs CloudGrow's $2.13) requires more simulations to bring scatter below the 1% precision bar. The elbow stays at 2,000; the separation is precision-rule-driven.

**C3.** z\*\* = **5,000** on three of four seeds (seed 7: 3,000). This is the first fixture showing z\*\* unambiguously above z\* on all seeds. The one-rung separation (seed 7) and two-rung separation (seeds 42/99/123) are consistent with shocks widening sigma modestly and the precision rule responding correctly.

**C4.** Shocked margins vary dramatically across seeds (3.0%–35.5%). The variance reflects where z\*\* lands on the scatter decay curve. Seeds where z\*\* = 5,000 show wide margins; seed where z\*\* = 3,000 shows a thin margin (3.0%, rec_batches 2,168). The engine is correctly measuring each seed's actual scatter.

**C5.** Cash channel prominence (32%) is higher than CloudGrow (25%), consistent with MedTechX's higher revenue/equity ratio (~1.6× vs CloudGrow's ~1.1×). The capital-structure predictor from F4 continues to operate quantitatively.

### Tier 2: Fragile-company class (accumulating across positive-centre fixtures)

**FC1.** z\*\* ≥ z\* on both positive-centre fragile fixtures. CloudGrow: tied (z\*\* = z\* on all seeds). MedTechX: z\*\* > z\* on all seeds. The direction is consistent: shocks push the convergence requirement upward or leave it equal. It does not fall. This is a two-fixture observation and a fragile-company finding.

**FC2.** The worst-5% channel ordering (margin > cash > revenue > strategic > funding) is identical on CloudGrow and MedTechX. Two-fixture confirmation of the channel rank order for positive-centre fragile companies.

**FC3.** Revenue re-enters the worst-5% channel mix when the centre is positive (CloudGrow 20.1%, MedTechX 13.5%). On negative-centre companies (Carvana 5.5%, Rivian 4.3%), revenue is nearly absent. Two-fixture confirmation: revenue shocks are more consequential when the starting valuation is positive because they damage an already-meaningful terminal value trajectory. (MedTechX is lower than CloudGrow — the larger cash share has partly displaced revenue in the worst-path mix.)

**FC4.** Cash channel share in the worst-5% tracks the revenue/equity ratio across positive-centre fixtures (CloudGrow ~1.1× → 25%; MedTechX ~1.6× → 32%). The capital-structure predictor from F4 extends to positive-centre companies with a continuous relationship, not a binary switch.

### Tier 3: Architecture-level

**F8 revised (promote to architecture tier).** The engine correctly detects that shocked distributions are harder to converge (wider sigma → higher z\*\*) and responds with a higher required sample count. The precision rule is the mechanism: z_pct moves from 3,000 to 5,000 when the shocked sigma rises. The batch machinery correctly grades rec_batches based on the margin at z\*\*. This is confirmed on both positive-centre fixtures (CloudGrow and MedTechX). The corollary that "shocked margins are always thin" is not architecture-level — it is a seed- and fixture-conditional phenomenon that depends on where z\*\* lands on the scatter decay curve. Promoting F8 with the revised framing: **"On positive-centre fragile companies, the shocked convergence pass requires a higher or equal z\*\* than the continuous pass, and the batch machinery correctly grades the additional measurement burden."**

**F3 updated.** F3 was originally: "z\*\* direction relative to z\* is not stable for negative-centre fragiles." With positive-centre fixtures now available, the pattern is: z\*\* ≥ z\* (CloudGrow: tied; MedTechX: z\*\* > z\* by one–two rungs). As sigma increases with beta, z\*\* separates further above z\*. The direction is now directionally established for the positive-centre regime.

**F7 (B1/B2 negative-centre phenomena) — add-on confirmation.** B1 and B2 are now confirmed absent on two positive-centre fragile fixtures (CloudGrow, MedTechX). Four fixtures total: two negative (B1/B2 present on all seeds), two positive (B1/B2 absent on all seeds). The binary sign switch is robust on four candidates.

**F5 (benchmark) — fourth confirmation.** 0.68% mean gap at 30% of folk compute. Now confirmed on four total fixtures (Steady Co, Carvana, Rivian, CloudGrow, MedTechX). Architecture-level. This is also the first fixture where z\* > 2,000 was warranted; the benchmark holds even at a higher company-specific n.

---

## 11. Unexpected results

- **Shocked margins are sometimes wider than continuous margins.** Seeds 99 and 123 show shocked margins (33–35%) substantially wider than continuous (17–19%). This was not anticipated. The cause — z\*\* landing at n=5,000 where scatter is low — is mechanically sound but produces a counterintuitive result. F8's thin-margin narrative requires qualification.

- **Continuous distribution extends below zero at 0.4%.** CloudGrow's continuous min was +$0.59. MedTechX's min is −$1.31 under perturbation alone. The higher sigma and thinner early margins are sufficient to push a small fraction of continuous paths below zero without any shock. The zero boundary is not exclusively a shock phenomenon for high-beta high-WACC companies.

- **z\*\* > z\* appears unambiguously.** The build-sequence prediction was that shocks should raise z\*\*. Steady Co, CloudGrow, and the negative-centre candidates all showed z\*\* ≤ z\* or unstable. MedTechX is the first fixture where the prediction is cleanly confirmed — likely because the higher sigma amplifies the precision rule's sensitivity to the shocked sigma increase.

---

## 12. Future questions generated by this run

1. **What drives the seed 7 anomaly?** Seed 7 produces a thin continuous margin (4.7%, z\* = 2,000) and a thin shocked margin (3.0%, z\*\* = 3,000) on MedTechX, and the most extreme shocked case on CloudGrow (margin 1.9%). Is seed 7's random stream structurally more likely to produce edge cases, or is this coincidental?

2. **Is there a beta threshold above which z\*\* > z\* appears consistently?** CloudGrow (beta 1.9) showed z\*\* = z\*. MedTechX (beta 2.4) showed z\*\* > z\*. Is there a continuous relationship between beta/sigma and the z\*\*−z\* gap, or a threshold effect?

3. **Does a high-leverage positive-centre fixture show cash-channel dominance?** MedTechX has $0.75/share net debt; CloudGrow has $1.00/share. Neither shows cash dominance. A positive-centre company with heavy per-share leverage and large revenue would test whether the capital-structure predictor holds at higher leverage.

4. **Does the F8 thin-margin pattern become universal at very high beta?** MedTechX shows it on seed 7 (z\*\* = 3,000) but not on seeds 99/123 (z\*\* = 5,000). A fixture where the scatter decay curve is shallower — requiring z\*\* to fall at a grid rung where scatter is still near the bar on most seeds — might produce consistent thin shocked margins. Whether that requires a specific beta range, sigma level, or grid configuration is an open design question.

5. **Does z\*\* continue to rise with beta?** Steady Co (beta 1.1): z\*\* = 2,000. CloudGrow (beta 1.9): z\*\* = 2,000. MedTechX (beta 2.4): z\*\* = 5,000 on three seeds. A beta ~3.0 fixture might show z\*\* = 7,500 or 10,000. If so, the z\*\*−z\* gap is a useful diagnostic for how much the shock overlay amplifies uncertainty relative to the underlying company volatility.

---

*End of first-run log. Next append: after a third positive-centre fixture is run, or after the B1/B2 fix is implemented and the positive-centre findings are re-verified.*
