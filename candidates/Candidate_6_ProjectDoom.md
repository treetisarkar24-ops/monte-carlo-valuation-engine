# Candidate #6 — Project Doom (Convergence Stress Test)

**A permanent research log for the sixth case study run through the Monte Carlo Valuation Engine.**

**Classification:** Convergence Stress Test — **Gate Failed (Negative Central Value)**
**Status:** Complete / living document. Append, don't overwrite.
**First run:** 2026-06-01. Engine state: steps 2–6 complete and locked.
**Run artefacts:** Deterministic DCF only. Full pipeline not run (pre-run gate not met).

---

## 0. Framing — read before trusting any number here

Project Doom is a **fixture for architecture exploration, not an investment recommendation.** This is a synthetic company. Nothing here is a view on any real entity.

**Primary architectural objective.** Every prior candidate was designed to stress a different part of the engine — negative centre (Carvana, Rivian), positive-centre boundary crossing (CloudGrow), high-beta positive fragility (MedTechX), revenue-scale amplification (RetailRollup). Project Doom was designed for a single, focused question: **can the current convergence architecture recognise when the N_GRID itself is insufficient?**

The intended mechanism: a company with beta = 4.0 would produce a WACC of ~21.4% and a distribution sigma wide enough that z\* and z\*\* would be driven to the top rung of N_GRID (n = 10,000). Reaching the top rung while still showing thin margins, a live borderline flag, and evidence that the scatter has not yet converged would constitute evidence that the true convergence requirement lies beyond the grid. The stretch goal was credible evidence that the true requirement is in the 15,000–20,000+ range.

**What actually happened.** The pre-run deterministic DCF check produced a **central value of −$13.19/share**. Per the pre-run protocol, the pipeline was stopped. The fixture was not modified. This document records the full analysis of why the gate failed, what the failure reveals architecturally, and what it implies for designing a successful convergence stress test.

---

## 1. Inputs & assumptions

| Field | Value |
|---|---|
| starting_revenue | 1,500 |
| net_debt | 100 |
| shares_outstanding | 50 |
| forecast_years | 5 |
| revenue_growth | 60%, 45%, 35%, 25%, 15% |
| operating_margin | 1%, 3%, 5%, 8%, 12% |
| capex_pct_revenue | 8%, 8%, 7%, 6%, 5% |
| da_pct_revenue | 2% flat |
| nwc_pct_revenue | 6%, 6%, 6%, 5%, 5% |
| tax_rate | 25% |
| terminal_growth | 2.5% |
| risk_free_rate | 4% |
| equity_risk_premium | 5.5% |
| beta | **4.0** (highest of any candidate by a wide margin) |
| cost_of_debt | 10% |
| debt_to_total_capital | 25% |

**Derived WACC:**
- Equity weight = 75%; equity cost = 4% + 4.0 × 5.5% = **26.0%**
- After-tax debt cost = 10% × 0.75 = **7.5%**
- WACC = 0.75 × 26.0% + 0.25 × 7.5% = **21.375%**

This is the highest WACC of any candidate, and it is not close. Prior candidates: RetailRollup 12.845%, MedTechX 14.98%. At 21.375%, the Gordon multiple (1 + g)/(WACC − g) = 1.025 / 0.18875 = **5.43×** — extraordinarily low. A normal WACC produces multiples of 8–13×; here the multiple is halved relative to MedTechX.

**What makes this fixture distinctive (intended).** Three deliberate design tensions, all in the direction of maximum variance and maximum required sample size:

1. **Beta 4.0 — the primary driver.** Not just the highest beta in the register; at 4× the ERP, it is in the range of speculative early-stage venture-type assets or highly leveraged cyclicals. Every perturbation of beta produces a per-simulation WACC swing roughly 1.7× larger than MedTechX's (0.75 × 0.12 × 4.0 × 0.055 ≈ 2.0pp per sigma vs 1.2pp for MedTechX). This was the intended sigma amplifier.

2. **Hyper-growth with heavy investment.** Revenue grows 60%, 45%, 35% in years 1–3 — the steepest growth profile of any candidate. But capex consumes 7–8% of that rapidly expanding base, and NWC consumes 6% every year (as a fraction of total revenue, not just the change). The company invests heavily into its own growth before margins are large enough to fund it.

3. **Thin early margins (1%→12% ramp).** Operating margin is only 1% in year 1, ramping to 12% by year 5. This is the most back-loaded margin profile in the register — all the value creation sits in the terminal period, which must be discounted at 21.375%.

The design logic: all three tensions together would generate a distribution too wide to converge at moderate n, forcing the engine to the top of N_GRID.

---

## 2. Deterministic central case — PRE-RUN CHECK RESULT

### ❌ GATE FAILED — central value = −$13.19/share

Per the pre-run protocol: **"Run deterministic DCF first. If the central valuation is not positive: STOP. Report why. Do not modify the fixture."**

The full pipeline (continuous MC, shocked MC, convergence sweeps, seed study) was NOT run. The analysis below is the explanation of why the gate failed and what it implies.

| | Project Doom | MedTechX (ref) | PowerGridCo 4A (ref) | Steady Co (ref) |
|---|---|---|---|---|
| Central per-share | **−$13.19** | +$6.20 | −$9.62 (also gate-failed) | +$12.77 |
| WACC | **21.375%** | 14.98% | 10.345% | 8.16% |
| Net debt/share | **$2.00** | $0.75 | $20.00 | $3.00 |

---

## 3. Why the central value is negative — complete decomposition

The deterministic engine produces:

| Year | Revenue | EBIT | NOPAT | D&A | Capex | DNWC | FCF | Disc. Factor | PV(FCF) |
|------|---------|------|-------|-----|-------|------|-----|-------------|---------|
| 1 | 2,400 | 24 | 18 | 48 | 192 | 144 | **−270** | 1.2138 | −222 |
| 2 | 3,480 | 104 | 78 | 70 | 278 | 209 | **−339** | 1.4732 | −230 |
| 3 | 4,698 | 235 | 176 | 94 | 329 | 282 | **−341** | 1.7881 | −190 |
| 4 | 5,872 | 470 | 352 | 117 | 352 | 294 | **−176** | 2.1703 | −81 |
| 5 | 6,753 | 810 | 608 | 135 | 338 | 338 | **+68** | 2.6342 | +26 |
| | | | | | | | | **Sum PV FCF:** | **−699** |

Terminal value: $367M. PV(TV): **$139M**.

Enterprise value = −699 + 139 = **−$560M**.
Equity value = −560 − 100 = **−$660M**.
Per share = −660 / 50 = **−$13.19**.

Four compounding forces drive the negative outcome:

**Force 1 — WACC destroys the Gordon multiple.** At 21.375%, the Gordon multiple is 5.43×. This means the terminal value — which must be discounted over five years at 21.375% — is tiny relative to what it would be at a normal WACC. Year-5 FCF of $68M produces a TV of only $367M. That same FCF at MedTechX's 14.98% WACC would produce TV ≈ $575M; at Steady Co's 8.16% would produce TV ≈ $1,140M. The 21.375% WACC cuts the terminal value by 37% relative to MedTechX and by 68% relative to Steady Co. PV(TV) = $139M is the result of discounting $367M for five years at 21.375%.

**Force 2 — Cumulative early negative FCFs overwhelm the terminal value.** The sum of PV(early FCFs) = −$699M. Even ignoring the discount rate effect, years 1–4 throw off cumulative nominal FCFs of −270 − 339 − 341 − 176 = −$1,126M. Years 4 and 5 are the only non-deeply-negative years, and year 5's FCF of only $68M is the result of Force 3 below. The terminal value at $139M PV cannot offset a $699M PV hole.

**Force 3 — NWC investment consumes almost all of year-5 NOPAT.** NOPAT in year 5 is $608M (12% margin × $6,753M revenue × 0.75 tax). Yet FCF is only $68M — 89% of NOPAT is consumed by investment: capex ($338M) + NWC ($338M) − D&A ($135M) = $541M net investment. The engine computes NWC as nwc_pct × revenue each year (the level, not the change from prior year). At 5% of $6,753M in year 5, NWC = $338M. This is the same magnitude as capex. Even with 12% margins on $6.75bn revenue, the investment burden leaves only $68M of FCF — a paltry base for a $367M terminal value.

**Force 4 — The fixture's growth story requires investment that never produces free cash during the explicit period.** Revenue grows rapidly (60% → 15%) because the company keeps investing — in capex and in NWC. But the margin ramp (1% → 12%) is too slow to overcome the investment burden during the forecast horizon. Year 5 is the only year with positive FCF. A longer explicit period (10 years) might reveal the company "earning through" its investment phase, but the standard 5-year horizon does not capture this. The company's value is essentially entirely in a post-horizon period that the DCF does not model explicitly.

**The critical geometry.** The question "why is the central value negative?" reduces to: **the sum of PV(FCFs) is −$699M and the PV(TV) is only +$139M.** The terminal value is 80% smaller than the PV hole from early negative FCFs. This is not close — it would require the TV to be 5× larger (PV = $699M, implying nominal TV = $1,840M at WACC = 21.375%) just to break even. That would require FCF_5 × 5.43 = $1,840M → FCF_5 = $339M. But FCF_5 is $68M. Even if margins improved from 12% to 14% in year 5, FCF_5 would still be well below $339M.

### Breakeven analysis

Fixing all inputs except beta and solving for breakeven: **beta = 0.594** (WACC = 7.33%) produces per-share value of exactly $0. Scanning the beta range:

| Beta | WACC | Per share |
|------|------|-----------|
| 1.0 | 9.00% | −$5.70 |
| 1.5 | 11.06% | −$9.28 |
| 2.0 | 13.12% | −$11.17 |
| 2.5 | 15.19% | −$12.21 |
| 3.0 | 17.25% | −$12.79 |
| 3.5 | 19.31% | −$13.08 |
| 4.0 | 21.38% | −$13.19 |

**Three architecture observations emerge from this table:**

1. The fixture is negative at beta = 1.0. This means the negative centre is NOT a consequence of the extreme beta — it would fire with any market-normal beta. Even beta = 1.5 (a moderately above-average company) gives −$9.28/share.

2. The per-share value barely changes from beta = 2.0 to beta = 4.0 (−$11.17 to −$13.19). This is because the terminal value is already so small at high WACCs that further WACC increases produce diminishing additional damage. The loss is dominated by the PV of early negative FCFs, which are discounted more steeply at higher WACC — partially offsetting the additional loss of terminal value.

3. The only way to produce a positive central value with these inputs is a WACC below ~7.3%, requiring beta below ~0.59. **This fixture is fundamentally a negative-centre fixture regardless of beta.** The convergence stress test objective (which requires a positive centre to enable the precision rule and avoid B1/B2) is structurally incompatible with this fixture design.

---

## 4–8. Sections not run (pipeline halted at gate)

Per the pre-run protocol, the following sections have no data:

- **Section 4 — Continuous MC:** Not run.
- **Section 5 — Shocked MC:** Not run.
- **Section 6 — Convergence (z\*, z\*\*, decision margins):** Not run.
- **Section 7 — Benchmark vs folk 10,000:** Not run.
- **Section 8 — Shock channel behaviour:** Not run.
- **Section 9 — Seed robustness:** Not run.
- **Section 10 — Market-percentile signal:** Not run.

---

## 11. Convergence questions — answered with available evidence

Despite the gate failure, the eight questions can be partially answered using the deterministic analysis, the breakeven study, and inference from the prior candidate register.

**Q1. Does z\* reach the top rung?**
Unknown — the engine was not run. However: if the fixture had a positive centre, the extreme beta (4.0) would produce a sigma meaningfully above RetailRollup's $14.94. The estimated WACC volatility per simulation is ~2.0pp (vs ~1.2pp for MedTechX, ~1.5pp for RetailRollup). On a ~$10/share positive central with thin margins, the distribution would be extremely wide. z\* reaching 10,000 was plausible in principle — but **this is a counterfactual that cannot be confirmed from the failed run.**

**Q2. Does z\*\* reach the top rung?**
Same: unknown, for the same reason. The gate prevents the observation.

**Q3. Does borderline remain active at high n?**
Unknown. But the architecture finding from prior candidates (F8, F9) suggests that for a high-sigma positive-centre company, borderline and thin margins would appear even at high n. This is what the fixture was designed to exhibit.

**Q4. Do decision margins remain extremely thin?**
Unknown. With a sigma substantially above RetailRollup's ($14.94) and a central value near zero, margins would likely be thin throughout the grid — the precision bar would be very small (1% of a small positive centre) and the scatter would be large. The condition for thin margins is present in the fixture geometry, but the engine cannot confirm it.

**Q5. Does benchmark quality deteriorate?**
Unknown. But inference from the cross-candidate pattern (wider sigma → larger benchmark gap, up to 0.93% at RetailRollup) suggests the benchmark gap at z\* might approach 1% for the first time. Not confirmable.

**Q6. Does the engine produce evidence that the current grid is too small?**
**No** — because the engine did not run. The pre-run gate is itself the evidence: the architecture correctly identifies that this fixture cannot sustain the precision machinery, and stops. In a different framing, the gate IS evidence — it tells us that beta = 4.0 combined with these investment parameters produces a negative-centre company, which means the architecture cannot run the convergence test without B1/B2 firing. The grid's sufficiency question cannot be answered on a negative-centre fixture.

**Q7. Is there evidence that the true convergence requirement exceeds 10,000?**
**No direct evidence.** The fixture that was designed to produce this evidence could not run. The strongest available inference is from RetailRollup (z\*\* = 7,500, sigma $16.21), which suggests that a company with sigma ~$20+ would push z\*\* to 10,000. Whether the Project Doom fixture would have achieved this (had the central value been positive) cannot be confirmed.

**Q8. Does F9 (z\*\* ≥ z\*) continue to hold?**
Untestable on this fixture. F9 is confirmed on three prior positive-centre fixtures.

---

## 12. Comparison vs all prior candidates

| Dimension | Steady Co | Carvana | Rivian | CloudGrow | MedTechX | RetailRollup | **Project Doom** |
|---|---|---|---|---|---|---|---|
| Central value | +$12.77 | −$5.61 | −$2.35 | +$5.58 | +$6.20 | +$26.16 | **−$13.19** |
| WACC | 8.16% | 10.75% | 12.56% | 12.535% | 14.98% | 12.845% | **21.375%** |
| Beta | 1.1 | 2.2 | 2.0 | 1.9 | 2.4 | 2.2 | **4.0** |
| Equity cost | 10.1% | 16.1% | 15.0% | 14.45% | 17.2% | 16.1% | **26.0%** |
| Net debt/share | $3.00 | $22.73 | $0.83 | $1.00 | $0.75 | $10.00 | **$2.00** |
| Gate passed? | Yes | Yes | Yes | Yes | Yes | Yes | **NO** |
| Pipeline run? | Yes | Yes | Yes | Yes | Yes | Yes | **NO** |
| Breakeven beta | N/A | N/A | N/A | N/A | N/A | N/A | **~0.59** |

The breakeven beta comparison is the most important column in the register. Project Doom is the only fixture where breakeven beta is below 1.0 — meaning no market-normal level of systematic risk would produce a positive centre. The gate failure is structural, not marginal.

Compare to PowerGridCo (4A), the other gate failure: PowerGridCo had a breakeven gate failure driven by a $20/share net debt burden, capex exceeding D&A, and moderate WACC (10.345%). Project Doom's gate failure is driven by a different mechanism — the combination of extreme investment intensity (NWC + capex in a hyper-growth profile) with a tiny Gordon multiple (5.43×) at 21.375% WACC.

---

## 13. FINDINGS — tier 1: Candidate-specific

**C1.** The central DCF is **−$13.19/share**. This is the most negative central value of any candidate, including Carvana (−$5.61) and PowerGridCo (−$9.62). The pre-run gate correctly halts the pipeline.

**C2.** WACC = **21.375%** — the highest WACC of any candidate by a wide margin, driven entirely by beta = 4.0 → equity cost = 26%.

**C3.** The Gordon multiple at this WACC is only 5.43×. Year-5 FCF of $68M produces TV = $367M, PV(TV) = $139M. The terminal value is overwhelmed by PV of early negative FCFs (−$699M).

**C4.** The fixture's negative centre is **not a function of beta.** Even beta = 1.0 (WACC = 9.0%) produces per-share = −$5.70. The structural driver is the NWC + capex investment burden combined with thin early margins — these alone make the explicit period deeply negative at any reasonable WACC. Beta = 4.0 is catastrophic at the margin but not the root cause.

**C5.** Breakeven beta ≈ 0.59 (WACC ≈ 7.33%). The fixture requires a sub-market discount rate to produce a positive centre — economically implausible for any company with beta ≥ 1.

---

## 14. FINDINGS — tier 2: Fragile-company class

**FC-new-1.** A fixture can be structurally negative-centre regardless of its systematic risk (beta) if the investment intensity during the explicit period is high enough. The key relationship: high NWC% × high revenue growth × thin early margins → cumulative negative FCF PV that overwhelms any realistic terminal value at any reasonable WACC. Project Doom is the purest example of this so far. Carvana's negative centre was driven by leverage; Rivian's by early margin losses; PowerGridCo's by capex > D&A and leverage. Project Doom is driven by NWC intensity alone — even at beta = 1.0, WACC = 9%, the company is worth −$5.70/share.

**FC-new-2.** There is a **fixture design dead zone** for convergence stress testing: companies designed to produce high sigma (via extreme beta) are also the companies most likely to fail the positive-centre gate (because high beta → high WACC → lower terminal value multiplier → more likely to be overwhelmed by early investment outflows). The convergence stress test objective (reach the top of N_GRID) requires BOTH high sigma AND positive centre — and these requirements are in tension when sigma is driven by beta rather than revenue scale.

---

## 15. FINDINGS — tier 3: Architecture-level

**A-new-1 (architecture observation).** The pre-run gate and the convergence machinery have a **structural dependency**: the gate requires positive centre, and the convergence machinery requires positive centre (to avoid B1/B2 and enable the precision rule). A company that should require the most convergence scrutiny — extreme beta, maximum sigma — may be the company least likely to clear the gate. This creates a blind spot: the architecture cannot stress-test its own upper grid limits using companies designed around extreme beta alone. Revenue-scale amplification (the RetailRollup mechanism) is a more reliable path to high sigma with positive centre.

**A-new-2 (architecture observation — design principle for future stress tests).** Two paths to high sigma exist, with different gate implications:
- **Beta path:** sigma from WACC volatility. Pro: mechanically clean (raise beta). Con: also raises WACC, lowering TV multiplier, making negative centre more likely. Gate failure risk is high.
- **Revenue-scale path:** sigma from per-share dollar swings on large revenue base. Pro: does NOT raise WACC. A $20bn revenue base on 100m shares produces wide per-share swings purely from the perturbation machinery, without affecting the central DCF. Con: requires a large-revenue positive-centre company. Gate failure risk is low.

RetailRollup (beta 2.2, revenue $18bn, sigma $14.94, z\*\* = 7,500) demonstrates that the revenue-scale path can push z\*\* near the top of N_GRID without creating a negative centre. **The next convergence stress test should use a large-revenue, moderate-beta fixture — not an extreme-beta fixture — to stress the grid reliably.**

**A-new-3 (architecture observation — gate function confirmed).** The pre-run gate fired correctly and cleanly on this fixture. It did not require human judgment — the deterministic DCF alone was sufficient to detect the structural incompatibility. The gate is doing its job: it blocks the convergence machinery from running on fixtures where the precision rule would be disabled (B1/B2), and it does so before any expensive convergence sweeps are run. The two gate failures (PowerGridCo, Project Doom) now provide the clearest evidence of the gate's value: both were architecturally designed for a stated purpose that required a positive centre, and both failed cleanly before wasting compute.

---

## 16. Architecture questions — revised answers and convergence hypothesis

Given that the full pipeline was not run, the primary architecture question ("can the convergence architecture recognise when the grid is insufficient?") cannot be answered by this fixture. However, the analysis provides strong inputs for how to answer it:

**What the evidence says about the true convergence requirement.** Cross-candidate pattern on positive-centre fixtures (seed 42 data):

| Fixture | Beta | Cont sigma | z\* | z\*\* | z\*\*−z\* |
|---|---|---|---|---|---|
| CloudGrow | 1.9 | $2.13 | 2,000 | 2,000 | 0 |
| MedTechX | 2.4 | $3.01 | 3,000 | 5,000 | +2,000 |
| RetailRollup | 2.2 | $14.94 | 3,000 | 7,500 | +4,500 |
| *Project Doom (failed)* | *4.0* | *~$5–10 est.* | *10,000?* | *>10,000?* | *unknown* |

RetailRollup achieved z\*\* = 7,500 with sigma $16.21 (shocked). The grid has one rung remaining (10,000). To push z\*\* to 10,000 requires either a wider shocked sigma or a lower precision bar. The conditions for grid saturation are present in the RetailRollup fixture; one additional sigma increase would plausibly reach the top.

**Estimated true convergence requirement for an extreme-sigma positive-centre company.** If a positive-centre fixture with sigma $20–25 were run (achievable via revenue-scale amplification as noted in A-new-2), the precision rule would require the scatter at n=10,000 to clear 1% of the central value. At sigma $20, the scatter at n=10,000 under B=40 batches is σ/√n = 20/100 = $0.20. If the central value is, say, $5/share, the precision bar is 1% × $5 = $0.05. The scatter ($0.20) far exceeds the bar ($0.05) — z_pct would not find a solution within the grid. The grid would be provably insufficient. **A revenue-scale fixture with sigma $20+ and central value $3–8/share is the right design for the convergence grid stress test.** That fixture is reachable without the negative-centre problem.

---

## 17. Future questions generated by this run

1. **Design a positive-centre convergence stress test fixture.** Based on A-new-2, the correct approach is: large revenue base ($20–25bn), moderate beta (2.0–2.5), thin share count (50–100m), manageable margins (positive throughout, but thin). This produces a wide sigma from revenue scale without raising WACC into gate-failure territory. Targeting sigma $20+ on the shocked pass, with central value $3–8/share.

2. **Is there a revenue/equity ratio at which the z\*\* = 10,000 result is guaranteed?** RetailRollup at z\*\* = 7,500 had revenue/equity ≈ 2.75× and shocked sigma $16.21. A fixture with revenue/equity ≈ 4–5× would likely produce shocked sigma $25+, which — at a central value of $3–5/share — would guarantee z_pct cannot clear the bar at n=10,000. This is the clean test.

3. **What does "grid insufficient" look like in the engine output?** When z_pct cannot find a solution (scatter never falls below the bar across the full N_GRID), the engine returns z_pct = max(N_GRID) = 10,000 — not None (which is the negative-centre failure). The `decision_margin_pct` would be negative at n=10,000 but for the RIGHT reason: the scatter at n=10,000 is still above the precision bar, meaning the grid is genuinely too small. This is architecturally distinct from B1 (which produces z_pct = None because the bar is negative). The engine CAN produce this signal — it just has not been triggered yet.

4. **Should z_pct = 10,000 be reported with a distinct diagnostic flag?** When z_pct = 10,000 because the scatter never cleared the bar (vs the B1 case where z_pct = None), the engine could explicitly flag "grid saturation" — a signal that the grid must be extended before a reliable z\* can be quoted. This is an architecture enhancement worth considering.

5. **Post-mortem on the fixture design.** Project Doom's beta = 4.0 was never going to produce a positive centre with these investment parameters — the breakeven beta is 0.59. Future convergence stress tests should compute the breakeven beta before finalising the fixture design. If breakeven beta < 1.5, the fixture is in the structural dead zone and should be redesigned.

---

## 18. Unexpected results

- The negative centre at beta = 4.0 was anticipated. The magnitude (−$13.19/share, deeper than PowerGridCo's −$9.62 despite much lower net debt per share) was not. The dominant driver is NWC + capex investment intensity, not leverage.

- The breakeven beta of 0.59 was not anticipated. The fixture is negative at ANY reasonable beta, including beta = 1.0 (−$5.70) and beta = 2.0 (−$11.17). This means the fixture is fundamentally incompatible with the convergence stress test objective regardless of how beta is tuned.

- The Gordon multiple collapse (5.43×) is the most striking number in the analysis. At 21.375% WACC, the terminal value perpetuity is worth less than 6× year-5 FCF. For any company where year-5 FCF is constrained by heavy investment (as here), this leaves almost nothing in the terminal value. The mismatch between the investment regime (which generates heavy outflows during the explicit period) and the perpetuity assumption (which assumes the investment programme is complete and FCF is "steady-state") is particularly stark at extreme WACCs.

---

## 19. Comparison to prior gate failure (Candidate #4A — PowerGridCo)

| Dimension | PowerGridCo (4A) | **Project Doom (6)** |
|---|---|---|
| Central value | −$9.62 | **−$13.19** |
| WACC | 10.345% | **21.375%** |
| Beta | 1.8 | **4.0** |
| Net debt/share | $20.00 | **$2.00** |
| Primary failure driver | Heavy leverage ($20/share) | **NWC + capex investment intensity** |
| Breakeven beta | ~2.3 est. | **~0.59** |
| Gate failure margin | Marginal — reducing leverage slightly would fix | **Deep — no realistic beta rescues it** |
| Architectural intent | Second positive-centre fragile company | **Convergence grid stress test** |
| Lesson | Leverage can dominate beta | **Investment intensity > leverage as gate killer** |

Project Doom is a deeper, more structural gate failure than PowerGridCo. PowerGridCo was fixable by reducing leverage; MedTechX was designed to replace it with negligible leverage and succeeded. Project Doom is not fixable by any single parameter change while keeping beta = 4.0 — the entire fixture design must change. The lesson is in A-new-2: use revenue-scale, not beta, to stress the convergence grid.

---

## 20. Channel mix analysis (counterfactual — not run)

Had the central value been positive, the shock channel behaviour would be expected to be extreme. With beta = 4.0, the WACC perturbation volatility per simulation is approximately 1.7× MedTechX's. Revenue at $1,500M is smaller than most prior positive-centre fixtures, so the revenue/equity ratio (even at positive centre $10/share × 50M shares = $500M) would be 1,500/500 = 3.0× — above RetailRollup's 2.75×. Cash channel dominance was not observed at 2.75× (margin retained the lead), and likely would not appear at 3.0×. But funding channel (cost_of_debt = 10%, funding shock multiplies this) would apply to a starting debt cost already at the extreme — a 20-80% funding shock on 10% cost of debt could push debt cost to 12–18%, creating a meaningful WACC uplift. The funding channel would have been more consequential here than for any prior positive-centre candidate. These are architecture hypotheses, not confirmed findings.

---

*End of first-run log. Gate failed — central value negative. Pipeline not run. Architecture observations recorded per pre-run protocol. Next append: after a positive-centre convergence stress test fixture is designed and run.*
