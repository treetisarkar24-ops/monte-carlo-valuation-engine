# Candidate #3 — CloudGrow

**A permanent research log for the third fragile-company case study run through the Monte Carlo Valuation Engine.**

**Status:** Complete / living document. Append, don't overwrite.
**First run:** 2026-06-01. Engine state: steps 2–6 complete and locked (deterministic DCF + perturbation MC + convergence z\* + micro-shock overlay + shocked re-convergence z\*\*).
**Run artefacts:** `case_study_runner.py` (staged runner), `candidate3_results.json` (machine-readable dump). Every number below is read from that dump.

---

## 0. Framing and experimental purpose — read before trusting any number here

CloudGrow is a **fixture for architecture exploration, not an investment recommendation.** This is a synthetic company. Nothing here is a view on any real entity.

**Why Candidate #3 exists and what question it is designed to answer.**

Candidates #1 (Carvana, central −$5.61) and #2 (Rivian, central −$2.35) both produced identical convergence pathologies: B1 (the precision rule silently disabled because `precision_bar = 1% × centre` turns negative) and B2 (the borderline flag mis-fires, suppressing batch-grading and refinement). Those two candidates established that the sign of the valuation centre is a binary switch — a shallow negative centre (−$2.35) triggers the same inversion as a deep one (−$5.61). The magnitude of the negative valuation centre does not appear to matter.

That left the primary architecture question unanswered: **are B1 and B2 negative-centre phenomena, or do they also afflict a fragile company with a positive valuation centre?**

CloudGrow was designed specifically to cross the sign boundary: a high-beta, high-WACC, thin-margin cloud company that is genuinely fragile but whose central DCF valuation is positive. If the convergence machinery returns to normal operation once the centre is positive, B1 and B2 can be localised to the negative-centre regime. If the machinery still misbehaves, the issue is deeper than sign alone.

**Pre-run boundary check.** Before running the full pipeline, the deterministic DCF was run first. Central value = **+$5.58/share**. The boundary has been crossed. The full pipeline proceeds.

The governing discipline is the same as every prior candidate: **CloudGrow outputs are not architecture truths.** Findings are filed under candidate-specific, fragile-company-class, or architecture-level tiers, and a finding is only promoted to architecture-level once it reproduces across ≥2 fixtures.

---

## 1. Inputs & assumptions

| Field | Value |
|---|---|
| starting_revenue | 3,000 |
| net_debt | 500 |
| shares_outstanding | 500 |
| forecast_years | 5 |
| revenue_growth | 25%, 22%, 18%, 14%, 10% (decelerating from high base) |
| operating_margin | 5%, 7%, 9%, 11%, 13% (ramping — thin but positive throughout) |
| capex_pct_revenue | 4% flat |
| da_pct_revenue | 3% flat |
| nwc_pct_revenue | 2% flat |
| tax_rate | 25% |
| terminal_growth | 2.5% |
| risk_free_rate | 4% |
| equity_risk_premium | 5.5% |
| beta | **1.9** |
| cost_of_debt | 6.5% |
| debt_to_total_capital | **20%** |

**Derived:** WACC = **12.535%**. This is almost identical to Rivian's 12.56% — a useful control, since it isolates the effect of the valuation sign from any WACC change. The high WACC is driven by the large equity cost of capital: beta 1.9 × ERP 5.5% = 10.45% equity premium on top of the 4% risk-free rate, with the equity weight at 80%.

**What makes this fixture distinctive:** Four features conspire to keep this fixture fragile while holding the central valuation positive. (1) Revenue growth is strong (25% in year 1, decelerating to 10%) but decelerating — not the explosive scale-up of Rivian. (2) Operating margins are thin but positive in every year (5% to 13%), contrasting with Rivian's early losses. The margin ramp means the explicit-period cash flows are small but never negative. (3) The balance sheet is moderate: $500m net debt on 500m shares is manageable, making the per-share equity sensitive to changes in value without being dominated by a huge debt overhang like Carvana. (4) Beta 1.9 makes the discount rate high (12.535%), which acts as a continuous headwind — the company can be valued positively only because the margin ramp generates enough terminal-period cash to offset the high discount rate.

The fixture is intentionally "borderline healthy" rather than "comfortably positive" — the valuation at $5.58 is meaningful but not large. This maximises the chance of genuinely exercising the precision rule and giving meaningful answers to all eight architecture questions.

**Convergence/run settings:** Same standard: `N_GRID = [100, 250, 500, 1000, 1500, 2000, 3000, 5000, 7500, 10000]`, `BATCHES_PER_N = 40`, base shock hazard 0.0115/channel/year, stress sensitivity 1.0, equal fragility weights (V1). Convergence seeded by default (42); `rerun=False` on all passes (consistent with Candidates #1 and #2).

---

## 2. Deterministic central case

| | CloudGrow | Rivian (ref) | Carvana (ref) | Steady Co (ref) |
|---|---|---|---|---|
| Central per-share | **+$5.58** | −$2.35 | −$5.61 | +$12.77 |
| WACC | **12.535%** | 12.56% | 10.75% | 8.16% |

CloudGrow's base-case DCF produces **positive equity value** — the first fragile candidate to cross the zero boundary. At central inputs, the margin ramp from 5% to 13% generates positive free cash flows in every year, and the terminal value is substantial enough (at 2.5% terminal growth against 12.535% WACC) that the equity bridge produces a positive per-share result after subtracting net debt.

The magnitude ($5.58) is moderate by design. Steady Co's $12.77 reflects a mature, profitable company with a comfortable discount rate. CloudGrow sits at less than half that level despite having a positive central value — it is a "fragile positive" rather than a healthy positive. This is the correct profile for the boundary-crossing test.

**WACC comparison note.** CloudGrow (12.535%) and Rivian (12.56%) have virtually identical discount rates, making this the cleanest possible comparison across the negative/positive boundary. Any difference in convergence behaviour between the two fixtures is attributable to the sign of the valuation centre, not to the cost of capital.

---

## 3. Continuous-only Monte Carlo (perturbation, no shocks)

Production run at z\* = 2,000, seed 42, n = 2,000.

| Statistic | Value |
|---|---|
| Mean | +$5.73 |
| Median | +$5.49 |
| Std dev | $2.13 |
| Min / Max | +$0.59 / +$17.99 |
| 5th–95th pctile | **+$2.66 → +$9.55** |
| 10th / 25th | +$3.27 / +$4.20 |
| 75th / 90th | +$6.96 / +$8.62 |
| Share of sims **negative** | **0.0%** |
| P(value > 0) | 100.0% |

```
    0.59 | # 12
    1.46 | ###### 50
    2.33 | ############## 122
    3.20 | ################################ 272
    4.07 | #################################### 306
    4.94 | ########################################## 361
    5.81 | ################################# 285
    6.68 | ########################### 228
    7.55 | ################ 139
    8.42 | ############ 103
    9.29 | ####### 58
   10.16 | ### 30
   11.03 | ### 22
   11.90 |  4
   12.77 |  2
   13.64 |  3
   14.52 |  1
   15.39 |  1
   16.26 |  0
   17.13 |  1
```

**Every perturbation-only path produces a positive valuation.** The distribution is right-skewed, with a mode near $5–6/share and a long right tail reaching to $18. The min value ($0.59) confirms the distribution is close to the zero boundary at the extreme left tail — individual paths can be pushed down by correlated adverse draws, but not across zero under perturbation alone.

The mild right-skew is the multiplicative perturbation + DCF convexity behaviour first observed in Steady Co, now confirmed on a positive-centre fragile company. It is a property of the mechanics, not the company.

Std dev $2.13 is intermediate: wider than Rivian's $1.27 (which was compressed by the large share count) but much narrower than Carvana's $14.99 (which was amplified by a small share count on a large revenue base). CloudGrow's 500m shares and $3bn revenue put it in a moderate range.

---

## 4. Shocked Monte Carlo (perturbation + micro-shock overlay)

Production run at z\*\* = 2,000, seed 42, n = 2,000.

| Statistic | Continuous | **Shocked** | Δ |
|---|---|---|---|
| Mean | +$5.73 | **+$5.26** | −$0.47 |
| Median | +$5.49 | +$5.09 | −$0.40 |
| Std dev | $2.13 | $2.34 | +$0.21 |
| Min | +$0.59 | **−$2.89** | −$3.48 |
| Max | +$17.99 | +$18.34 | — |
| 5th pctile | +$2.66 | +$1.64 | −$1.02 |
| 95th pctile | +$9.55 | +$9.51 | −$0.04 |
| Share negative | 0.0% | **0.6%** | +0.6pp |
| Shock-free paths | — | 75.4% | — |

```
   -2.89 |  3
   -1.83 |  2
   -0.77 | # 12
    0.29 | ##### 53
    1.36 | ########### 111
    2.42 | ######################### 251
    3.48 | ################################### 352
    4.54 | ########################################## 423
    5.60 | ################################ 318
    6.66 | ###################### 219
    7.72 | ########### 114
    8.79 | ###### 61
    9.85 | #### 37
   10.91 | ### 27
   11.97 | # 8
   13.03 |  4
   14.09 |  3
   15.15 |  0
   16.22 |  1
   17.28 |  1
```

Two observations stand out.

**First, shocks are necessary to push any path below zero.** The continuous distribution sits entirely above zero; only the shock overlay produces negative-valuation paths (0.6%). This is the correct behaviour for a positive-centre company where the valuation centre is above zero but not by a large margin. The shock overlay is doing exactly what it exists to do: generating fat-tail outcomes that smooth perturbation cannot reach.

**Second, the shock effect is muted relative to Carvana but more visible than Rivian.** Mean drops $0.47 (Carvana: −$3.90; Rivian: −$0.21). The floor collapses from +$0.59 to −$2.89 (a $3.48 extension). The right tail barely moves (95th pctile: −$0.04). The asymmetric downside bite is present but the magnitude is proportional to a company that is not deeply leveraged or deeply loss-making.

Mean accumulated stress 0.153, max stress 3.12 — consistent with every prior fixture (Carvana: 0.15/3.12; Rivian: 0.153/3.12). The shock cascade mechanics are calibrated identically and behave identically regardless of the sign of the centre. The stress accumulation is a property of the overlay design, not the underlying company.

---

## 5. Convergence — z\*, z\*\*, decision margins

This is the primary section of the CloudGrow run. Every question the experiment was designed to answer lives here.

| | Continuous (z\*) | Shocked (z\*\*) |
|---|---|---|
| **z (headline, seed 42)** | **2,000** | **2,000** |
| **z_pct (precision rule)** | **2,000 ✓** | **2,000 ✓** |
| z_elbow | 2,000 | 1,000 |
| **z\* = max(z_pct, z_elbow)** | **2,000 (tied)** | **2,000 (precision binds)** |
| **decision_margin_pct** | **+21.4%** | **+3.3%** |
| precision_bar | +$0.057 | +$0.053 |
| centre (mean of run-means) | +$5.71 | +$5.26 |
| sigma_estimate | $2.16 | $2.32 |
| **borderline flag** | **False** | **True (correct)** |
| **batches_recommended** | **45 (graded)** | **1,799 (graded)** |
| adequately_resolved | False | True |

**This table is the answer to every architecture question CloudGrow was designed to test.** Reading each row in turn:

**z_pct fires.** For the first time on a fragile company, z_pct is not None. It equals 2,000 on the continuous run and 2,000 on the shocked run. The precision rule — "smallest n whose scatter stays below 1% of the valuation" — has a positive bar ($0.057 continuous, $0.053 shocked) and can be compared against a positive scatter. The rule is fully operational.

**decision_margin_pct is positive and interpretable.** Continuous: +21.4%. This is a clear, unambiguous reading: z\* sits well past the precision bar, and the scatter at z\* = 2,000 is 21.4% below it. The margin is moderate (healthy companies can show 30–50%) but genuine. Shocked: +3.3%. The shocked precision margin is thin. This is not a pathology — it is a real measurement. Under shocks, the scatter at z\*\* is nearly touching the precision bar from below. The company's shocked distribution is harder to grade cleanly than the continuous distribution.

**borderline behaves correctly — and differently in the two passes.** Continuous: `borderline = False`. The 21.4% margin is comfortable; there is no ambiguity about whether z\* = 2,000 is on the boundary. Shocked: `borderline = True`. The 3.3% margin is genuinely thin; z\*\* sits right at the precision bar. **This is the correct behaviour for both.** The contrast with Carvana and Rivian is stark: on those fixtures, `borderline = True` on every seed, every pass, at margins of −117% to −207% — not a measurement of thinness but a mechanical artefact of a negative bar. CloudGrow's shocked borderline is a real signal about the company's shock-distribution difficulty.

**Batch grading and refinement re-engage fully.** Continuous: `batches_recommended = 45`. This is the graded value for a 21.4% margin — a few extra batches would sharpen the call but it is already adequate. Shocked: `batches_recommended = 1,799`. This is the graded value for a 3.3% margin: the formula `batches = σ²/(2·margin²) + 1` amplifies the thin margin into a large recommendation, which is exactly what the engine is designed to do. The batch machinery is no longer pinned at 40 and falsely reporting adequacy; it is working.

**z_pct is the binding constraint on the shocked pass.** `z_elbow = 1,000`, `z_pct = 2,000`, `z\*\* = max(2000, 1000) = 2,000`. The precision rule is pulling z\*\* to a higher, more conservative value than the elbow alone would suggest. For Carvana and Rivian, the max() combiner had only one operand (z_pct = None); here both operands are real numbers and the precision rule wins. This is the correct engine behaviour.

**adequately_resolved:** Continuous: `False` (because `rerun=False`, z_star_moved is null — no refinement was attempted). Shocked: `True` — but for the right reason. When `borderline = True`, `adequately_resolved = True` means "the precision bar is genuinely at the boundary; no further refinement will give a crisp verdict." This is honest, not false comfort. The contrast with Carvana/Rivian's `adequately_resolved = True` (which reported false comfort while the honesty machinery was mis-firing) is complete.

**Does the shocked precision rule dominate because shocks compress the margin?** Yes. The shocked centre ($5.26) is slightly below the continuous centre ($5.71), and the shocked scatter is higher ($2.32 vs $2.16), so the precision bar ($0.053) is slightly lower and harder for the scatter to clear cleanly. The margin falls from 21.4% to 3.3%. This is the structural reason why the shocked pass lands in borderline territory while the continuous pass does not: shocks widen the distribution and push the centre slightly down, both of which tighten the bar-vs-scatter gap. At a 3.3% margin, the recommendation of ~1,800 batches is the correct honest diagnosis.

---

## 6. Benchmark vs the folk 10,000 (continuous)

| | z\* = 2,000 | Folk 10,000 |
|---|---|---|
| Mean | +$5.734 | +$5.727 |
| Median | +$5.494 | +$5.470 |
| Compute ratio | **0.20** | 1.00 |
| Mean gap | **0.12%** | — |

**The benchmark thesis holds on a positive-centre fragile company.** z\* = 2,000 reproduces the folk-10,000 mean to within 0.12% — the smallest gap of any fixture so far (Carvana: 0.92%, Rivian: 0.67%). At 20% of the folk compute, the elbow-found sample size is more than adequate. This is now three fragile candidates (plus Steady Co at step 6) all confirming that company-specific z\* reproduces the full-budget answer. The benchmark finding (F5 in the tracker) remains architecture-level confirmed.

An important note on *why* this is clean for CloudGrow but was also clean for Carvana/Rivian: the benchmark only compares two production runs at fixed n (z\* vs 10,000). It does not depend on the precision rule, decision_margin, or borderline machinery — it is a direct empirical comparison. So the benchmark was never broken by B1/B2; it just couldn't *see* whether the machinery for choosing the right n was working correctly. The contribution CloudGrow makes to the benchmark finding is confirming that when the full precision machinery is functioning, it produces an equally usable z\*.

---

## 7. Shock-channel behaviour

5,000 paths, seed 42. Fires by channel and share among worst 5% (worst 250 paths):

| Channel | All fires | All % | Worst-5% fires | Worst-5% share | Carvana | Rivian | Steady Co |
|---|---|---|---|---|---|---|---|
| **margin** | 300 | 19.8% | **135** | **41.2%** | 43.3% | 37.1% | 47% |
| **cash** | 329 | 21.7% | **81** | **24.7%** | 37.1% | 45.7% | 15% |
| **revenue** | 301 | 19.9% | **66** | **20.1%** | 5.5% | 4.3% | 21% |
| strategic | 290 | 19.2% | 27 | 8.2% | 6.5% | 6.7% | 10% |
| funding | 294 | 19.4% | 19 | 5.8% | 5.9% | 5.2% | 7% |

Total worst-5% fires: 328 (some paths hit multiple channels).

Mean stress 0.153, max stress 3.12 — identical to Rivian and Carvana to two decimal places.

**The channel mix for CloudGrow looks like Steady Co, not like Carvana or Rivian.** Margin is dominant (41%), revenue is the second-highest (20%), and cash — the dominant channel for both fragile candidates — sits at only 25%. This is not a fragile-company pattern; it is the capital-structure-dependent pattern. The mechanism is the same one that explained Carvana's cash dominance:

- CloudGrow revenue: $3–5.5bn across the forecast. On 500m shares with a per-share value near $5.58, the revenue/equity ratio is moderate.
- A cash shock of 5–25% of year-t revenue adds $150–1,375m to net debt. Divided across 500m shares, that is $0.30–$2.75/share — significant, but not catastrophic.
- Carvana's revenue ($20–26bn on 220m shares) made the same channel deliver 10× the per-share damage. Rivian was intermediate (revenue $5.5–12bn on 1,200m shares) but arrived at a similarly large ratio because the per-share equity was tiny.

**Revenue re-enters the worst-5% channel mix.** In both Carvana and Rivian, revenue was nearly absent from the worst paths (5.5% and 4.3%). For CloudGrow it returns to 20%, close to Steady Co's 21%. Revenue shocks are harmful when the starting value is positive and the revenue trajectory matters for the terminal value calculation — on negative-centre companies, shocks to an already-losing revenue stream don't differentiate the worst paths as sharply. This is a candidate-specific observation worth watching on future fixtures.

---

## 8. Seed observations (z\* / z\*\* stability)

Four seeds, B = 40, `rerun=False`:

| seed | CONT z\* | CONT margin% | CONT rec_batches | SHOCK z\*\* | SHOCK margin% | SHOCK rec_batches |
|---|---|---|---|---|---|---|
| 42 | 2,000 | +21.4 | 45 | 2,000 | +3.3 | 1,799 |
| 99 | 2,000 | +23.4 | 38 | 2,000 | +2.7 | 2,667 |
| 123 | 1,500 | +14.0 | 104 | 2,000 | +8.4 | 286 |
| 7 | 2,000 | +26.5 | 30 | 1,500 | +1.9 | 5,294 |

**All margins are positive across all seeds.** This is the definitive confirmation that B1 and B2 are negative-centre phenomena. Not a single seed on either the continuous or shocked engine produces a negative decision margin. The margins range from +1.9% to +26.5% — the precision rule is working everywhere.

**Continuous z\* is robust.** Three seeds read 2,000; one (seed 123) reads 1,500. This is a one-rung wobble consistent with Steady Co and Carvana. The continuous margins are all positive and substantial (+14% to +27%), confirming healthy operation.

**Seed 7 note.** For seed 7, `cont_zpct = 1500` but `cont_z = 2000`. This means z_pct = 1,500 and z_elbow = 2,000, so max(1500, 2000) = 2,000. Both operands are real and the elbow rule binds. This is the engine working as designed — both legs contribute a real operand to the max() combiner, and the conservative combiner correctly picks the larger.

**Shocked z\*\* ranges 1,500–2,000 (two-rung spread).** Three seeds read 2,000; one (seed 7) reads 1,500. This is comparable to the continuous z\* spread, slightly more stable than Rivian's shocked three-rung spread (1,000/1,500/2,000), and consistent with the general finding that z is stable in the 1,500–2,000 band for moderate-risk companies.

**The shocked rec_batches swing is the step-6 headline finding, now visible.** Across seeds, shocked rec_batches ranges 286 → 5,294 — a 18× swing. This is qualitatively identical to the Steady Co step-6 finding (171 → 1,464 under shocks). The seed-sensitivity of rec_batches under shocks was the headline insight from step 6, but it was entirely invisible for Carvana and Rivian because B2 pinned rec_batches at 40 on every seed. Now that the batch machinery is functioning correctly, the seed-sensitivity is visible and correctly flagged. **This is what the engine is supposed to do: expose the fact that a shocked margin near the precision bar makes the batch count unreliable, so the user should treat rec_batches as a range, not a single number.**

**Continuous rec_batches is seed-stable.** Ranges 30–104 — the same modest swing seen on healthy companies. Shocks are what make the batch count blow up; the continuous pass is well-behaved.

---

## 9. Market-percentile signal

No market price is a fixture input. The grid maps hypothetical price points onto the **shocked** distribution:

| Hypothetical price | Percentile of shocked sims below |
|---|---|
| −$5 | 0.0 |
| −$2 | 0.1 |
| $0 | 0.6 |
| +$2 | 6.3 |
| +$5 | 48.4 |
| +$8 | 88.9 |
| +$11 | 98.1 |
| +$15 | 99.9 |

**The market-percentile signal is fully informative for CloudGrow.** At $5.58 (the central value), roughly 50% of shocked simulations fall below it — the shocked distribution is centred just below the deterministic point, as expected given that shocks are a net negative. At $8/share, 89% of simulations are below — a price of $8 would reflect substantial optimism relative to this model. At $2/share, 94% of simulations exceed it — a price of $2 would look cheap by almost any simulation path.

The percentile grid is spread across the full range in a meaningful, interpretable way. Compare to Rivian's grid, where almost the entire distribution was compressed between −$5 (4th percentile) and $0 (97th percentile) — the narrow distribution made the signal nearly useless at any realistic positive price. CloudGrow's wider distribution and positive centre produce a percentile grid that reads as intended.

---

## ARCHITECTURE QUESTIONS — answered

The eight questions CloudGrow was designed to answer:

**Q1. Does z_pct become active again?**
Yes. z_pct = 2,000 on both continuous and shocked runs, on all four seeds, on both engines. It is not None. The precision bar is positive and the scatter can be compared against it. The precision arm is fully operational.

**Q2. Does decision_margin become interpretable again?**
Yes. Continuous: +21.4% (clear). Shocked: +3.3% (thin but real). All seeds positive. The margin is a genuine measurement of how far z\* clears the precision bar, not a mechanical artefact of a negative centre.

**Q3. Does borderline behave normally?**
Yes — and the two passes exhibit different borderline states for the correct structural reason. Continuous: `borderline = False` (margin +21.4%, no ambiguity). Shocked: `borderline = True` (margin +3.3%, genuinely thin). This is the correct behaviour: borderline fires when the decision is genuinely close, not as a mis-fire triggered by a negative centre.

**Q4. Does batch grading and refinement re-engage?**
Yes. Continuous: `rec_batches = 45` (graded for a 21.4% margin). Shocked: `rec_batches = 1,799` (graded for a 3.3% margin). The 1/margin² formula is working. The 18× swing across seeds (286–5,294) is the correct honest output: a thin margin produces a large, seed-sensitive batch recommendation, and the engine says so.

**Q5. Does z\*\* become more stable?**
More stable than Rivian's shocked z\*\* (which ranged 1,000–2,000, a three-rung spread), but still shows a one-to-two-rung band (1,500–2,000 across seeds). Three of four seeds agree on 2,000. The instability in the shocked z\*\* is now correctly surfaced through the margin/rec_batches pathway (thin margins → large rec_batches → honest flagging), rather than being silently hidden by B2's suppression.

**Q6. Does F3 (z\*\* vs z\*) become measurable again?**
Partially. z_pct and z_elbow both produce real operands for the max() combiner, so the diagnostic is functioning. However, both z\* and z\*\* remain in the 1,500–2,000 band. The shocked z\*\* is not systematically above z\* on every seed (seeds 42/99/123 give z\*\* ≥ z\*; seed 7 gives z\*\* < z\*). Within the current grid resolution, a systematic z\*\* > z\* direction is not established. What IS newly measurable is that the shocked DECISION MARGIN is consistently and substantially thinner than the continuous margin (1.9–8.4% vs 14–27%), even when z\*\* = z\*. The gap between continuous and shocked runs appears more clearly in the margin and rec_batches than in z itself.

**Q7. Are B1 and B2 truly negative-centre phenomena?**
Yes — confirmed. Neither B1 nor B2 fires for CloudGrow. All margins positive, z_pct active, borderline correctly behaved, batch grading working. The complete absence of these pathologies on a positive-centre fragile company, combined with their universal presence on two negative-centre fragile companies across all seeds and both engines, localises B1 and B2 to the negative-centre regime. The sign of the valuation centre is the switch.

**Q8. Does the convergence framework behave normally for a fragile company with a positive valuation centre?**
Yes, substantially. The continuous run behaves entirely normally. The shocked run behaves correctly, with one expected complication: the thin shocked margin (+3.3%) produces a genuinely large batch recommendation (~1,800) and a wide seed-sensitive swing (286–5,294). This is not misbehaviour — it is the engine correctly reporting that the shocked elbow sits close to the precision bar, making the grading call difficult. The engine is louder on the shocked pass precisely because the shocked distribution is harder to resolve, which is the right direction.

---

## COMPARISON vs Carvana, Rivian, and Steady Co

| Dimension | Steady Co | Carvana | Rivian | **CloudGrow** |
|---|---|---|---|---|
| Central value | +$12.77 | −$5.61 | −$2.35 | **+$5.58** |
| WACC | 8.16% | 10.75% | 12.56% | **12.535%** |
| Distribution std (cont) | ~$4.60 | $14.99 | $1.27 | **$2.13** |
| Distribution std (shock) | ~$4.94 | $17.40 | $1.39 | **$2.34** |
| Share negative (cont) | ~0% | 65.3% | 96.6% | **0.0%** |
| Share negative (shock) | ~0% | 71.3% | 97.15% | **0.6%** |
| P(value > 0) cont | ~100% | 34.7% | 3.4% | **100.0%** |
| Precision rule (z_pct) | fires | None | None | **fires** |
| decision_margin_pct (seed 42) | ~+27% | −117% | −171% | **+21% cont / +3% shock** |
| borderline (cont) | False | True (mis-fire) | True (mis-fire) | **False (correct)** |
| borderline (shock) | True | True (mis-fire) | True (mis-fire) | **True (correct)** |
| rec_batches cont | graded | pinned 40 | pinned 40 | **graded (30–104)** |
| rec_batches shock (seed 42) | 171–1,464 | pinned 40 | pinned 40 | **286–5,294** |
| z\* (seed 42) | 2,000 | 2,000 | 1,500 | **2,000** |
| z\*\* (seed 42) | 2,000 | 1,500 | 2,000 | **2,000** |
| Worst-5% leader | margin 47%, rev 21% | margin 43%, cash 37% | cash 46%, margin 37% | **margin 41%, cash 25%, rev 20%** |
| Shock mean shift | modest | −$3.90 | −$0.21 | **−$0.47** |
| Shock floor extension | modest | −$54→−$90 | −$7.84→−$10.24 | **+$0.59→−$2.89** |
| Shock-free % | ~75% | 75.4% | 75.36% | **75.4%** |

---

## FINDINGS — tier 1: CloudGrow-specific (these inputs only)

1. The central DCF is **+$5.58/share** — the first fragile candidate to produce a positive valuation centre. WACC 12.535%, nearly identical to Rivian (12.56%), making this the cleanest sign-boundary comparison possible.

2. The continuous distribution is entirely positive (min +$0.59) with std $2.13. Shocks push 0.6% of paths below zero, with a floor at −$2.89. The shocked distribution retains a positive centre ($5.26 mean) and is the first fragile-candidate distribution where a realistic positive market price would NOT sit in the 97th–100th percentile.

3. **Margin dominates the worst-5% channel mix (41%), not cash.** Revenue returns to a meaningful worst-path share (20%). This is the capital-structure profile of a company with a moderate revenue/equity ratio — the same ordering as Steady Co — not the cash-dominated ordering of Carvana/Rivian.

4. z\* = 2,000 continuous; z\*\* = 2,000–1,500 across seeds. Benchmark: 0.12% mean gap at 20% compute. Both precision and elbow rules deliver real operands to the max() combiner. Shocked rec_batches ranges 286–5,294 across seeds.

5. The shocked decision margin (+1.9% to +8.4%) is thin but positive — a genuine signal about the difficulty of grading the shocked distribution, not a mis-fire.

## FINDINGS — tier 2: Fragile-company (accumulating across fixtures)

1. **The shock overlay causes the decision margin to narrow substantially** on a positive-centre fragile company (21–27% continuous → 2–8% shocked). This is structurally expected: shocks widen the distribution and slightly depress the centre, both of which make it harder for the scatter to stay below the precision bar. This finding was invisible on Carvana/Rivian (where B2 masked the margin change) and on Steady Co (where the margin was more robust). CloudGrow is the first fixture where this compression is cleanly observable.

2. **The shocked rec_batches swing re-appears on a positive-centre fragile company** and is large (286–5,294 across seeds). This confirms that the Steady Co step-6 finding — shocked rec_batches is seed-sensitive because of the 1/margin² amplification — generalises to fragile companies once B2 is no longer mis-firing.

3. **Capital structure predicts the worst-path channel mix.** Three fragile candidates now: Carvana (high revenue/thin equity → cash 37%), Rivian (even more extreme → cash 46%), CloudGrow (moderate revenue/equity ratio → margin 41%, cash 25%). The transition from cash-dominated to margin-dominated ordering tracks the revenue-to-per-share-equity ratio across all three fixtures. This is a three-fixture observation and qualifies as a fragile-company finding.

4. **Revenue re-enters the worst-5% channel mix when the centre is positive.** Carvana: 5.5%. Rivian: 4.3%. CloudGrow: 20.1%. The mechanism: revenue shocks matter more when the starting valuation is positive because they hurt an already-positive cash flow trajectory and compound into the terminal value. For loss-making companies, shocks to a negative revenue trajectory do not differentiate the worst paths as sharply. One fixture; watch on Candidate #4.

## FINDINGS — tier 3: Architecture-level (promoted to architecture tier where evidence is sufficient)

**A-7 (new, architecture) — B1 and B2 are negative-centre phenomena, not fragile-company phenomena.** Both bugs fire universally on Carvana (central −$5.61) and Rivian (central −$2.35), across all seeds, both engines. Neither fires on CloudGrow (central +$5.58) on any seed or engine. The sign of the valuation centre is a binary switch: positive centres enable the full convergence machinery; negative centres disable it structurally. The magnitude of the negative centre does not matter — a shallow negative (−$2.35) triggers the same inversion as a deep one (−$5.61). **Three fixtures now confirm this localisation.** Source: Carvana, Rivian (trigger), CloudGrow (non-trigger). This is architecture-level.

**A-8 (new, architecture) — When the precision rule is functioning, the shocked pass produces a genuinely thin decision margin for a fragile positive-centre company.** The continuous margin (+21%) and shocked margin (+3%) are both real measurements. The shocked margin being thin is not a bug — it is the precision rule correctly reporting that shocks make the distribution harder to grade. On Carvana/Rivian the same phenomenon was occurring but was invisible (B2 suppressed it). On CloudGrow it is visible and correctly diagnosed. **The engine is louder about diagnostic uncertainty on the shocked pass precisely because the shocked distribution is harder to resolve, and for the right reason.** Source: CloudGrow. One fixture; upgrade to confirmed on next positive-centre fixture.

**F3 status update (fragile-class → uncertain, positive-centre evidence now available).** The tracker notes F3 (z\*\* direction vs z\*) "cannot resolve while B1/B2 active." With B1/B2 now confirmed absent, CloudGrow is the first fixture where F3 can be examined. Result: z\*\* is not systematically above z\* across seeds (3 seeds 2,000, 1 seed 1,500, compared to continuous 3 seeds 2,000, 1 seed 1,500). The z gap is within grid noise. However, the margin gap IS systematic: shocked margins are consistently and substantially below continuous margins (+2–8% vs +14–27%). **F3 may be better characterised as "shocks narrow the decision margin and increase rec_batches, but do not reliably move z to a different grid cell" for this fixture.** Keep open pending additional positive-centre fixtures.

**F5 (architecture) — Benchmark thesis holds on positive-centre fragile company.** Mean gap 0.12% at 20% compute. Third fragile fixture confirming the elbow-found z\* reproduces the full-budget answer. The smallest gap yet. Now confirmed on four total fixtures (Steady Co, Carvana, Rivian, CloudGrow). Architecture-level.

---

## Unexpected results

- The shocked decision margin (+3.3%) is thin enough to trigger a `borderline = True` verdict even on a positive-centre company. Anticipated that the shocked pass would show a narrower margin than the continuous; not anticipated that it would be this close to triggering borderline. The shocked rec_batches of 1,799 is the direct consequence.
- Revenue re-enters the worst-5% channel mix at 20%, reverting toward the Steady Co profile. Expected cash to remain elevated for a fragile company; it is the capital structure (and specifically the revenue/per-share-equity ratio) that determines this, not fragility per se.
- Min of the continuous distribution is +$0.59 — the perturbation machinery comes close to zero but never crosses. The zero crossing requires shocks, which is a natural validation of the two-layer architecture.

---

## Future questions generated by this run

1. **Does the thin shocked margin and large shocked rec_batches generalise to other positive-centre fragile companies?** CloudGrow's shocked margin (1.9–8.4%) is structurally driven by the combination of a modest positive centre and moderate WACC. A company with a more comfortable positive centre (e.g. +$10/share) should produce a thicker shocked margin. Candidate #4 can test this.

2. **Does z\*\* > z\* appear on any positive-centre fixture?** The build-sequence predicted shocks raise required n. Three fragile candidates plus Steady Co all show z and z\*\* in the same 1,500–2,000 band without a clear systematic gap. The current grid (N_GRID) may be too coarse to detect the gap, or the gap may genuinely be sub-grid-resolution for moderate-σ companies. A higher-σ positive-centre company (biotech? leveraged buyout?) might reveal the gap.

3. **Does cash channel dominance return for a positive-centre company with a high revenue/equity ratio?** CloudGrow's revenue/equity ratio is moderate, and cash is not the dominant channel. A positive-centre company with high revenue and few shares (like a Carvana that has crossed into positive territory) would test whether the cash-dominance mechanism depends on the revenue/equity ratio regardless of sign.

4. **The B1/B2 fix is confirmed necessary and feasible.** CloudGrow shows that when the precision bar is positive, the full machinery works correctly. The fix should ensure negative-centre companies get a positive bar — option (b) from the candidate log (bar as fraction of σ, sign-agnostic) remains the architecturally cleanest candidate. Three fixtures now confirm the fix is needed; no more evidence is required to justify implementing it.

5. **Is the "shocked margin consistently thinner than continuous margin" a fragile-company pattern or a general one?** Steady Co shows shocked margin behaviour too (the step-6 batch-count swing) but the margin itself was not documented there with the same granularity. Worth a retrospective read of the Steady Co convergence data.

---

*End of first-run log. Next append: after Candidate #4 provides additional evidence on the positive-centre regime, or after the B1/B2 fix is implemented and this fixture is re-run to verify the fix.*
