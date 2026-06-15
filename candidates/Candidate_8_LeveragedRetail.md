# Candidate #8 — LeveragedRetail

**A permanent research log for the eighth case study run through the Monte Carlo Valuation Engine.**

**Classification:** Convergence Stress Test — **Gate Failed (Negative Central Value)**
**Status:** Complete / living document. Append, don't overwrite.
**First run:** 2026-06-01. Engine state: steps 2–6 complete and locked.
**Run artefacts:** Deterministic DCF only. Full pipeline not run (pre-run gate not met).

---

## 0. Framing — read before trusting any number here

LeveragedRetail is a **fixture for architecture exploration, not an investment recommendation.** This is a synthetic company. Nothing here is a view on any real entity.

**Primary architectural objective.** Every prior positive-centre fixture (CloudGrow, MedTechX, RetailRollup) and every prior gate failure (PowerGridCo, Project Doom, TitanScale) has probed a different dimension of the convergence architecture. Two routes to high sigma were identified in Candidates 6 and 7: the **beta path** (sigma from WACC volatility) and the **revenue-scale path** (sigma from per-share dollar swings on a large revenue base). Both were tested. The beta path produced gate failures (F11, F12); the revenue-scale path produced z\*\* = 7,500 but not grid saturation (F13).

LeveragedRetail tests a third route: **leverage-driven CV amplification through the equity bridge.**

The mechanism under test: if net debt is very large relative to EV, the equity cushion (EV − net_debt) is thin. The same absolute perturbation in EV translates to a proportionally much larger perturbation in per-share equity value. The coefficient of variation (CV = σ/mean) rises not because σ is larger in absolute terms, but because the mean is compressed by the equity bridge. The hypothesis: this could push CV above the threshold where z\* saturates the grid.

**The operating template is RetailRollup (Candidate #5).** Same revenue profile, growth rates, margins, capex, D&A, NWC, and beta. Only the capital structure changes: net\_debt raised from $2,500M to $21,000M; shares\_outstanding cut from 250M to 200M; debt\_to\_total\_capital raised from 0.30 to 0.75; cost\_of\_debt raised from 7.0% to 7.5%.

**What actually happened.** The pre-run deterministic DCF check produced a **central value of −$16.59/share**. Per the pre-run protocol, the pipeline was stopped. The fixture was not modified. This document records the full analysis of why the gate failed, what the failure reveals architecturally, and what it implies for the leverage-CV-amplification route.

---

## 1. Inputs & assumptions

| Field | Value | vs RetailRollup (C5) |
|---|---|---|
| starting\_revenue | 18,000 | unchanged |
| **net\_debt** | **21,000** | **↑ from 2,500** |
| **shares\_outstanding** | **200** | **↓ from 250** |
| forecast\_years | 5 | unchanged |
| revenue\_growth | 12%, 10%, 8%, 6%, 4% | unchanged |
| operating\_margin | 9%, 10%, 11%, 12%, 13% | unchanged |
| capex\_pct\_revenue | 6%, 6%, 5%, 5%, 5% | unchanged |
| da\_pct\_revenue | 3% flat | unchanged |
| nwc\_pct\_revenue | 3% flat | unchanged |
| tax\_rate | 25% | unchanged |
| terminal\_growth | 2.5% | unchanged |
| risk\_free\_rate | 4% | unchanged |
| equity\_risk\_premium | 5.5% | unchanged |
| beta | 2.2 | unchanged |
| **cost\_of\_debt** | **7.5%** | **↑ from 7.0%** |
| **debt\_to\_total\_capital** | **0.75** | **↑ from 0.30** |

**Derived WACC:**
- Equity cost = 4% + 2.2 × 5.5% = **16.10%**; equity weight = 0.25
- After-tax debt cost = 7.5% × 0.75 = **5.625%**; debt weight = 0.75
- WACC = 0.25 × 16.10% + 0.75 × 5.625% = **8.244%**

Note: WACC of 8.244% is dramatically **lower** than RetailRollup's 12.845%, because the heavy debt weighting (75%) pulls the blended rate down toward the cheap after-tax debt cost. This is the tax-shield effect of leverage operating at full force — the interest deduction on 75% of the capital structure substantially reduces the effective cost of capital.

---

## 2. Deterministic central case — PRE-RUN CHECK RESULT

### ❌ GATE FAILED — central value = −$16.59/share

Per the pre-run protocol: **"Run deterministic DCF first. If the central valuation is not positive: STOP. Report why. Do not modify the fixture."**

The full pipeline (continuous MC, shocked MC, convergence sweeps, seed study) was **NOT run**. The analysis below explains why the gate failed and what it implies architecturally.

| | LeveragedRetail | RetailRollup (C5) | MedTechX | Steady Co |
|---|---|---|---|---|
| Central per-share | **−$16.59** | +$26.16 | +$6.20 | +$12.77 |
| WACC | **8.244%** | 12.845% | 14.98% | 8.16% |
| Net debt | **$21,000M** | $2,500M | $300M | $300M |
| Net debt/share | **$105.00** | $10.00 | $0.75 | $3.00 |

---

## 3. Why the central value is negative — complete decomposition

**Year-by-year FCF (same operating profile as RetailRollup, discounted at 8.244%):**

| Yr | Rev ($M) | Margin | NOPAT ($M) | D&A ($M) | Capex ($M) | ΔNWC ($M) | FCF ($M) |
|----|---------|--------|-----------|---------|-----------|----------|---------|
| 1 | 20,160 | 9.0% | 1,361 | 605 | 1,210 | 65 | **151** |
| 2 | 22,176 | 10.0% | 1,663 | 665 | 1,331 | 60 | **333** |
| 3 | 23,950 | 11.0% | 1,976 | 719 | 1,198 | 53 | **778** |
| 4 | 25,387 | 12.0% | 2,285 | 762 | 1,269 | 43 | **1,015** |
| 5 | 26,403 | 13.0% | 2,574 | 792 | 1,320 | 30 | **1,254** |

Note: the FCFs are *identical* to RetailRollup's operating profile — the operating engine is unchanged. What changes is where those FCFs are discounted and how much debt sits in front of the equity holders.

**Valuation summary:**

| Component | Value ($M) |
|---|---|
| TV (undiscounted, year 5) | 22,380 |
| PV(FCFs) | 2,621 |
| PV(TV) | 15,061 |
| **EV** | **17,682** |
| Net debt | 21,000 |
| **Equity value** | **−3,318** |
| Per share (200M shares) | **−$16.59** |

**The EV is $17,682M. The net debt is $21,000M. Debt exceeds EV by $3,318M. There is no equity.**

The operating business is worth $17.7bn. The debt holders are owed $21bn. Every dollar of enterprise value belongs to creditors; equity holders get nothing and are $3.3bn short. This is the classic technical insolvency situation: asset value (EV) less than debt. The DCF engine computes it correctly.

---

## 4. The WACC paradox — why leverage makes EV larger but equity negative

The most important geometric insight of this run: **the leverage mechanism designed to thin the equity denominator simultaneously inflates the EV numerator — but not nearly enough.**

RetailRollup (C5) had WACC = 12.845%. LeveragedRetail has WACC = 8.244%, a drop of 4.60 percentage points. A lower WACC raises the terminal value multiple (1/(WACC−g)) from 9.67× to 17.43×, inflating EV substantially.

| | RetailRollup (C5) | LeveragedRetail (C8) | Change |
|---|---|---|---|
| WACC | 12.845% | 8.244% | −4.60pp |
| TV multiple (1/(WACC−g)) | 9.67× | 17.43× | +80% |
| EV | $9,039M | $17,682M | **+$8,643M** |
| Net debt | $2,500M | $21,000M | **+$18,500M** |
| Equity value | +$6,540M | −$3,318M | −$9,858M |

The lower WACC does boost EV by $8,643M. But the debt load increased by $18,500M — more than double the EV gain. The net effect on equity is a destruction of $9,858M. The leverage mechanism defeats itself: the same capital structure change that inflates EV via the WACC tax shield also loads far more debt onto the equity holders than the EV gain can absorb.

**Breakeven net\_debt = $17,682M** (= EV). Any net debt below this level with the same inputs would produce a positive equity value. At the specified $21,000M, the excess is $3,318M — not a rounding error.

---

## 5. D/V scan — can tuning the capital structure assumption rescue the gate?

With net\_debt fixed at $21,000M, no value of D/V can produce a positive per-share value:

| D/V | WACC | EV ($M) | Per share |
|---|---|---|---|
| **0.75** | **8.244%** | **17,682** | **−$16.59** ← specified; best case |
| 0.70 | 8.768% | 16,449 | −$24.76 |
| 0.60 | 9.815% | 14,551 | −$37.56 |
| 0.50 | 10.863% | 13,129 | −$47.11 |
| 0.40 | 11.910% | 12,027 | −$54.50 |
| 0.30 | 12.957% | 11,076 | −$60.38 |

The specified D/V = 0.75 is actually the **least bad** scenario: at 75% debt weight, the tax shield is maximised and WACC is minimised, producing the highest EV. Every other D/V assumption makes the per-share value more negative, because a higher WACC (from shifting weight toward expensive equity) compresses EV further below the $21,000M debt level.

**This means the gate failure is structural, not a tuning issue.** With $21,000M of net debt, no capital structure assumption (within the bounds of the DCF framework) produces a positive central value using this operating profile. The breakeven requires net\_debt ≤ $17,682M.

---

## 6. Why the hypothesis fails — the structural incompatibility

The leverage-CV-amplification hypothesis rests on the following chain:

1. Push net\_debt close to (but below) EV → equity denominator (EV − debt) becomes thin
2. Thin denominator → same absolute EV perturbation → much larger per-share swing
3. Higher CV → precision rule requires higher z\*
4. High enough CV → z\* saturates the grid

The flaw in step 1: **EV is not a fixed number independent of the capital structure.** When you push debt\_to\_total\_capital from 0.30 to 0.75, you simultaneously lower WACC and inflate EV. The EV "target" moves upward as you push more debt onto the structure. For this to work, the EV would need to rise faster than the debt — but the $8,643M EV gain from the WACC drop is swamped by the $18,500M debt increase.

More precisely: the tax shield benefit of debt (raising EV) operates on the whole capital base through the WACC formula, whereas the debt load (lowering equity) operates dollar-for-dollar. For a company with modest FCFs relative to its intended debt load, the dollar-for-dollar debt burden always wins.

This is structurally analogous to the beta-path failure (F11): just as raising beta simultaneously raises WACC and therefore kills terminal value, raising debt simultaneously lowers WACC (good for EV) but loads more nominal obligations onto the equity (bad for gate). Both mechanisms have a self-defeating property built into the DCF framework's equity bridge.

---

## 7. Gate failures — all three compared

| | PowerGridCo (4A) | Project Doom (6) | **LeveragedRetail (8)** |
|---|---|---|---|
| Central value | −$9.62 | −$13.19 | **−$16.59** |
| WACC | 10.345% | 21.375% | **8.244%** |
| Primary failure driver | Heavy leverage + capex > D&A | NWC + capex intensity | **Debt exceeds EV ($21B vs $17.7B)** |
| Design intent | Second positive-centre fragile | Beta-path grid stress | **Leverage CV amplification** |
| Route to sigma | Moderate beta | Extreme beta | **Equity bridge thinning** |
| Why route fails | Capex > D&A crushed FCF | WACC too high for investment phase | **Debt load > EV gain from WACC tax shield** |
| Breakeven net\_debt | ~$10,500M (est.) | ~N/A (beta-driven) | **$17,682M** |
| Fixable by single param change? | Yes (reduce leverage) | No (beta kills gate) | **Yes (reduce net\_debt to ≤$17.6B)** |

LeveragedRetail is the **deepest per-share gate failure** (−$16.59) despite having the **lowest WACC** of any fixture (8.244%). The paradox is resolved by the debt analysis above: the low WACC actually reflects the maximum tax shield available — which inflates EV but cannot match the debt obligation.

Unlike Project Doom (where the gate failure was structural regardless of any single parameter), LeveragedRetail is fixable: net\_debt = $17,000M would produce a small positive central value (~$3.41/share) while keeping the leverage-amplification mechanism partially intact. That fixture — thin equity, high leverage, same operating profile — would be the correct design for testing the hypothesis. It was not specified here.

---

## 8. Architecture observations

**A-new-1 (architecture observation — leverage path has same incompatibility as beta path).** Three distinct routes to high sigma have now been probed:

1. **Beta path** (Project Doom): raises sigma via WACC volatility, but also raises WACC, compresses the Gordon multiple, and kills terminal value relative to investment-phase FCF drain. Gate failure is structural (F11, F12).
2. **Revenue-scale path** (TitanScale): raises absolute sigma but leaves CV unchanged — the precision bar scales with the mean. Grid saturation is structurally impossible under standard perturbation widths (F13).
3. **Leverage path** (LeveragedRetail): raises per-share CV by thinning the equity denominator. But the same D/V increase that lowers WACC (inflating EV) is insufficient to absorb the required debt load. Gate failure when debt > EV.

All three routes share the same property: the design parameter intended to stress the convergence grid is also the parameter most likely to trigger the positive-centre gate. This extends F11 from a two-path observation to a **three-path pattern**. The gate and the grid are structurally coupled in a way that creates a systematic blind spot across all three known sigma-amplification mechanisms.

**A-new-2 (architecture observation — thin-equity leverage fixture is theoretically feasible but requires precise calibration).** The leverage route is not permanently dead. If net\_debt is set just below the breakeven (e.g. $17,000M), equity is thin (≈$682M / $3.41 per share) and the CV amplification mechanism is active. A perturbation that moves EV by 10% moves per-share equity by ~26× more than the same perturbation on RetailRollup (thin denominator amplifies). Whether this pushes z\* toward 10,000 depends on the resulting CV, which requires running the engine. The key design constraint is: **net\_debt must be calibrated against the EV before finalising the fixture, not imposed a priori.** Imposing $21,000M without checking EV first guarantees gate failure.

**A-new-3 (architecture observation — gate function confirmed on third independent failure).** The gate fired correctly and cleanly on this fixture, as it did on PowerGridCo and Project Doom. The deterministic DCF alone detected the structural incompatibility before any expensive convergence sweeps were run. Three gate failures now confirm the gate's diagnostic value: it is reliably blocking the convergence machinery from running on architecturally incompatible fixtures.

---

## 9. Comparison vs all prior candidates

| Dimension | Steady Co | Carvana | Rivian | CloudGrow | MedTechX | RetailRollup | TitanScale | P.Doom | **Leveraged (C8)** |
|---|---|---|---|---|---|---|---|---|---|
| Central value | +$12.77 | −$5.61 | −$2.35 | +$5.58 | +$6.20 | +$26.16 | +$459.24 | −$13.19 | **−$16.59** |
| WACC | 8.16% | 10.75% | 12.56% | 12.535% | 14.98% | 12.845% | 13.80% | 21.375% | **8.244%** |
| Beta | 1.1 | 2.2 | 2.0 | 1.9 | 2.4 | 2.2 | 2.3 | 4.0 | **2.2** |
| Net debt/share | $3 | $22.73 | $0.83 | $1.00 | $0.75 | $10.00 | $4.00 | $2.00 | **$105.00** |
| Gate passed? | Yes | Yes | Yes | Yes | Yes | Yes | Yes | No | **No** |
| Pipeline run? | Yes | Yes | Yes | Yes | Yes | Yes | Partial | No | **No** |
| Primary failure | — | — | — | — | — | — | — | NWC intensity | **Debt > EV** |

LeveragedRetail's net debt/share ($105) is by far the highest of any fixture — 4.6× the prior record (Carvana at $22.73). Its WACC (8.244%) is the lowest of any non-Steady Co fixture, demonstrating that the tax-shield effect of 75% debt weight is maximally applied — and still insufficient to overcome the debt load.

---

## 10. The primary research question — answered

**Can a legitimate positive-centre company produce z\* > 10,000 via leverage-driven CV amplification through the equity bridge?**

**This fixture cannot answer the question.** The gate fails before the convergence machinery runs. Net debt ($21,000M) exceeds EV ($17,682M) by $3,318M, making equity negative and the positive-centre condition unsatisfiable.

The architectural insight the failure provides: **the leverage route to high CV has the same self-defeating property as the beta route.** The design parameter that creates the convergence stress (extreme leverage → thin equity denominator → high CV) simultaneously risks destroying the gate condition (debt > EV → negative equity). A correctly calibrated thin-equity fixture — with net\_debt just below the EV breakeven (~$17,000–17,500M) — would be the correct vehicle for testing this hypothesis. That fixture was not specified here.

---

## 11. Future questions generated by this run

1. **Design a thin-equity leverage fixture with net\_debt calibrated to EV.** Compute EV at the target D/V first (using the deterministic DCF), then set net\_debt to ~95% of EV (e.g. ~$16,800M). This produces a small positive central value (~$4–5/share) with extremely thin equity. The CV amplification mechanism should be active. Whether z\* reaches 10,000 depends on the resulting distribution — worth testing.

2. **Is the three-path incompatibility pattern (A-new-1) a general theorem or a coincidence?** Beta path, revenue-scale path, and leverage path all share the property that the sigma-amplification mechanism is coupled to the gate condition. Is there a formal proof that any mechanism for raising CV in a standard DCF framework simultaneously risks the gate? Or is there a fourth path that avoids this coupling?

3. **What is the minimum equity cushion (EV − net\_debt) required for the gate to pass while keeping CV above the grid-saturation threshold (CV > 100%)?** CV > 100% requires σ > mean (per F13). With leverage amplification, σ scales as σ_EV / equity_per_share. This may be achievable with thin equity — but the gate boundary must be respected. A parametric sweep of (equity cushion, β, revenue scale) would map out the feasible region.

---

*End of first-run log. Gate failed — central value negative. Pipeline not run. Architecture observations recorded per pre-run protocol. Next append: after a thin-equity leverage fixture (calibrated to EV) is designed and run.*
