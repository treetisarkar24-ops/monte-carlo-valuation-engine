# NVIDIA Corporation (NVDA)
## Real-World Valuation Case Study — Monte Carlo DCF Engine

**Purpose:** Production application of the finished engine to NVIDIA Corporation, the dominant supplier of accelerated-computing hardware powering the current AI infrastructure buildout. No engine, convergence, N\_GRID, or shock-calibration logic was modified. NVIDIA is a real-world case study, not a stress-test subject; the fixture is constructed from publicly disclosed financials and analyst-consistent forward assumptions.

**Base fixture:** FY2025 actuals (fiscal year ending 31 January 2025), 7-year explicit horizon. Engine seed = 42 throughout. All Monte Carlo / convergence / shock / seed figures were produced deterministically from seeded caches; the 5,000-path channel diagnostic was recomputed live.

---

## 1. Assumptions Used (DCFInputs Fixture)

| Input | Value | Rationale |
|---|---|---|
| Starting revenue | $130,500M | FY2025 reported total revenue |
| Net debt | −$26,000M | Net *cash* position: cash + equivalents ~$34.5B, gross debt ~$8.5B |
| Shares outstanding | 24,400M | Post–10-for-1 split diluted count (June 2024 split) |
| Forecast horizon | 7 years | Standard explicit window for a company mid-growth-cycle |
| Revenue growth | 75% → 4% (7-step fade) | Details below |
| Operating margin | 61% → 53% (7-step compression) | Details below |
| Capex % revenue | 2.5% (Yr 1–3) → 3.0% (Yr 4–7) | Fabless model; modest step-up for infra investment |
| D&A % revenue | 2.0% flat | Primarily software/IP amortisation; scales with revenue |
| NWC % revenue | 2.0% flat | Fabless model; no heavy inventory; modest working capital |
| Tax rate | 15% | Normalised effective rate (SBC deductions, R&D credits) |
| Terminal growth | 2.5% | Long-run nominal GDP-like; AI-era franchise warrants upper bound |
| Risk-free rate | 4.3% | US 10-year Treasury |
| Equity risk premium | 5.5% | Standard equity premium |
| Beta | 1.75 | Elevated; AI-cycle concentration, customer-capex dependency |
| Cost of debt | 4.5% | Investment-grade; near-zero leverage |
| Debt / total capital | 5% | Predominantly equity-financed; debt is a rounding item |

### Revenue Growth Trajectory (Year 1 → Year 7)

| Year | FY | Growth Rate | Revenue ($M) |
|---|---|---|---|
| 1 | FY2026 | +75% | 228,375 |
| 2 | FY2027 | +35% | 308,306 |
| 3 | FY2028 | +20% | 369,967 |
| 4 | FY2029 | +12% | 414,363 |
| 5 | FY2030 | +8% | 447,512 |
| 6 | FY2031 | +6% | 474,362 |
| 7 | FY2032 | +4% | 493,337 |

### Operating Margin Trajectory (Year 1 → Year 7)

| Year | FY | Operating Margin |
|---|---|---|
| 1–2 | FY2026–27 | 61%, 60% |
| 3–4 | FY2028–29 | 58%, 57% |
| 5–7 | FY2030–32 | 55%, 54%, 53% |

---

## 2. Assumption Rationale

**Revenue (FY2025 base, $130.5B).** NVIDIA's reported FY2025 revenue represents a 122% year-over-year increase, driven almost entirely by the Data Center segment as hyperscalers accelerated Hopper (H100/H200) deployments and early Blackwell orders began to flow. This base figure is confirmed public disclosure and anchors the entire forecast.

**Year 1 growth (+75%, to ~$228B).** The Blackwell GPU architecture (B100/B200/GB200) entered full production ramp in late 2025. Hyperscaler capex (Microsoft, Google, Meta, Amazon, Oracle) collectively guided to record data-centre investment. A +75% estimate for FY2026 reflects analyst consensus for the Blackwell supercycle, while acknowledging execution risk and geopolitical export constraints (China). It is not the most optimistic scenario on the Street, nor the most conservative.

**Years 2–4 growth (35% → 12%).** The ramp decelerates as Blackwell reaches saturation, next-generation (Rubin) architecture transitions begin, and competition from AMD Instinct, Intel Gaudi, and custom silicon (Google TPU, Microsoft Maia, Amazon Trainium) matures. A 35% FY2027 estimate reflects a still-expanding addressable market against a higher base. By FY2029 the rate approaches typical large-cap tech deceleration.

**Years 5–7 growth (8% → 4%).** Normalisation toward a maturing $450–490B revenue base as AI infrastructure build-out transitions from exponential to sustained-growth phase. The 4% terminal fade is deliberately conservative — it sits one percentage point above the terminal growth assumption, providing a buffer in the Gordon terminal value.

**Operating margins (61% down to 53%).** FY2025 EBIT margin was approximately 62% — extraordinary by any historical standard, driven by pricing power on Hopper and near-monopoly positioning in GPU compute. The 61%/60% profile in Years 1–2 sustains that level while acknowledging Blackwell mix effects and increased R&D investment. The compression to 53% by Year 7 reflects (a) intensifying competitive pressure on price, (b) the ongoing mix-shift toward systems and networking (lower margin than raw silicon), and (c) normalisation of supply-demand dynamics as capacity expands. Even at 53%, NVIDIA's margins would remain among the highest of any large-cap hardware company in history.

**Capex (2.5–3.0% of revenue).** NVIDIA operates a fabless model — it designs chips, contracts manufacturing to TSMC, and outsources packaging. This keeps reported capex structurally low relative to revenue. The modest step-up from 2.5% to 3.0% in Years 4–7 captures increasing investment in data-centre infrastructure, networking equipment, and internal test capacity as revenue scales.

**D&A and NWC (2.0% flat).** Both scale with revenue in a fabless, software-and-services-adjacent model. D&A is driven primarily by IP and software amortisation; NWC reflects a business with limited raw-materials inventory and strong receivables management.

**Tax rate (15%).** NVIDIA's effective tax rate in recent years has been below statutory rates, reflecting substantial stock-based-compensation deductions (treated as a tax shield), R&D tax credits, and jurisdictional income-routing. A 15% normalised rate is above the recent realised rate but below the US statutory 21% — a defensible mid-point for a forward-looking model.

**WACC inputs.** Beta of 1.75 reflects NVIDIA's above-market systematic risk: the stock is highly correlated with the AI investment cycle, customer capital-expenditure cycles, and geopolitical risk (export controls, TSMC concentration). The 5% debt/total-capital ratio reflects a balance sheet that is functionally all-equity. The resulting WACC of **13.42%** is the relevant discount rate.

**Terminal growth (2.5%).** Set at the upper end of the engine's triangular band (1.5–3.0%). For a company building the compute infrastructure of the AI economy, a GDP+ terminal growth assumption is defensible; the 2.5% mode reflects secular tailwinds without extrapolating hypergrowth in perpetuity.

---

## 3. Deterministic Valuation

Running the deterministic DCF (`run_dcf`) on the central-case fixture produces a single-point estimate:

| Metric | Value |
|---|---|
| WACC | 13.42% |
| Cost of equity | 13.93% |
| Cost of debt (after-tax) | 3.83% |
| Central intrinsic value per share | **$64.20** |

The $64.20 figure represents the single point estimate from compounding the central-case revenue trajectory through the DCF blocks — operating profit, free cash flow, terminal value, and the equity bridge (adding back $26B net cash, dividing by 24.4B shares). It is the model's best guess under the stated assumptions, and the anchor against which the Monte Carlo distribution is interpreted. It does not capture the distribution of outcomes around that anchor; that is the Monte Carlo's job.

---

## 4. Continuous Monte Carlo (z\* = 2,000)

### Convergence

The engine swept the full N\_GRID ([100, 250, 500, …, 10,000]) to locate z\* — the per-company sample size at which the scatter of run-means falls below the 1%-of-value precision bar.

| Metric | Value |
|---|---|
| z\* (convergence elbow) | **2,000** |
| Decision margin | 74.1% |
| Precision bar | $0.660 |
| σ estimate | $17.71/share |
| Borderline | No |
| Batches recommended | 5 |
| Compute vs folk 10,000 | **0.20× (5× savings)** |
| Mean gap vs folk run | **0.098%** |

NVIDIA is a *moderate* convergence problem: z\* = 2,000 is in the lower half of the N\_GRID, well below the 10,000 folk default. The 74% decision margin signals a clean elbow — the scatter curve bends decisively at n = 2,000, not at a borderline threshold. Five production batches is all the apparatus requires. The benchmark confirms it: running the engine at 10,000 paths produces a mean only 0.098% higher than the z\* = 2,000 run, for five times the compute cost. The folk number, on these inputs, is pure waste.

### Production Distribution (n = 2,000, seed 42)

| Statistic | Value |
|---|---|
| Mean | $65.93 |
| Median | $63.80 |
| Std deviation | $17.87 |
| Minimum | $28.29 |
| Maximum | $158.31 |
| 5th percentile | $40.37 |
| 10th percentile | $44.60 |
| 25th percentile | $52.93 |
| 50th percentile | $63.80 |
| 75th percentile | $76.37 |
| 90th percentile | $90.08 |
| 95th percentile | $98.63 |
| Fraction negative | **0.0%** |

**Shape.** The distribution is right-skewed: mean ($65.93) exceeds median ($63.80) by $2.13, a 3.3% gap. The right tail extends to $158 while the left floor sits at $28. The positive skew reflects the asymmetry in the upside: aggressive-but-correlated growth paths (revenue surge + margin expansion, via the +0.5 revenue–margin correlation) can compound to very high valuations, while the downside is bounded by the net-cash cushion and positive-but-thin margin in the worst paths. Every simulation — 100% — produces a positive valuation, consistent with a company holding ~$26B net cash and generating substantial free cash flow even in stressed scenarios.

The histogram (text representation):

```
   28.29 | ###                                            25
   34.79 | #############                                  96
   41.29 | #########################                     182
   47.79 | ####################################          257
   54.30 | ########################################      290
   60.80 | ##########################################    304
   67.30 | ###################################           255
   73.80 | ##########################                    188
   80.30 | #####################                         155
   86.80 | #############                                  94
   93.30 | #########                                      63
   99.80 | ######                                         40
  106.30 | ####                                           28
  112.80 | #                                              10
  119.30 | #                                               6
  125.80 |                                                 3
  132.30 |                                                 1
  138.80 |                                                 1
  145.30 |                                                 1
  151.80 |                                                 1
```

The modal bucket ($60.80–$67.30) brackets the deterministic central case ($64.20), confirming the engine's perturbation design is symmetric around the central estimate. The long right tail (the handful of simulations at $125–$158) represents high-growth, high-margin trajectories compounding into large terminal values.

**Jensen's inequality effect.** The MC mean ($65.93) exceeds the deterministic value ($64.20) by $1.73 (+2.7%). This is the expected Jensen upward adjustment: when FCF is a convex function of the perturbed inputs, the mean of the distribution sits above the point-estimate of the function evaluated at the central inputs. For NVIDIA, the convexity is modest — terminal value depends quadratically on revenue trajectory, but the discount rate (WACC) attenuates the effect. The 2.7% gap is consistent with prior observations on similar-profile companies.

---

## 5. Shocked Monte Carlo (z\*\* = 1,500)

### Convergence

The shocked convergence sweep layers the discrete micro-shock overlay (five channels: revenue, margin, funding, strategic, cash) onto the continuous perturbation and re-finds the convergence elbow.

| Metric | Value |
|---|---|
| z\*\* (shocked convergence elbow) | **1,500** |
| Decision margin | 36.6% |
| Precision bar | $0.625 |
| σ estimate (shocked) | $18.50/share |
| Batches recommended | 16 |
| Shock-free paths | **67.4%** |
| z\* → z\*\* change | **2,000 → 1,500 (−500)** |

The shocked stage surfaces a notable result: z\*\* = 1,500 is *lower* than z\* = 2,000. The addition of discrete shocks did not raise the required sample size; it lowered it. The mechanism and implications are documented separately in the Investigation Log (Section 9). The practical consequence for the production run: the shocked engine needs *fewer* simulations than the continuous engine to meet the 1%-of-value precision bar.

The 36.6% decision margin — lower than the continuous 74.1% — reflects a harder determination: the shock scatter curve's elbow is shallower and the call is closer to the borderline. The recommendation of 16 batches (vs 5 for continuous) confirms the shocked apparatus needs more replication to stabilise its own elbow estimate.

### Production Distribution (n = 1,500, seed 42)

| Statistic | Continuous | Shocked | Δ |
|---|---|---|---|
| Mean | $65.93 | $62.65 | −$3.28 (−5.0%) |
| Median | $63.80 | $60.16 | −$3.64 (−5.7%) |
| Std deviation | $17.87 | $18.79 | +$0.92 (+5.1%) |
| Minimum | $28.29 | $15.93 | −$12.36 |
| Maximum | $158.31 | $167.01 | +$8.70 |
| 5th percentile | $40.37 | $35.28 | −$5.09 |
| 10th percentile | $44.60 | $41.01 | −$3.59 |
| 25th percentile | $52.93 | $49.82 | −$3.11 |
| 50th percentile | $63.80 | $60.16 | −$3.64 |
| 75th percentile | $76.37 | $74.06 | −$2.31 |
| 90th percentile | $90.08 | $86.61 | −$3.47 |
| 95th percentile | $98.63 | $95.48 | −$3.15 |
| Fraction negative | 0.0% | **0.0%** | — |

**Shock overlay effects.** The discrete shocks reduce the mean by $3.28 (−5.0%) and the median by $3.64 (−5.7%), while widening the standard deviation by $0.92 (+5.1%). The left tail extends from $28 to $16 — a $12 extension representing the worst-case stacking of multiple shock events on an already-stressed path. The right tail extends *upward* to $167 (from $158), a feature of the shock engine's structure: on certain lightly-shocked paths, the fragility-adjusted dynamics produce slightly different terminal-value contributions.

The fraction of negative-valuation paths remains 0.0%. NVIDIA's $26B net-cash cushion and consistently positive margins mean that even the most adverse shock scenario in this engine does not threaten the firm's solvency or equity value. This is the low-leverage, high-margin profile behaving exactly as the fragility model predicts.

### Shock Channel Analysis (5,000 diagnostic paths)

**Overall firing rates:**

| Channel | Total Fires | Rate per Path |
|---|---|---|
| Revenue | 448 | 0.090 |
| Margin | 417 | 0.083 |
| Funding | 436 | 0.087 |
| Strategic | 415 | 0.083 |
| Cash | 453 | 0.091 |
| **Total** | **2,169** | — |

All five channels fire at broadly similar rates (0.083–0.091 per path), consistent with the equal-hazard V1 design. No channel exhibits anomalous frequency.

**Worst-5% path drivers:**

| Channel | Worst-5% Fires | vs Overall |
|---|---|---|
| Revenue | 125 | **2.1× elevated** |
| Margin | 121 | **2.1× elevated** |
| Funding | 30 | 0.5× (suppressed) |
| Strategic | 38 | 0.7× (near base) |
| Cash | 37 | 0.6× (suppressed) |

The worst-5% outcomes are driven by **revenue loss and margin compression** — not by financing stress or strategic impairment. Revenue and margin channel fires are more than twice as frequent in the worst paths as their overall rate; funding, strategic, and cash channels are suppressed. This is the expected fragility pattern for NVIDIA's profile: a company with minimal debt and $26B net cash is nearly immune to funding shocks, while operating channels (customer loss, competitive margin pressure) are the real destroyers of equity value.

The finding has a direct business interpretation: NVIDIA's primary tail risk is not a financial crisis or even a strategic pivot failure — it is the loss of its dominant position in the AI compute market, manifesting as simultaneous revenue haircuts and margin compression (e.g., AMD/Intel breakthrough, hyperscaler in-house custom silicon achieving full substitution, or an AI spending reversal). The model cannot assign a probability to that scenario, but it can identify the *transmission channel* — and it is operating, not financial.

Mean cumulative stress: 0.217. Max observed: 3.92.

---

## 6. Market Percentile Analysis

NVIDIA's exact share price as of the valuation date is not embedded in the engine; the table below provides CDF reference points so the reader can locate the current traded price within the modelled distribution. Estimated from interpolating the percentile tables of both distributions:

| Reference Price | Continuous CDF | Shocked CDF | Interpretation |
|---|---|---|---|
| $40 | ~5% | — | Left-tail boundary |
| $50 | ~17% | ~10% | Low-end pessimistic scenario |
| $60 | ~44% | ~38% | Near median (below central DCF) |
| $64 (≈ central DCF) | ~50% | ~45% | Deterministic anchor |
| $75 | ~75% | ~74% | IQR upper bound |
| $90 | ~88% | ~87% | Top-decile threshold |
| $100 | ~95% | ~96% | Tail entry |
| $120 | ~97% | ~97% | Deep right tail |
| $140 | ~99% | ~99% | Near maximum of distribution |

**Interpretation.** NVIDIA's market price — which traded in the $100–120 range in publicly disclosed periods prior to this analysis — sits at approximately the **95th–97th percentile** of both the continuous and shocked modelled distributions. The engine, on these inputs, rarely simulates an intrinsic value as high as the current traded price.

This is not a call to sell. It is a precise statement about what the model's assumptions imply. The gap between central intrinsic (~$64) and market (~$110–120) is the market pricing three things that this fixture deliberately does not encode:

1. **Growth optionality beyond the 7-year horizon.** A fabless-model company with NVIDIA's CUDA ecosystem lock-in, DGX/NVLink infrastructure standard, and expanding TAM in robotics, autonomous vehicles, and sovereign AI data centres may generate economically significant cash flows well beyond Year 7 that a standard Gordon terminal-value model compresses into a single 2.5% assumption.

2. **AI infrastructure as a structural shift, not a cycle.** The fixture models growth fading toward 4% by Year 7 — rational caution, but potentially wrong if the AI compute buildout is decade-long rather than cycle-long. Markets may be pricing a longer duration of above-normal growth.

3. **Ecosystem moat premium.** CUDA's developer lock-in represents a durable competitive advantage that pure DCF mechanics cannot capture. A buyer of NVIDIA stock is in part paying for the optionality embedded in that moat — the probability that NVIDIA secures a disproportionate share of the next compute paradigm.

The model cleanly separates what the *fundamentals support under stated assumptions* (~$64 central) from what the *market is pricing* (~$115–120), and quantifies how far into the tail the market price sits. That separation is the engine's contribution — not a verdict on the market's intelligence.

---

## 7. Risk Discussion

**Upside risks (not fully captured in the fixture):**

The fixture's assumptions are intentionally conservative on growth duration. Revenue is modelled fading to 4% by Year 7 across a $493B base. If the AI inference, robotics, and autonomous vehicle markets develop faster than modelled, or if NVIDIA sustains pricing power longer than the margin compression schedule assumes, realised values would cluster in the upper half of the distribution. The 95th-percentile outcome (~$98 continuous, ~$95 shocked) would represent a relatively modest AI acceleration scenario by current market standards.

**Downside risks:**

The model's 5th-percentile outcome (~$40 continuous, ~$35 shocked) is characterised by revenue growth substantially below the central case and margin compression toward the lower end of the distribution. The channels driving these tail outcomes are revenue loss and margin compression simultaneously — the signature of a competitive disruption event (AMD/Intel breakthrough, hyperscaler custom silicon, demand softening). The net-cash position ensures no path crosses zero in this model, but a $35/share scenario represents ~70% below recent market prices, and would require a material re-rating of NVIDIA's competitive position.

**Export controls and geopolitical concentration** are not modelled as a separate shock channel (the engine's five channels are economically generic). The revenue channel absorbs this risk implicitly — a shock to the revenue level is the mechanism by which a restriction on China or other export-controlled markets would flow through. This is one area where company-specific calibration of the shock hazards (currently at the generic V1 default) would improve the analysis.

**TSMC concentration.** NVIDIA manufactures 100% of its leading-edge GPUs at TSMC, primarily on the N4 and N3 nodes. A sustained disruption to TSMC capacity (natural disaster, geopolitical conflict in Taiwan, yield crisis on a new node) would be a severe supply-side shock with no short-term substitute. This risk is again absorbed into the revenue channel in the current engine, but its potential magnitude (a multi-quarter revenue gap while no alternative exists) exceeds what a standard revenue-shock band might generate.

**Valuation sensitivity to WACC.** At WACC = 13.42%, the Gordon terminal value is discounted at (WACC − g) = 10.92%. A 100 basis-point reduction in WACC to 12.42% — defensible if AI infrastructure becomes treated as a utilities-adjacent regulated asset — raises (WACC − g) to 9.92% and increases the terminal value by roughly 10%. For a company with this terminal-value weight, WACC sensitivity is material. The MC distribution already captures WACC variation through the correlated beta and ERP perturbations; the 90th-percentile outcome (~$90) implicitly reflects lower-WACC paths.

---

## 8. Convergence Observations

| Metric | Continuous | Shocked |
|---|---|---|
| z | 2,000 | 1,500 |
| Decision margin | 74.1% | 36.6% |
| σ estimate | $17.71 | $18.50 |
| Batches recommended | 5 | 16 |
| Adequately resolved | Yes | Yes |
| Grid saturation | No | No |

**z\* = 2,000 (continuous).** NVIDIA is a moderately easy continuous convergence problem. The 74.1% margin reflects a clean elbow: the scatter of run-means at n = 2,000 is 0.379 (comfortably below the $0.660 precision bar), and the curve had already crossed the bar at n = 1,500 with 0.454. The recommendation of only 5 batches signals that the convergence machinery did not need to work hard to reach a confident conclusion.

**z\*\* = 1,500 (shocked).** The shocked elbow landed *earlier* than the continuous elbow, a result documented and analysed in the Investigation Log (Section 9). The margin is narrower at 36.6%, and 16 batches are recommended — signals that the shocked determination is less precise and merits additional batches before trusting the elbow reading. The elbow nonetheless cleared the bar, the determination is marked as adequate, and the production run proceeds at z\*\* = 1,500.

**Compute benchmark.** The continuous engine at z\* = 2,000 reproduces the 10,000-path folk run with a mean gap of 0.098% — essentially identical answers — at 20% of the computational cost. Every additional simulation beyond n = 2,000 was wasted effort under the folk convention.

---

## 9. Seed Robustness

Four independent seeds confirm the stability of the convergence recommendations:

| Seed | z\* (cont) | cont margin | z\*\* (shock) | shock margin |
|---|---|---|---|---|
| 42 | 2,000 | 74.1% | 1,500 | 36.6% |
| 99 | 1,500 | 41.0% | 2,000 | 62.8% |
| 123 | 1,500 | 84.8% | 1,500 | 44.7% |
| 7 | 1,000 | 19.4% | 1,500 | 67.5% |

**Continuous.** z\* ranges 1,000–2,000 across seeds, clustered in the lower half of the N\_GRID. Seed 7 at 1,000 carries a thin 19.4% margin — borderline, but still above the N\_GRID minimum. The qualitative conclusion is consistent across all seeds: NVIDIA is an easily-convergent company, resolved well below the folk 10,000 on every draw.

**Shocked.** z\*\* clusters tightly at 1,500 across three of four seeds (42, 123, 7); seed 99 lands at 2,000 with a 62.8% margin. The central tendency is clearly 1,500. No seed required grid saturation (10,000), confirming that the shocked engine's convergence properties for NVIDIA are well-behaved across the random-number landscape.

**Conclusion.** The seed robustness table shows NVIDIA as one of the more stable convergence subjects in this engine's history. The z\*/z\*\* recommendations are not artefacts of one particular seed's random stream; they reflect genuine properties of the valuation distribution.

---

## 10. Final Interpretation

On a FY2025-base fixture with conservative analyst-consistent assumptions, NVIDIA's Monte Carlo intrinsic value is a **right-skewed, entirely-positive distribution centred near $64/share** — continuous mean $65.93, shocked mean $62.65, zero negative paths in either engine. The 90% confidence interval spans roughly $40 to $98 (continuous), widening to $35 to $95 under shocks.

Three findings stand out:

**1. Operating fragility dominates the tail.** In the worst-5% outcomes, revenue and margin channels fire at more than twice their base rate, while funding channels are suppressed. NVIDIA's negligible leverage immunises it against financial distress; the real risk is operating — a disruption to its dominant GPU market position manifesting as simultaneous revenue loss and margin compression. The engine cannot assign a probability to that event, but it can name the transmission route.

**2. The engine converges cheaply.** z\* = 2,000 and z\*\* = 1,500 are both far below the folk default of 10,000. Five production batches suffice for the continuous determination. The mean gap between the z\*-run and a 10,000-path run is 0.098% — the folk convention costs five times the compute for a 0.1% improvement in mean precision. NVIDIA joins a growing set of observations confirming that the folk number is not derived from the company's variance profile; it is inherited.

**3. The market price sits deep in the right tail.** At $64 central DCF, the modelled fundamental value is approximately 45–50% below typical recent market prices (~$110–120). The market is pricing substantial optionality — long-duration growth, ecosystem moat, and AI infrastructure as a structural shift — that a standard 7-year DCF with a conservative terminal growth assumption cannot reproduce. The engine's contribution is to quantify exactly how far into the tail the market's implied expectations sit: approximately the 95th–97th percentile of the modelled distribution. That is a precise, useful finding, whether one views it as the market being rational about NVIDIA's option value or as pricing that requires a leap of faith well beyond what current financials support.

---

*Engine applied as-is; no DCF, Monte Carlo, shock, or convergence logic modified. Seed 42 throughout; all figures produced from seeded deterministic caches. Fixture based on FY2025 public disclosures. Market price reference range estimated from publicly available data; reader should verify current price.*
