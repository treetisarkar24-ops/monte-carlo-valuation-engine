# Candidate #2 — Rivian

**A permanent research log for the second fragile-company case study run through the Monte Carlo Valuation Engine.**

**Status:** Complete / living document. Append, don't overwrite.
**First run:** 2026-06-01. Engine state: steps 2–6 complete and locked (deterministic DCF + perturbation MC + convergence z\* + micro-shock overlay + shocked re-convergence z\*\*).
**Run artefacts:** `case_study_runner.py` (staged runner), `candidate2_results.json` (machine-readable dump). Every number below is read from that dump.

---

## 0. Framing — read before trusting any number here

Rivian is a **fixture for architecture exploration, not an investment recommendation.** These inputs are *Rivian-inspired*, not a faithful model of the real company, and nothing here is a view on the stock.

**Why Candidate #2 was chosen.** Carvana (Candidate #1) exposed two architecture bugs when the central valuation turned negative: B1 (sign-fragile precision rule) and B2 (borderline misfire). But Carvana's central valuation was deeply negative (−$5.61/share). That left the primary architecture question unanswered: did those bugs fire because of the *negative valuation centre*, or because of *company fragility itself*, or some *interaction* of the two?

Rivian was chosen to apply pressure from a different angle. It is:
- Fragile in exactly the Carvana sense (high beta, negative early margins, rapid growth with heavy capex)
- But with a materially smaller net-debt load and a much larger share count — so the central valuation, while still negative, is much *shallower* (−$2.35 vs −$5.61)
- Its path to positive equity is visible in the trajectory: operating margins turn positive by year 3

The primary question is: **does the convergence machinery behave normally again when the valuation centre becomes positive?** Rivian's central case remains negative, so Candidate #2 partially answers this: it tests whether reducing the magnitude of negativity changes anything, and establishes a second fragile-negative data point. A positive-centre fragile company is still needed — but the findings here sharpen what that test would need to show.

The governing discipline of this log is the same as Candidate #1: **Rivian outputs are not architecture truths.** Findings are filed under candidate-specific, fragile-company-class, or architecture-level tiers, and a finding is only promoted to architecture-level when it reproduces across ≥2 fixtures.

---

## 1. Inputs & assumptions

| Field | Value |
|---|---|
| starting_revenue | 5,500 |
| net_debt | 1,000 |
| shares_outstanding | 1,200 |
| forecast_years | 5 |
| revenue_growth | 35%, 30%, 25%, 18%, 12% |
| operating_margin | −12%, −5%, +1%, +5%, +8% (ramp from losses to profit) |
| capex_pct_revenue | 10%, 9%, 8%, 7%, 6% (declining) |
| da_pct_revenue | 4% flat |
| nwc_pct_revenue | 3% flat |
| tax_rate | 25% |
| terminal_growth | 2.5% |
| risk_free_rate | 4% |
| equity_risk_premium | 5.5% |
| beta | **2.0** |
| cost_of_debt | 7% |
| debt_to_total_capital | 25% |

**Derived:** WACC = **12.56%**. Higher than Carvana's 10.75%, driven primarily by the high equity beta (2.0) and ERP = 5.5% — the equity weight is large (75%) so the equity cost of capital dominates. Debt is cheaper (7% vs 8.5%) and the leverage is lower (25% vs 55%), but the beta more than compensates.

**What makes this fixture distinctive:** Four design choices in tension. (1) Revenue growth is aggressive (35% in year 1) — a scale-up story. (2) Operating margins are deeply negative in the early years (−12% in year 1) but ramp to +8% by year 5 — a classic EV/automotive build-out. (3) Capex is heavy but declining. (4) Despite all this, net debt is only $1bn on 1,200m shares — thin leverage relative to the equity base. This combination means the central valuation is negative (the explicit period throws off large cash losses early) but only shallowly so; the terminal value is not enough to rescue the equity at a 12.56% discount rate. A lower discount rate or a faster margin ramp would tip it positive.

**Convergence/run settings:** Same as Candidate #1: `N_GRID = [100, 250, 500, 1000, 1500, 2000, 3000, 5000, 7500, 10000]`, `BATCHES_PER_N = 40`, base shock hazard 0.0115/channel/year, stress sensitivity 1.0, equal fragility weights (V1). Convergence seeded by default (42); `rerun=False` on all passes (same as first Carvana run).

---

## 2. Deterministic central case

| | Rivian | Carvana (ref) | Steady Co (ref) |
|---|---|---|---|
| Central per-share | **−$2.35** | −$5.61 | +$12.77 |
| WACC | **12.56%** | 10.75% | 8.16% |

Rivian's base-case DCF puts equity **underwater, but only shallowly.** At central inputs, the heavy explicit-period cash losses (negative FCF in years 1–2 from the combination of negative EBIT and large capex) plus a high discount rate mean that discounted FCFs plus terminal value fall short of net debt. The shortfall is roughly half of Carvana's on a per-share basis.

The proximity to zero is important for what follows: Rivian's central value is negative but much closer to the zero boundary than Carvana. If the sign-fragile precision rule (B1) is a sharp cliff at zero, Rivian tests whether being "slightly negative" produces the same pathology as being "very negative."

---

## 3. Continuous-only Monte Carlo (perturbation, no shocks)

Production run at z\* = 1,500, seed 42, n = 1,500.

| Statistic | Value |
|---|---|
| Mean | −$2.34 |
| Median | −$2.37 |
| Std dev | $1.27 |
| Min / Max | −$7.84 / +$3.41 |
| 5th–95th pctile | **−$4.40 → −$0.33** |
| 10th / 25th | −$3.88 / −$3.16 |
| 75th / 90th | −$1.53 / −$0.74 |
| Share of sims **negative** | **96.6%** |
| P(value > 0) | **3.4%** |

```
   -7.84 |  1
   -7.28 |  2
   -6.72 |  2
   -6.15 |  3
   -5.59 | ### 20
   -5.03 | ###### 41
   -4.47 | ########### 76
   -3.90 | ######################### 165
   -3.34 | ################################### 231
   -2.78 | ########################################## 280
   -2.22 | ###################################### 252
   -1.65 | ############################## 199
   -1.09 | ################# 116
   -0.53 | ########## 64
    0.03 | #### 27
    0.60 | ## 13
    1.16 | # 5
    1.72 |  2
    2.28 |  0
    2.85 |  1
```

Two things stand out immediately.

**First, the distribution is much tighter than Carvana's.** Std dev $1.27 vs Carvana's $14.99 — an order of magnitude narrower. This is a direct consequence of the scale difference: Rivian's revenue base ($5.5bn) produces perturbations that are dollar-small compared to Carvana's ($20bn) multiplied by 220m shares vs 1,200m shares. Per-share volatility is compressed by the large share count. The distribution is also near-symmetric — the histogram is a clean bell sitting below zero, with only a tiny right tail poking above.

**Second, P(value > 0) collapses to 3.4%**, far lower than Carvana's 34.7%. Despite Rivian's central value being shallower in absolute terms, the narrow distribution means almost no paths escape into positive territory. Carvana's wider distribution gave 34.7% of paths a chance at positive value; Rivian's tight bell almost never does. This is a genuine difference in the character of the two fixtures, and it has implications for what "fragile" means: Rivian is fragile in the sense of extremely narrow odds of recovery, not in the sense of a fat-tailed catastrophe distribution.

---

## 4. Shocked Monte Carlo (perturbation + micro-shock overlay)

Production run at z\*\* = 2,000, seed 42, n = 2,000.

| Statistic | Continuous | **Shocked** | Δ |
|---|---|---|---|
| Mean | −$2.34 | **−$2.55** | −$0.21 |
| Median | −$2.37 | −$2.53 | −$0.16 |
| Std dev | $1.27 | $1.39 | +$0.12 |
| Min | −$7.84 | **−$10.24** | −$2.40 |
| Max | +$3.41 | +$2.66 | −$0.75 |
| 5th pctile | −$4.40 | −$4.86 | −$0.46 |
| 95th pctile | −$0.33 | −$0.39 | −$0.06 |
| Share negative | 96.6% | **97.15%** | +0.55pp |
| Shock-free paths | — | **75.36%** | — |

```
  -10.24 |  1
   -9.60 |  0
   -8.95 |  1
   -8.31 |  3
   -7.66 | # 5
   -7.02 | # 7
   -6.37 | ## 19
   -5.73 | #### 35
   -5.08 | ########## 94
   -4.44 | ################ 154
   -3.79 | ############################### 293
   -3.15 | ########################################## 400
   -2.50 | ######################################### 391
   -1.86 | ############################### 298
   -1.21 | ################## 168
   -0.57 | ######## 78
    0.08 | ### 31
    0.72 | # 13
    1.37 | # 5
    2.01 |  4
```

The shock overlay bites, but **dramatically less severely than Carvana.** Carvana's mean dropped $3.90 under shocks; Rivian's drops only $0.21. Carvana's floor collapsed from −$54 to −$90; Rivian's extends from −$7.84 to −$10.24. The shock-free rate is identical (75.36% vs Carvana's 75.4%) — by design, the base hazard is calibrated to the same ~75% target — but the consequence of being hit is far smaller.

**Why the muted shock response?** Two structural reasons. First, Rivian's revenue is smaller and its equity base is larger (1,200m shares), so a cash shock sized off revenue lands as smaller per-share damage than Carvana's. Second, Rivian's explicit-period FCFs are already deeply negative — there is less positive cash flow to destroy, and the engine's perturbation/shock mechanics apply to the *trajectory*, so hitting an already-loss-making trajectory differently than hitting a profitable one.

Mean accumulated stress (0.153) and max stress (3.12) are nearly identical to Carvana — the shock cascade mechanics work the same; it's the transmission that differs.

---

## 5. Convergence — z\*, z\*\*, decision margins

| | Continuous (z\*) | Shocked (z\*\*) |
|---|---|---|
| z (headline, seed 42) | 1,500 | **2,000** |
| z_pct (precision rule) | **None** | **None** |
| z_elbow | 1,500 | 2,000 |
| decision_margin_pct | **−170.8%** | **−207.0%** |
| precision_bar | **−$0.023** | **−$0.025** |
| centre (mean of run-means) | −$2.35 | −$2.54 |
| sigma_estimate | $1.32 | $1.41 |
| borderline flag | **True** | **True** |
| batches_recommended | 40 (suppressed) | 40 (suppressed) |
| adequately_resolved | True | True |

The same pathologies from Candidate #1 reproduce here with identical structure, confirming they are not Carvana-specific artefacts:

- **z_pct = None in both runs.** The precision bar is again negative (−$0.023, −$0.025) because it is 1% of a negative centre. Scatter is always positive, so it can never clear a negative bar. The precision arm is silent.
- **z\* collapses to z_elbow alone**, same as Carvana.
- **decision_margin_pct is negative** (−171% continuous, −207% shocked) — not a measured confidence level but a mechanical artefact of the negative centre.
- **borderline mis-fires**, suppressing the batch-grading and refinement pathway.
- **batches_recommended pinned at 40** on every seed (contrast Steady Co's shocked swing of 171–1,464).

### One new result: z\*\* > z\* (seed 42)

**Candidate #2 is the first fixture where the shocked elbow lands above the continuous elbow** — z\*\* = 2,000 > z\* = 1,500. This is the direction the build-sequence expected but did not observe in Carvana (where z\*\* = 1,500 < z\* = 2,000). However, the seed study complicates the picture considerably.

### Scatter columns (the elbow data the z is derived from)

Continuous scatter: 0.154, 0.066, 0.049, 0.047, 0.033, 0.028, 0.021, 0.020, 0.015, 0.011  
Shocked scatter: 0.133, 0.084, 0.056, 0.049, 0.031, 0.024, 0.026, 0.020, 0.018, 0.013

The shocked scatter at n=3,000 (0.026) is HIGHER than at n=2,000 (0.024) — a non-monotone bump. This is the kneedle algorithm reading the elbow at 2,000 instead of a deeper n. The bump is within normal noise at B=40. This is relevant to the z\*\* > z\* result: it is a one-grid-rung difference driven partly by measurement noise in the scatter estimate, not a strong signal.

---

## 6. Benchmark vs the folk 10,000 (continuous)

| | z\* = 1,500 | Folk 10,000 |
|---|---|---|
| Mean | −$2.340 | −$2.355 |
| Median | −$2.372 | −$2.359 |
| Compute ratio | **0.15** | 1.00 |
| Mean gap | **0.67%** | — |

**The headline thesis survives a second fragile fixture.** At 15% of the folk compute, z\* = 1,500 reproduces the folk-10,000 mean to within 0.7%. This is the elbow-only path (z_pct silent) and it works. Two fixtures now confirm: the elbow leg alone, even when the precision leg is disabled, finds a usable sample size for negative-centre companies.

---

## 7. Shock-channel behaviour

5,000 paths, seed 42. Fires by channel and share among worst 5%:

| Channel | All fires | All % | Worst-5% count | Worst-5% share | Carvana worst-5% | Steady Co worst-5% |
|---|---|---|---|---|---|---|
| **margin** | 300 | 19.8% | **78** | **37.1%** | 43.3% | 47% |
| **cash** | 329 | 21.7% | **96** | **45.7%** | 37.1% | 15% |
| strategic | 290 | 19.2% | 14 | 6.7% | 6.5% | 10% |
| funding | 294 | 19.4% | 11 | 5.2% | 5.9% | 7% |
| revenue | 301 | 19.9% | 9 | 4.3% | 5.5% | 21% |

**Cash is now the dominant worst-path channel at 45.7%**, and margin is second at 37.1%. This is more extreme than Carvana's cash dominance (37.1%) and completely unlike Steady Co (where cash was 15% and revenue was 21%). Mean stress 0.153, max stress 3.12 — nearly identical to Carvana.

The mechanism is the same as Carvana's cash dominance but amplified by the even larger revenue-to-equity ratio. Rivian's revenue in the forecast years is substantial ($5.5–12bn range), and with 1,200m shares at a small per-share value, a cash shock sized as a fraction of revenue delivers an outsized per-share punch. The cash channel's revenue-sizing makes it lethal for high-revenue / thin-per-share-equity companies. With Rivian having a larger revenue base relative to its per-share equity than Steady Co (but smaller than Carvana's absolute revenue), and with early FCFs already deeply negative offering little buffer, cash shocks concentrate into the worst paths at near-Carvana intensity.

This is the second fixture confirming that **equal base hazards do not produce equal worst-path shares** — the capital structure and revenue/equity ratio are the amplifier, not the hazard.

---

## 8. Seed observations (z stability)

Four seeds, B = 40, `rerun=False`:

| seed | CONT z\* | CONT margin% | SHOCK z\*\* | SHOCK margin% |
|---|---|---|---|---|
| 42 | 1,500 | −170.8 | **2,000** | −207.0 |
| 99 | 1,500 | −177.0 | **1,000** | −166.7 |
| 123 | 1,500 | −201.0 | **1,500** | −187.2 |
| 7 | 2,000 | −206.5 | **1,500** | −191.5 |

**Continuous z\* is stable** — three seeds read 1,500, one reads 2,000 (one grid rung). The margins are consistently and stably negative across all seeds (−171% to −207%), confirming the pathology is structural, not a seed artefact.

**Shocked z\*\* is seed-sensitive** and ranges across three grid rungs (1,000 / 1,500 / 2,000). This is meaningfully more seed-sensitive than Carvana's shocked z\*\* (which was rock-stable at 1,500 on all four seeds). The shocked scatter column bump at n=3,000 (visible in seed 42) is a noise-driven elbow read that shifts with the random stream. Within the {1,000, 1,500, 2,000} band, the honest statement is: **z\*\* is not precisely determined at B=40 for this fixture**. This is qualitatively the same as the Steady Co step-6 finding that batch counts become seed-sensitive under shocks, but here it manifests at the level of z\*\* itself (not just rec_batches), because the negative centre suppresses the batch-grading machinery that would normally diagnose and report this instability.

**Decision margins are uniformly negative** across all seeds/engines, confirming B1 and B2 reproduce independently of seed. Rec_batches pinned at 40 on every seed — the borderline short-circuit is consistent.

---

## 9. Market-percentile signal

No market price is a fixture input. The grid below maps hypothetical price points onto the **shocked** distribution:

| Hypothetical price | Percentile of shocked sims below |
|---|---|
| −$5 | 3.95% |
| −$2 | 66.65% |
| $0 | 97.15% |
| +$2 | 99.80% |
| +$5 | 100.0% |
| +$8 | 100.0% |
| +$11 | 100.0% |
| +$15 | 100.0% |

The market-percentile machinery works as designed — it is sign-agnostic. Any positive real-world market price for Rivian would sit at the 97th–100th percentile of simulated intrinsic values under this fixture, i.e. the model reads any positive price as reflecting extreme optimism relative to the modelled cash flow trajectory. This is consistent with how early-loss growth companies are typically priced — the market is pricing in a future that the DCF cannot see without a longer explicit period or richer terminal value assumptions.

The narrow distribution (std $1.39 shocked) means the percentile grid is very compressed: between −$5 (4th percentile) and $0 (97th percentile) is almost the entire distribution.

---

## COMPARISON vs Carvana (Candidate #1) and Steady Co

| Dimension | Steady Co | Carvana | **Rivian** |
|---|---|---|---|
| Central value | +$12.77 | −$5.61 | **−$2.35** |
| WACC | 8.16% | 10.75% | **12.56%** |
| Distribution std (cont) | ~$4.60 | $14.99 | **$1.27** |
| Distribution std (shock) | ~$4.94 | $17.40 | **$1.39** |
| Share negative (cont) | ~0% | 65.3% | **96.6%** |
| Share negative (shock) | ~0% | 71.3% | **97.15%** |
| P(value > 0) cont | ~100% | 34.7% | **3.4%** |
| Precision rule (z_pct) | fires | None | **None** |
| decision_margin_pct | positive | −116% to −128% | **−171% to −207%** |
| borderline | meaningful | mis-fired | **mis-fired** |
| rec_batches across seeds | swings wide | pinned 40 | **pinned 40** |
| z\* (seed 42) | 2,000 | 2,000 | **1,500** |
| z\*\* (seed 42) | 2,000 | 1,500 | **2,000** |
| z\*\* seed stability | stable | very stable | **less stable (3-rung spread)** |
| Worst-5% leader | margin 47% | margin 43%, cash 37% | **cash 46%, margin 37%** |
| Shock magnitude (mean shift) | modest | −$3.90 | **−$0.21** |
| Shock floor extension | modest | −$54→−$90 | **−$7.84→−$10.24** |
| Shock-free % | ~75% | 75.4% | **75.36%** |

**Key contrast against Carvana:** Rivian's distribution is dramatically narrower (std $1.27 vs $14.99) despite having a higher WACC. The large share count (1,200m vs 220m) compresses per-share volatility. The net effect is that Rivian has *fewer* paths in positive territory than Carvana (3.4% vs 34.7%) — a more certain-but-moderate loss, whereas Carvana is a wide-distribution loss. Both trigger identical convergence pathologies (B1/B2), confirming these are sign-driven, not magnitude-driven.

**Key contrast against Steady Co:** Everything that was invisible for Steady Co remains invisible here — the precision rule silently disabled, borderline mis-firing, batch-grading suppressed.

---

## FINDINGS — tier 1: Rivian-specific (these inputs only; NOT architecture truths)

1. The central DCF is **−$2.35/share** — negative but shallow. The WACC (12.56%) is the highest of any tested fixture, driven by high beta (2.0) on a predominantly equity-financed structure.
2. The continuous distribution is **extremely narrow** (std $1.27), almost entirely negative (96.6%), with only 3.4% of paths above zero. Shocks add modest additional damage: mean shift −$0.21, floor extension to −$10.24.
3. **Cash is the dominant worst-path channel (45.7%)**, more extreme than Carvana, for the same structural reason: large revenue relative to per-share equity makes cash shocks catastrophic per share.
4. z\* = 1,500 (continuous, seed 42); z\*\* ranges 1,000–2,000 across seeds. The benchmark confirms z\* reproduces folk-10,000 within 0.67% at 15% compute.
5. P(value > 0) is 3.4% continuous / 2.85% shocked — far lower than Carvana's 34.7%/28.7%. A positive market price would sit at the 97th–100th percentile of this model's distribution.

## FINDINGS — tier 2: Fragile-company (two fixtures now; promoted from Carvana watch items)

1. **Shocks bite asymmetrically on fragile companies** — confirmed on a second fixture. The left tail extends and the mean falls; the right tail is relatively untouched. (First seen: Carvana. Second: Rivian. Mechanism consistent.)
2. **Cash channel disproportionately drives worst paths when revenue is large relative to per-share equity** — the revenue-sizing of the cash shock interacts with capital structure. Carvana: 37%; Rivian: 46%. Steady Co: 15%. The pattern is consistent across two fragile fixtures and one healthy one; the capital-structure × revenue-sizing mechanism is now a fragile-company finding, not a Carvana-specific one.
3. **Which channel kills is predicted by revenue/equity ratio, not by hazard rates.** Confirmed on both fragile candidates. Equal hazards, systematically unequal worst-path shares, with the ordering tracking the fixture's capital structure.
4. **Stress cascades (max stress ~3.1) are a populated part of the distribution for fragile companies** — both Rivian and Carvana reached max stress ~3.12, identical to two decimal places. The stress accumulation mechanic behaves consistently across fragile fixtures.

## FINDINGS — tier 3: Architecture-level (confirmed across ≥2 fixtures)

**A-1 — The convergence precision rule breaks for non-positive valuations — CONFIRMED on second fixture.** `precision_bar = 0.01 × centre` goes negative when the centre is negative. z_pct = None on both runs for both Carvana and Rivian. The bug is reproducible, structural, and not fixture-specific. It is now an **architecture-level confirmed finding.**

**A-2 — The `borderline` flag mis-fires on negative centres — CONFIRMED on second fixture.** `borderline=True`, `batches_recommended=40` (suppressed), `adequately_resolved=True` (false comfort) — identical behaviour on Rivian. The batch-grading pathway is suppressed for both fragile companies, in both cases because the negative centre drives the margin negative. This is now **architecture-level confirmed.**

**A-3 — "adequately_resolved = True" is not trustworthy for negative-centre companies — CONFIRMED.** Both candidates report it while the honesty machinery is mis-firing. Architecture-level.

**A-4 — The elbow leg is robust and sign-agnostic; the benchmark thesis survives negative-centre companies — CONFIRMED on second fixture.** Carvana: z\* reproduces folk-10,000 within 0.92% at 20% compute. Rivian: within 0.67% at 15% compute. The elbow leg alone, when the precision leg is disabled, still finds a usable sample size. This is now **architecture-level confirmed.**

**A-5 — z\*\* did not systematically exceed z\* across seeds.** Seed 42 for Rivian gives z\*\* = 2,000 > z\* = 1,500 — the first fixture where z\*\* > z\*. But seeds 99 and 123 give z\*\* ≤ z\*, and the shocked scatter column is non-monotone (bump at n=3,000 under seed 42). The honest conclusion: **z\*\* is not reliably distinguishable from z\* at B=40 for negative-centre fragile companies**, because the borderline suppression removes the batch-grading machinery that would normally detect and report the unreliability. Whether z\*\* genuinely exceeds z\* for any fragile company remains unknown — the architecture cannot answer that question while B1/B2 are active.

**A-6 (new) — The borderline mis-fire also suppresses z\*\* seed-sensitivity reporting.** For Steady Co (positive centre), seed-sensitive rec_batches (171–1,464) was the step-6 headline finding — the engine correctly flagged instability via the batch-grading pathway. For both Carvana and Rivian (negative centres), that pathway is suppressed: rec_batches pins at 40 on every seed. The result is that fragile companies — which presumably need MORE diagnostic scrutiny given fat tails — get LESS. The suppression makes the engine *quieter* precisely when it should be louder. This is the B2 consequence, and it now has a concrete operational meaning.

---

## Unexpected results

- Rivian's distribution is dramatically narrower than Carvana's despite a higher WACC and similar fragility profile — the large share count is the compressor.
- z\*\* = 2,000 > z\* = 1,500 on seed 42 — the first fixture where the shocked elbow exceeds the continuous elbow. But the seed study shows this result is not stable.
- The shocked z\*\* is more seed-sensitive (three-rung spread: 1,000/1,500/2,000) than Carvana's (completely stable at 1,500). The non-monotone scatter bump is the mechanism. With the borderline mis-fire suppressing batch-grading, the engine doesn't report this instability — it just silently picks whichever elbow the seed delivers.
- P(value > 0) = 3.4%, lower than Carvana's 34.7% despite a shallower central loss — the narrow distribution is what collapses the positive-equity probability.

---

## Does this answer the primary question?

The primary question was: **"Does the convergence machinery behave normally again when the valuation centre becomes positive?"**

Candidate #2 does NOT have a positive valuation centre (−$2.35). So Candidate #2 partially answers the question by establishing a **second data point in the negative-centre space** at a shallower depth. The answer to the refined question is: **reducing the magnitude of the negative centre (from −$5.61 to −$2.35) does not change the pathology.** B1 and B2 fire identically, with similar negative margins (−171% vs −117%), because the sign of the centre is binary — a tiny negative centre triggers the same inversion as a large one. The precision rule doesn't care about magnitude; it cares about sign.

This is itself a useful architectural insight: **the fix for B1/B2 cannot be "pick a company with a less-negative centre." It has to be a rule change that handles sign correctly.** The question of what "normal" behaviour looks like requires a positive-centre fragile company to answer.

---

## Future questions generated by this run

1. **Candidate #3 should be a positive-centre fragile company** to finally answer the primary architecture question. A leveraged, high-beta, high-growth company with thin but positive margins (or one further along the margin ramp than Rivian) would serve. The transition from negative to positive centre is the critical boundary.
2. **z\*\* seed-sensitivity under negative centres.** The Rivian shocked z\*\* ranging 1,000–2,000 across seeds is more unstable than Carvana's rock-stable 1,500. Is this because Rivian's shocked scatter is closer to non-monotone (the bump at n=3,000)? Or does the suppression of batch-grading mean all negative-centre companies have an undetected z\*\* instability that simply wasn't visible in Carvana? A fixture with high shock variance might expose this.
3. **Cash channel dominance across fragile candidates.** Both Carvana (37%) and Rivian (46%) show cash as a co-dominant or dominant worst-path channel. The mechanism (revenue-sizing × thin per-share equity) is clear. If Candidate #3 has a positive centre and a different revenue/equity profile, does cash dominance persist? This would tell us whether the pattern is "fragile company" or "high-revenue/thin-equity company."
4. **The B1/B2 fix is now confirmed necessary.** Two candidates, four seeds each, all showing the same pathology. The question is which fix preserves the thesis most honestly: (a) bar as fraction of |centre|; (b) bar as fraction of σ (sign-agnostic, scale-free — possibly the cleanest anchor); (c) explicit "non-positive centre" branch that reports z_pct as N/A instead of None. Option (b) is architecturally cleanest and separates the precision concept from the valuation sign entirely.
5. **Does the z\*\* > z\* direction hold for a positive-centre fragile company?** The build-sequence expected shocks to raise required n. Carvana said z\*\* < z\*; Rivian seed 42 said z\*\* > z\*; other Rivian seeds say z\*\* ≤ z\*. None of this is clean because B1/B2 are active. A positive-centre company would let z_pct and decision_margin function correctly, giving a fair test of whether the direction is systematic.

---

*End of first-run log. Next append: after a positive-centre fragile company (Candidate #3) provides the comparison needed to fully answer the primary architecture question.*
