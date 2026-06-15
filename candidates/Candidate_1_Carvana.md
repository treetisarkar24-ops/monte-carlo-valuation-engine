# Candidate #1 — Carvana

**A permanent research log for the first fragile-company case study run through the Monte Carlo Valuation Engine.**

**Status:** Open / living document. Append, don't overwrite.
**First run:** 2026-05-31. Engine state: steps 2–6 complete and locked (deterministic DCF + perturbation MC + convergence z\* + micro-shock overlay + shocked re-convergence z\*\*).
**Run artefacts:** `candidate1_carvana_run.py` (staged runner), `candidate1_carvana_results.json` (machine-readable dump). Every number below is read from that dump.

---

## 0. Framing — read before trusting any number here

Carvana is a **fixture for architecture exploration, not an investment recommendation.** These inputs are *Carvana-inspired*, not a faithful model of the real company, and nothing here is a view on the stock.

The governing discipline of this log: **Carvana outputs are not architecture truths.** Steady Co — the synthetic teaching fixture (a tame, positive-value firm) — validated that the machinery *runs*. Carvana's job is different: it is the first genuinely fragile company, and the question is what fragility reveals about the framework that a healthy fixture structurally *could not*. Where a finding is specific to these inputs it is filed under "Carvana-specific". Where it is a property of fragile companies generally, "Fragile-company". Where it is a property of the engine, "Architecture-level". The three are kept separate on purpose.

The single most important result of this run is an **architecture-level** one, surfaced only because Carvana's central valuation is negative — a regime Steady Co never enters.

---

## 1. Inputs & assumptions

| Field | Value |
|---|---|
| starting_revenue | 20,300 |
| net_debt | 5,000 |
| shares_outstanding | 220 |
| forecast_years | 5 |
| revenue_growth | 20%, 15%, 10%, 6%, 4% |
| operating_margin | 4%, 5%, 6%, 7%, 8% (ramping) |
| capex_pct_revenue | 3% flat |
| da_pct_revenue | 1.5% flat |
| nwc_pct_revenue | 3% flat |
| tax_rate | 25% |
| terminal_growth | 2.5% |
| risk_free_rate | 4% |
| equity_risk_premium | 5.5% |
| beta | **2.2** |
| cost_of_debt | 8.5% |
| debt_to_total_capital | **55%** |

**Derived:** WACC = **10.75%**. The fragility is wired into the inputs in four reinforcing ways: a high beta (2.2) and a heavy, expensive debt load (55% weight at 8.5%) push the discount rate up; thin early margins (4% ramping to 8%) mean the explicit-period cash flows are weak; and a large net-debt and revenue base sit on a thin share count (220m). The valuation is therefore dominated by the back end and is acutely sensitive to the discount rate and to anything that touches the balance sheet.

**Convergence/run settings:** `N_GRID = [100, 250, 500, 1000, 1500, 2000, 3000, 5000, 7500, 10000]`, `BATCHES_PER_N = 40`, base shock hazard 0.0115/channel/year, stress sensitivity 1.0, equal fragility weights (V1). Convergence seeded by default (42); refinement re-run disabled for this first pass (`rerun=False`) to keep each sweep bounded — see Architecture finding A-4.

---

## 2. Deterministic central case

| | Carvana | Steady Co (ref) |
|---|---|---|
| Central per-share | **−$5.61** | +$12.77 |

Carvana's base-case DCF already puts the equity **underwater**: at the central inputs, discounted free cash flows plus terminal value do not cover net debt, so equity value per share is negative. This is not an artefact of the Monte Carlo — it is the deterministic engine's single-point answer. It is also the fact that drives almost everything downstream, because the convergence module's precision rule is defined relative to the *valuation level*, and that level is now negative.

---

## 3. Continuous-only Monte Carlo (perturbation, no shocks)

Production run at z\* = 2,000, seed 42, n = 2,000.

| Statistic | Value |
|---|---|
| Mean | −$5.43 |
| Median | −$6.05 |
| Std dev | $14.99 |
| Min / Max | −$54.20 / +$52.39 |
| 5th–95th pctile | **−$29.13 → +$19.90** |
| 10th / 25th | −$23.78 / −$15.74 |
| 75th / 90th | +$4.11 / +$13.56 |
| Share of sims **negative** | **65.3%** |
| P(value > 0) | 34.7% |

```
  -54.20 | # 4
  -43.54 | ## 11
  -38.21 | ###### 41
  -32.88 | ######## 56
  -27.55 | ################### 127
  -22.22 | ############################### 214
  -16.89 | #################################### 247
  -11.56 | ########################################## 287
   -6.23 | ####################################### 267
   -0.91 | ##################################### 254
    4.42 | ########################### 183
    9.75 | ################### 133
   15.08 | ############ 80
   20.41 | ###### 44
   25.74 | #### 25
   31.07 | ## 11
   36.40 | # 6
   47.06 |  3
```

The continuous distribution is broad and only mildly skewed — a roughly bell-shaped cloud whose **centre of mass sits below zero**. Two-thirds of perturbation-only paths value the equity at less than nothing. The peak (the engine's "most likely value") is around −$6 to −$11.

## 4. Shocked Monte Carlo (perturbation + micro-shock overlay)

Production run at z\*\* = 1,500, seed 42, n = 1,500.

| Statistic | Continuous | **Shocked** | Δ |
|---|---|---|---|
| Mean | −$5.43 | **−$9.33** | −$3.90 |
| Median | −$6.05 | −$9.23 | −$3.18 |
| Std dev | $14.99 | $17.40 | +$2.41 |
| Min | −$54.20 | **−$89.78** | −$35.58 |
| Max | +$52.39 | +$60.21 | — |
| 5th pctile | −$29.13 | −$37.71 | −$8.58 |
| 95th pctile | +$19.90 | +$17.86 | −$2.04 |
| Share negative | 65.3% | **71.3%** | +6.0pp |
| Shock-free paths | — | 75.4% | — |

```
  -89.78 |  1
  -67.28 | # 7
  -59.79 | ## 10
  -52.29 | ### 20
  -44.79 | ###### 42
  -37.29 | ############# 86
  -29.79 | ###################### 141
  -22.29 | #################################### 234
  -14.79 | ########################################## 273
   -7.29 | ######################################### 269
    0.21 | ############################# 190
    7.71 | ################### 126
   15.21 | ######### 56
   22.71 | #### 23
   30.21 | ## 14
   52.71 |  3
```

The shock overlay does exactly what it is designed to: it bites **asymmetrically on the left.** The right tail barely moves (95th pctile −$2), while the floor collapses from −$54 to **−$90** and the mean drops nearly $4. 25% of the shock fixture's paths land in shock cascades (24.6% non-shock-free) and those paths are precisely the ones in the new, deep left tail. Mean accumulated stress 0.15, max stress 3.12 — death-spiral paths (repeated, escalating hits) are present and are what produce the −$60 to −$90 sliver.

## 5. Convergence — z\*, z\*\*, decision margins

| | Continuous (z\*) | Shocked (z\*\*) |
|---|---|---|
| z (headline) | 2,000 | **1,500** |
| z_pct (precision rule) | **None** | **None** |
| z_elbow | 2,000 | 1,500 |
| decision_margin_pct | **−116.9%** | **−121.9%** |
| precision_bar | **−$0.055** | **−$0.090** |
| centre (mean of run-means) | −$5.48 | −$9.01 |
| sigma_estimate | $15.44 | $17.29 |
| borderline flag | **True** | **True** |
| batches_recommended | 40 | 40 |
| adequately_resolved | True | True |

This table is where the run earns its keep, and it needs reading carefully because several fields are **pathological, not informative**:

- **z_pct = None in both runs.** The precision rule ("smallest n whose scatter falls under 1% of the valuation") never fires, because the bar is 1% of a *negative* centre → a **negative precision bar** (−$0.055, −$0.090). Scatter is a standard deviation and is always positive, so it can never fall "below" a negative bar. The entire precision arm of the convergence criterion is silently disabled.
- **z\* therefore collapses to z_elbow alone.** With z\* = max(z_pct, z_elbow) and z_pct = None, the conservative `max()` combiner has only one operand. Both z values are pure elbow reads.
- **decision_margin_pct is negative (−117% / −122%)** and `borderline = True` — again a mechanical consequence of the negative bar, not a measured "this company sits on the precision threshold". The borderline short-circuit then pins `batches_recommended` at the default 40 and reports `adequately_resolved = True`, which here means "no refinement attempted", **not** "the answer is well-resolved".

So the honest reading is: **for this fixture the convergence module is running on one leg (the elbow) and reporting confidence it has not actually earned.** z\* = 2,000 and z\*\* = 1,500 are real elbow locations of genuine σ/√n decay curves (the scatter columns decay cleanly: 1.76 → 0.11 continuous, 1.71 → 0.17 shocked), so they are not garbage — but the surrounding precision/margin/borderline apparatus is mis-firing.

**Does z\*\* separate from z\*?** Only by one grid rung, and **in the opposite direction to the design's expectation** (z\*\* = 1,500 < z\* = 2,000). The handoff anticipated shocks fattening tails → raising required n → z\*\* > z\*. That did not happen here. The elbow of the shocked decay curve sits at 1,500 because the shocked curve starts higher and bends sooner, not later. Within grid resolution the two are effectively the same; the meaningful finding is not the gap but that **both legs of the criterion that should detect a gap are disabled by the sign of the valuation.**

## 6. Benchmark vs the folk 10,000 (continuous)

| | z\* = 2,000 | Folk 10,000 |
|---|---|---|
| Mean | −$5.426 | −$5.476 |
| Median | −$6.052 | −$6.068 |
| Compute ratio | **0.20** | 1.00 |
| Mean gap | **0.92%** | — |

The headline thesis **survives the fragile case**: running at the company-specific z\* uses 20% of the folk compute and lands within 0.9% of the 10,000-run mean. The convergence module's *output* (z\*) is usable even though its internal precision-rule *diagnostics* are broken — the elbow still finds a sample size that reproduces the full-budget answer. Worth stating precisely: the engine got the right n for the wrong reasons here.

## 7. Shock-channel behaviour

5,000 paths, seed 42. Fires are near-equal across channels by design (equal hazards, equal weights). The story is in the **worst 5% of paths**:

| Channel | All fires | Worst-5% share | Steady Co worst-5% (ref) |
|---|---|---|---|
| **margin** | 300 (19.8%) | **43.3%** | 47% |
| **cash** | 329 (21.7%) | **37.1%** | 15% |
| strategic | 290 | 6.5% | 10% |
| funding | 294 | 5.9% | 7% |
| revenue | 301 | 5.5% | 21% |

This is the most interesting fragile-company result after the negative-centre finding. **The worst-path channel mix is materially different from Steady Co's.** For Steady Co, margin (47%) and revenue (21%) drove the worst cascades and cash sat at 15%. For Carvana, **cash leaps to co-dominant (37%) and revenue collapses to 5.5%.**

The mechanism is structural and traces straight to the inputs. The cash channel applies a one-off outflow **sized as a fraction of that year's revenue** (`net_debt += damage × revenue`). Carvana's revenue (~$20–24bn across the forecast) is enormous relative to its thin equity cushion (220m shares, $5bn net debt, negative central equity). So a single cash shock of 5–25% of revenue dumps $1–6bn onto net debt — catastrophic per-share. The same channel barely registered for Steady Co because Steady Co's revenue ($1bn) is small relative to its equity. **The funding/cash survival-threat the step-5 design hypothesized — but which the Steady Co trip-wire showed funding/cash *failing* to deliver — actually materializes here, through the cash channel, purely because of capital structure.**

## 8. Seed observations (z stability)

Four seeds, B = 40, `rerun=False`:

| seed | CONT z\* | CONT margin% | SHOCK z\*\* | SHOCK margin% |
|---|---|---|---|---|
| 42 | 2,000 | −116.9 | 1,500 | −121.9 |
| 99 | 2,000 | −115.6 | 1,500 | −123.5 |
| 123 | 1,500 | −119.0 | 1,500 | −125.4 |
| 7 | 2,000 | −117.9 | 1,500 | −128.2 |

- **z\*\* is rock-stable at 1,500 on every seed.** z\* wobbles between 1,500 and 2,000 (one grid rung). Both bands overlap — consistent with the step-6 finding that, at this grid resolution, continuous and shocked required-n move together.
- **Decision margins are uniformly, stably negative (−116% to −128%)** — the pathology is reproducible, not a one-seed fluke. Shocked margins are consistently slightly *more* negative than continuous (the shocked centre is more negative, so the negative bar is deeper).
- **rec_batches pinned at 40 on every seed/engine.** Contrast Steady Co, whose shocked rec_batches swung 171→1,464 across seeds. Here the **borderline short-circuit suppresses the batch-grading machinery entirely** — a negative centre trips `borderline=True`, which skips the recommendation logic. So the seed-sensitivity of rec_batches that was the headline step-6 architecture finding is *invisible* for this company, masked by the same negative-centre bug.

## 9. Market-percentile signal

No market price is a fixture input, so the signal is reported as a grid mapping a hypothetical price onto the **shocked** distribution (read: at price P, X% of simulated valuations fall below P):

| Hypothetical price | Percentile of shocked sims below |
|---|---|
| −$5 | 60.0 |
| −$2 | 66.6 |
| $0 | 71.3 |
| +$2 | 76.1 |
| +$5 | 81.0 |
| +$8 | 85.3 |
| +$11 | 89.2 |
| +$15 | 92.8 |

Architecture note: the project's signature signal — "where does today's price sit inside the distribution of intrinsic values?" — is **well-defined even when the distribution is mostly negative.** Any positive real-world market price would sit in the high-70s percentile or above, i.e. the model would read the equity as expensive relative to most simulated paths. The percentile machinery does not break on a negative-valued distribution, unlike the precision-rule machinery; the comparison is purely an empirical rank and is sign-agnostic.

---

## FINDINGS — tier 1: Carvana-specific (these inputs only; NOT architecture truths)

1. The central DCF is **−$5.61/share**; the perturbation-only distribution is centred at −$5.4 with 65% of paths negative; the shocked distribution at −$9.3 with 71% negative. Under these fragile inputs the engine reads the equity as worth less than nothing on the majority of paths.
2. WACC 10.75% (beta 2.2 + 55% debt at 8.5%) plus thin ramping margins is the proximate driver: the explicit period throws off little cash and the discount rate is high, so net debt dominates the equity bridge.
3. **Cash is a co-dominant worst-path channel (37%)** for Carvana specifically, because its huge revenue base sizes the cash-outflow shock against a thin equity cushion.
4. z\* = 2,000 (continuous), z\*\* = 1,500 (shocked) under default seeds; the benchmark confirms z\* reproduces the folk-10,000 mean to within 0.9% at 20% compute.

## FINDINGS — tier 2: Fragile-company (likely generalize to other fragile names; to be confirmed on Candidate #2)

1. **Shocks bite asymmetrically and hard on a fragile company.** The left tail extended from −$54 to −$90 and the mean fell ~$4, while the right tail was untouched. A fragile firm's downside is dominated by discrete-event cascades, not by smooth perturbation.
2. **A fragile company can be valued below zero across most of its distribution** — meaning the interesting quantity stops being "the per-share value" and becomes "the probability the equity is worth anything" (here ~35% continuous, ~29% shocked). Fragile-company reporting should lead with P(value > 0), not the mean.
3. **Which channel kills depends on capital structure, not on the channel hazards.** Equal hazards still produced a wildly unequal worst-path mix, and the mix differs from Steady Co's because the *transmission* of each channel interacts with the balance sheet. The cash channel's revenue-sizing makes it lethal for high-revenue/thin-equity firms.
4. Stress cascades (max stress 3.1) are a real, populated part of the distribution for a fragile firm, where for Steady Co they were a thin sliver.

## FINDINGS — tier 3: Architecture-level (properties of the engine, exposed by fragility)

**A-1 — The convergence precision rule breaks for non-positive valuations.** `precision_bar = 0.01 × centre` goes negative when the centre is negative, so `z_pct` (scatter < bar) can never fire and `decision_margin_pct` becomes a meaningless negative number. The engine then silently runs on `z_elbow` alone and the conservative `max(z_pct, z_elbow)` combiner is reduced to a single operand. **Steady Co (centre +$12.75) could never expose this** — a positive centre always yields a positive bar. This is the headline architecture insight of the run.

**A-2 — The `borderline` flag mis-fires on negative centres.** Designed to mean "z\* sits right on the precision bar, no batch count can sharpen it", it instead trips because the (negative) margin is below threshold for a structural reason. The mis-fire then suppresses the entire batch-grading / refinement pathway (`batches_recommended` pinned at 40, `adequately_resolved = True`). So a fragile company gets *less* convergence scrutiny than a healthy one, exactly backwards from what its fat tails warrant.

**A-3 — "adequately_resolved = True" is not trustworthy in this regime.** It currently means "no refinement was attempted" rather than "the answer is well-resolved". For a negative-centre company the honest verdict machinery reports false comfort.

**A-4 — The elbow leg is robust; the price/percentile leg is sign-agnostic and also robust.** Two of the engine's three measurement ideas survive a negative valuation intact: the σ/√n elbow still locates a usable z (benchmark-confirmed), and the market-percentile rank is a pure empirical ordering that does not care about sign. Only the *relative-precision* idea (1% of valuation) is sign-fragile. This localizes the fix.

**A-5 — z\*\* did not exceed z\* here**, contradicting the build-sequence expectation. The shocked decay curve bends one grid rung *earlier*, not later. Whether this is a fixture quirk or a general fragile-company behaviour is unknown — flagged for Candidate #2.

---

## Unexpected results (call-outs)

- z\*\* **<** z\*, not >. (Expected the opposite.)
- The negative central value silently disabling half the convergence criterion — not anticipated anywhere in the handoff; Steady Co's positive centre had hidden it for the entire build.
- Cash overtaking revenue as a worst-path channel (37% vs 5.5%), reversing the Steady Co ordering, driven entirely by capital structure × the cash channel's revenue-sizing.
- The borderline/refinement machinery going *quieter* on the fragile company than on the tame one.

## Differences vs the Steady Co fixture (summary)

| Dimension | Steady Co | Carvana |
|---|---|---|
| Central value | +$12.77 | −$5.61 |
| Distribution centre | positive, mild right-skew | negative, broad |
| Precision rule (z_pct) | fires normally | **disabled (None)** |
| decision_margin | positive (~+27%) | **negative (~−120%)** |
| borderline | meaningful | **mis-fired** |
| rec_batches across seeds | swings 171–1,464 (shocked) | pinned at 40 (suppressed) |
| Worst-5% channel leader | margin 47%, revenue 21% | margin 43%, **cash 37%** |
| Shock effect on tail | left tail sinks modestly | left tail collapses (−$54→−$90) |
| z\* → z\*\* | same band, "shocks didn't move it" | z\*\* one rung **lower** |

## Future questions generated by this run

1. **Fix or guard the precision rule for non-positive valuations.** Options to weigh: bar as a fraction of |centre|; bar as a fraction of σ rather than of the valuation level (scale-free and sign-agnostic — possibly the cleaner anchor); or an explicit "valuation straddles/falls below zero" branch that reports the precision leg as N/A instead of silently emitting a negative bar. Which preserves the thesis most honestly?
2. **Decouple `borderline` from the sign of the centre** so the batch-grading machinery still runs for fragile companies (they need it *more*, not less).
3. **Should the headline output flip for fragile names** from "per-share value" to "P(value > 0)" and the percentile rank? The mean of a mostly-negative distribution is a weak summary.
4. **Re-examine the cash channel's revenue-sizing.** Is sizing a one-off cash shock off revenue right when revenue dwarfs equity? Should it be sized off a balance-sheet quantity, or PV-discounted (the documented V1 simplification)? Carvana makes this choice load-bearing.
5. **Is z\*\* < z\* a fixture quirk or a fragile-company pattern?** Test on Candidate #2 with a different fragility profile (e.g. a leveraged but positive-value turnaround) and on a positive-value high-variance name to see whether the negative-centre pathology, not fragility per se, is what suppressed the gap.
6. **Does the benchmark thesis hold when z\* is elbow-only?** It did here (0.9% gap), but that is one fixture — confirm the elbow-only path is reliable across fragile names before leaning on it.

---

*End of first-run log. Next append: re-run after the precision-rule guard (question 1) is implemented, to see whether z\*/z\*\* and the margins become interpretable for a negative-valued company.*
