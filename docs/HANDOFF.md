# Monte Carlo Valuation Engine — Project Handoff

This document is a complete handoff for continuing work on this project in a new conversation, project, or chat. Read it end-to-end before responding. It contains the build state, the intellectual framework, the working patterns, and the design decisions made so far. The goal is to let the next Claude pick up the work without forcing Treeti to re-derive context.

**Last updated:** 2026-05-31 — **Step 5 (micro-shock overlay) BUILT, VERIFIED, and LOCKED.** `mc_shocks.py` + shock knobs in `mc_defaults.py` + `mc_shocks_smoke_test.py` all live in the MC folder; `dcf.py`/`mc_engine.py` untouched (clean add-on). Smoke test passes (disabled==pure step-3, shocks-on sinks the left tail, seed reproducible, 75.4% shock-free). The trip-wire fired — margin dominates the worst tail, funding/cash structurally weak — flagged as the V2 calibration signal. **See the FINAL SESSION UPDATE — 2026-05-31 (step 5 BUILT...) at the very bottom** for the authoritative current state; it supersedes the open questions in the philosophy update above (notably: the fragility mechanic is a severity-weighted damage tally, NOT the value-deterioration "V2" that earlier sections lean toward). Next: step 6 (convergence round two -> z**). The original step-2-close content below remains foundational context.

**Original handoff date:** 2026-05-28, at the close of step 2 (deterministic DCF engine fully complete and verified). Next step on resume at that time: step 3 (Monte Carlo machinery) — now in progress, see session update.

---

## Who Treeti is and what this project is

Treeti is building a six-project portfolio of quant-finance work intended to be defensibly intelligent, not just functional. Each project has a point of view — not "I built this" but "I built this because I believe X, and here's what would change my mind."

Project #1 — this one — is the Monte Carlo Valuation Engine. The engine is general-purpose: the code is the engine, and any specific company is just a case study that gets run through it. No company is locked yet, and that is deliberately the right call — building around a specific company would compromise the engine's generality.

The other five projects in the portfolio: Annual Report Dissection, Expectations Gap Model, Shock Analyser, Sector Deep Dive Dashboard, Excel Data Toolkit. Project #6 (Excel Data Toolkit) is the data-quality spine of the portfolio, not the weakest project. Treeti saw that before I did.

---

## The intellectual thesis

The Monte Carlo Valuation Engine produces a *distribution* of intrinsic values per share, not a point estimate. It has two distinguishing features beyond a standard Monte Carlo DCF:

**1. Discrete micro shock event overlay.** Company-level binary events — CEO departure, regulatory action, customer loss, patent expiry, supply chain failure — layered onto the continuous distribution of inputs, with state-conditional probabilities so the probability of further bad events rises in already-stressed simulation paths. This produces realistic fat-tail behaviour and death-spiral scenarios that fixed-probability and continuous-only models cannot generate. The micro shock concept lives in two places across the portfolio — as event overlays here, and as the analytical framework in the Shock Analyser project. That cross-project connection demonstrates systems thinking.

**2. Convergence analysis module — the headline feature.** This is the load-bearing intellectual claim of the entire project. The industry-standard 10,000 simulations is folk wisdom inherited from 1990s computational finance, NOT a number derived from any company's variance profile. The engine replaces that folk number with a per-company empirical z, found by running MC at increasing n and locating the elbow of the convergence curve (scatter of run-means vs n).

Z varies materially by company and industry. Drivers, in order of impact: width of input distributions, tail heaviness, input correlation (reduces effective sample size), and presence of discrete shocks. A regulated utility might converge at n≈2,000; a speculative biotech with binary events might need 50,000+.

Two convergence passes are required by the build sequence: n\* for continuous-only, n\*\* after the micro shock overlay. Adding shocks fattens the tails, which raises z. The gap between n\* and n\*\* is itself a finding worth reporting.

**Critical pedagogical distinction — peak vs elbow.** Hold this distinction firmly:

- The OUTPUT of one MC run is a (roughly) bell-shaped distribution of valuations. It has a peak — that peak is the most likely value of the company. This is the engine's answer.
- The DIAGNOSTIC for choosing n is a separate object. At each n, you run MC multiple times and measure how scattered the run-means are. Plot scatter against n and you get a decay curve, not a bell. It asymptotes toward zero. The right n (z) is at the elbow, not at any peak.

The bell has a peak. The convergence curve has an elbow. Two different distributions doing two different jobs. Do not merge them.

---

## Point of view

Standard DCF outputs false precision — one number, no honesty about the range of possibility. This engine treats uncertainty as the subject, not the footnote. It treats company-level fragility as state-dependent, not static. It treats sample size as a calibration problem, not a default. That point of view should be visible in every architectural choice and every line of inline documentation.

---

## Tech stack

Python primary. R as fallback for simulation-heavy work or where it's genuinely cleaner. SQL and Power BI integration planned for later phases. All code must be readable and documented — this is portfolio code, meant to be read by hiring managers and finance colleagues. It is not throwaway.

---

## Build sequence (locked — agreed in prior conversations)

1. Sanity check the historicals (light pass). **— DONE**
2. Deterministic DCF skeleton. **— DONE, end-to-end verified**
3. Monte Carlo machinery (the code that perturbs revenue growth, margins, and so on — the smooth dials). **← currently here, NEXT**
4. Convergence analysis, round one → find the right sample size n\* → run the production Monte Carlo at n\*. Continuous-only valuation distribution.
5. Build the micro shock overlay.
6. Convergence analysis, round two (shocks change the variance, so the right n shifts) → run the production Monte Carlo with shocks at n\*\*.
7. Full input validation layer.

Convergence is paired with the production run, not a separate step. The convergence module IS the Monte Carlo machinery used at varying n. Treeti spotted this when I had them separated and was right.

Data philosophy: clean data is not the same as deterministic data. Cleaning strips out the spurious stuff (one-time items, restatements). The natural variance that remains is the source signal the Monte Carlo eats.

---

## Current state — step 2 of 7 COMPLETE

The deterministic DCF lives at `/Users/treetisarkar/Documents/Claude/Projects/MC/dcf.py`. Seven engine blocks plus an orchestrator, in strict topological order:

1. `project_revenue` — revenue trajectory (block 1)
2. `project_ebit`, `project_nopat` — operating profit (block 2)
3. `project_da`, `project_capex`, `project_dnwc`, `project_fcf` — free cash flow (block 3)
4. `compute_wacc` — weighted average cost of capital (block 4)
5. `terminal_value` — Gordon growth perpetuity (block 5)
6. `discount_fcfs`, `discount_tv`, `discount` — present-valuing and enterprise value (block 6)
7. `equity_value`, `equity_value_per_share` — bridge from EV to per-share intrinsic value (block 7)
8. `run_dcf` — orchestrator, wires the seven blocks in sequence and returns per-share value

**Block 4 was originally TV and block 5 was WACC + discounting. That ordering had block 4 reaching forward to block 5 for WACC. Treeti spotted the wart; we refactored to strict topological order — every block reads only from prior blocks. Narrative still works: blocks 1–3 = "what cash the business produces", block 4 = "what investors demand" (the pivot), blocks 5–7 = "what it's worth today".**

### Verification

Two independent verifications passed:

- **`sanity_check.py`** — constructs a synthetic DCFInputs, walks every block, prints intermediate trajectories, hand-checks against worked-example numbers, and confirms `run_dcf` produces the same per-share value as the manual walk-through. PV_TV is 78.1% of EV, right in the predicted 60–80% band.

- **`textbook_verification.py`** — Gordon-growth limit test. Constructs a degenerate steady-state DCFInputs where the engine should mathematically collapse to the closed-form Gordon formula `EV = FCF_1 / (WACC − g)`. Verified PASS across seven forecast horizons (3, 5, 7, 10, 25, 50, 100 years) with per-share value identical to the closed-form bar (`$31.500000`) and relative gaps at floating-point epsilon (`~3e-16`). Horizon-invariance confirms the telescoping of explicit FCF PVs + TV PV. This is the rigorous mathematical verification — composition of all seven blocks tested simultaneously against first-principles theory.

---

## Design decisions made (with reasoning)

These are decisions made in conversation. Some are partially baked into the code; the *reasoning* lives only here.

**Frequency: annual, not quarterly or monthly.** DCF is a long-horizon tool; quarterly precision past year 1 is false precision. Annual matches the noise floor of long-horizon forecasting, matches convergence granularity, keeps parameter space manageable, matches every benchmark valuation convention. Stub-period model can be added later if a specific case needs year-1 quarterly resolution.

**Forecast horizon: variable based on stability.** Default 7 years. Stretch to 10 for stable companies. Contract to 5 for unstable companies. The engine just takes `forecast_years` as int; the stability judgment lives upstream. Possible future addition (parked): a "stability score" from historical coefficient of variation that suggests a horizon automatically.

**Trajectory representation: Option A (lists), not decay functions.** Each forward-looking dial stored as a list of length `forecast_years`. More flexible, fully explicit, easier to read. May revisit Option B (start + end + interpolation) when Monte Carlo wants fewer dials to perturb.

**Composition pattern: each block plugs into the next via explicit arguments.** No shared mutable state, no hidden coupling. The orchestrator `run_dcf` wires the seven blocks.

**Two-function split for block 2.** `project_ebit` and `project_nopat` separate for composability and inspectability.

**Helper functions for blocks 3 and 6.** Block 3 exposes `project_da`, `project_capex`, `project_dnwc` as helpers used by `project_fcf`. Block 6 exposes `discount_fcfs`, `discount_tv` as helpers used by `discount`. Same reason: inspect intermediates without digging inside the main function. Especially load-bearing for MC diagnostics later (e.g., PV_TV as % of EV per simulation).

**Block ordering: strict topological dependency order.** Originally block 4 was TV (reaching forward to block 5 for WACC). Refactored: block 4 is now WACC, block 5 is TV, block 6 is discounting, block 7 is equity bridge. Every block reads only from prior blocks. Narrative grouping still works (operating engine → cost of capital → valuation).

**D&A, capex, NWC modelled as % of revenue with caveats.** Simplifying assumptions, with inline NOTEs flagging breaks. D&A%: assumes asset base and revenue grow in proportion; breaks for capital-heavy and early-stage companies. Capex%: arguably most fragile because capex is the active investment decision. NWC%: most defensible because NWC components genuinely scale with sales.

**EBIT-based, not EBITDA-based.** Technical reason: tax shield — D&A is tax-deductible, so tax must be applied to EBIT not EBITDA, or cash flow is under-stated by `D&A × tax_rate` every year. Philosophical reason (Buffett/Munger): EBITDA pretends assets are free.

**Negative beta is mathematically valid.** Beta is a covariance ratio; the `beta` field in `DCFInputs` is `float` deliberately to allow the full range.

**Share price is NOT an input.** The engine produces intrinsic value per share; share price is the market's current consensus. Comparison is the actionable signal. In Monte Carlo terms: market price gets compared to the *distribution* of simulated intrinsic values, not a single point — a stronger statement. A `current_market_price` field will be added at the comparison/output step, not in the dataclass.

**End-of-year discounting convention.** Each year's cash is treated as arriving at end-of-year. Mid-year convention would shift PVs up slightly; end-of-year matches the standard textbook choice and most published DCFs.

**Single-source-of-truth for WACC.** WACC is computed once by `compute_wacc(inputs)` in block 4 and passed as a float into both `terminal_value` (block 5) and `discount` (block 6). No block recomputes it.

**Input validation deferred to step 7 — REAFFIRMED this session.** Treeti raised whether assertions should be added to block 4 (`debt_to_total_capital ∈ [0,1]`) and block 5 (`g < WACC`). Pushback held: math first, validation last. Reasons: (a) partial validation in two blocks is inconsistent — there are ~10 other preconditions, and step 7 will handle them comprehensively in one place; (b) `assert` is the wrong tool because Python's `-O` flag strips assertions, so step 7 should use `raise ValueError` or `__post_init__` checks instead; (c) requirements ARE already documented in docstrings. Decision: blocks stay validation-free; step 7 does a unified sweep.

**Worked-example pedagogy lesson (caught during sanity check).** During block 5's concept beat I used `WACC = 9%` as a placeholder (block 4 hadn't been written yet) and computed TV = $312.23M. Then in block 6's concept beat I switched to the real `WACC = 8.385%` for discounting but kept the old TV value, producing a Frankenstein EV that didn't tie to either WACC. The engine itself is correct — only the chat-narrative numbers were inconsistent. Lesson for future Claudes: when a placeholder gets used in early teach-mode beats, recompute downstream examples with the real number once it's available, OR explicitly carry the placeholder through. Don't mix.

---

## Working patterns (the rhythm — preserve this)

**Teach mode.** Treeti owns the theory; Claude writes the Python. Standard flow for each block:

1. Explain the concept (bilingually — see below).
2. Give a numerical worked example, continuing from the previous block's outputs where possible.
3. Provide pseudocode / flowchart.
4. (Treeti reads, asks clarifying questions, signals understanding.)
5. Claude writes the Python with rich bilingual inline comments.
6. Brief walkthrough pointing at the key bits.
7. Treeti reviews, asks more questions, then either iterates or signals ready for the next block.

Do not ask Treeti to type Python. Treeti has VS Code and Cursor for that purpose; the intellectual value isn't in syntax.

**Bilingual delivery.** Every technical term comes with a plain-English gloss in the same beat. Pattern: "WACC (the rate at which we shrink future cash to present value, because future money is worth less today)." Once glossed in the current conversation, drop the gloss on later mentions unless it's been a long stretch.

**Avoid developer jargon.** Treeti is theory-strong, Python-light. When infrastructure stuff comes up (sandboxes, mounts, VMs, virtual environments), translate or skip. The intellectual value is the finance and the model; the plumbing is incidental.

**Push back when warranted.** Treeti pushes back on conventions — that's a feature, not a bug. Validate good instincts when right; explain the geometry/math when slightly off. Don't bulldoze when the convention is actually defensible. Examples this session: peak vs elbow (Treeti's good instinct; engine narrative reinforced); block ordering (Treeti spotted a real wart, we refactored); input validation now-vs-later (Treeti proposed early asserts, pushback held the math-first principle).

**Save design decisions to memory and to this handoff as they're made.** Conversational decisions that aren't visible in code need persisted notes.

**Tone: direct, honest, warm but not saccharine.** No over-apology, no excessive hedging, no trailing summaries the user can read for themselves. Avoid the words "genuinely", "honestly", "straightforward".

**Treeti's working style: question-driven, not output-driven.** Clarifying questions are healthy engagement, not weakness. When Treeti asks "is this getting too long?" — they're checking your read, not asking you to fix it.

---

## Files of record

`/Users/treetisarkar/Documents/Claude/Projects/MC/dcf.py` — the deterministic DCF engine, containing all seven engine blocks plus the orchestrator `run_dcf`. Read this file at the start of any new conversation to see the current code state. The inline comments are rich on purpose — they're meant to be the canonical documentation, and they encode the design caveats (D&A/capex/NWC modelling assumptions, negative beta, tax shield, single-source WACC, etc.).

`/Users/treetisarkar/Documents/Claude/Projects/MC/sanity_check.py` — end-to-end smoke test. Constructs synthetic inputs, walks every block, prints intermediates, hand-checks worked-example numbers, and verifies `run_dcf` matches manual composition. PASSED.

`/Users/treetisarkar/Documents/Claude/Projects/MC/textbook_verification.py` — Gordon-growth limit test. Constructs a degenerate steady-state where the engine should collapse to `EV = FCF_1 / (WACC − g)`. Verifies across seven forecast horizons with relative gaps at floating-point epsilon. PASSED.

`/Users/treetisarkar/Documents/Claude/Projects/MC/HANDOFF.md` — this document.

---

## What's next (when work resumes) — entering step 3

**Step 3: Monte Carlo machinery.** Wrap `run_dcf(inputs)` in a perturbation loop that produces a distribution of per-share values instead of a single point estimate.

### Conceptual scope of step 3

The MC machinery has three main design questions to settle with Treeti before writing code:

1. **Which inputs to perturb?** Default candidates: every forward-looking trajectory (revenue_growth, operating_margin, capex_pct_revenue, da_pct_revenue, nwc_pct_revenue), plus cost-of-capital ingredients with material estimation uncertainty (beta, equity_risk_premium, sometimes risk_free_rate), plus terminal_growth. Some fields probably stay fixed per company (tax_rate, debt_to_total_capital, shares_outstanding). This is a design conversation, not an assumption to bake in.

2. **What distribution shape for each perturbed input?** Candidates:
   - Uniform within a band (simplest, no distribution-shape assumption — "I don't know").
   - Normal around a central estimate (defensible when uncertainty is symmetric).
   - Lognormal (better for things bounded below at zero, like growth rates that can't go arbitrarily negative).
   - Triangular (good when you have min/mode/max judgements but no theory).
   - Empirical bootstrap from historicals (where the variance signal is real).
   Per-input choice — partly philosophical (uniform = ignorance; normal = central tendency known), partly empirical (what does the historical data look like).

3. **Correlation between perturbed inputs?** Some inputs naturally correlate — revenue growth and operating margin may move together (operational leverage), or risk-free rate and equity risk premium may move opposite. Naive independent sampling underestimates joint behaviour. Approaches: full covariance matrix; copulas (decouple marginals from dependence structure); pairwise correlation rules; no correlation (baseline).

### Sampling structure

Per-year vs per-trajectory sampling for the lists:

- **Per-year independent:** each year's growth rate, margin, etc., drawn independently. More variance, captures "anything can happen" optionality, but underweights persistence.
- **Per-trajectory shock:** one draw scales the whole trajectory. Lower variance, captures persistence, but limits mixed-scenario exploration.
- **Hybrid (likely the right answer):** small number of "regime shocks" per simulation scaling central trajectories, plus small per-year noise.

Real design conversation worth having before coding.

### Architecture sketch (subject to revision)

```python
@dataclass
class MCConfig:
    """Configuration for one Monte Carlo run."""
    n_simulations: int
    perturbation_specs: dict   # input field name → distribution spec
    correlation_matrix: ...    # or None for independent
    random_seed: int | None

def sample_inputs(base: DCFInputs, config: MCConfig) -> DCFInputs:
    """Return one perturbed DCFInputs from the central case."""
    ...

def run_monte_carlo(base: DCFInputs, config: MCConfig) -> List[float]:
    """Run n_simulations independent DCF valuations.

    Returns: list of per-share intrinsic values, one per simulation.
    The distribution lives in this list — analysis (percentiles,
    histogram, mean, std, comparison to market price) happens
    downstream.
    """
    return [
        run_dcf(sample_inputs(base, config))
        for _ in range(config.n_simulations)
    ]
```

Conceptually thin — most complexity is in `sample_inputs` (perturbation + correlation handling), which is the design discussion above.

### Convergence (step 4) is paired with this

Treeti's headline thesis says: don't default to n=10,000. Run MC at varying n, plot scatter of run-means against n, find the empirical elbow z. Step 4 implements that diagnostic. Step 3's `run_monte_carlo` is the engine the convergence step calls at different n values. So **step 3 should NOT pick an n upfront** — `n_simulations` is a config field; step 4 explores it.

### Suggested teach-mode rhythm for step 3

Same as before: concept → numerical example → pseudocode → Treeti reviews → Claude writes Python → walkthrough → review. Likely sub-blocks:

1. Perturbation specification (what gets perturbed, what shape).
2. Single-sample input generator (`sample_inputs`).
3. Multi-sample runner (`run_monte_carlo`).
4. Diagnostic summaries (mean, median, percentiles, histogram).
5. Smoke test against the deterministic case (zero-perturbation → single-point distribution).

---

## How to use this document

If you are a fresh Claude in a new project or conversation picking up this work: read this document end-to-end before responding to Treeti. Then read `/Users/treetisarkar/Documents/Claude/Projects/MC/dcf.py` to ground yourself in the code state, and skim `sanity_check.py` and `textbook_verification.py` to see how the engine was verified. Then proceed in teach mode with bilingual delivery. Don't re-litigate decisions already made unless Treeti raises them. Trust this document on the working patterns; honour the rhythm.

If you are Treeti reading this: paste this document verbatim into the new conversation as the first message, OR upload the file and ask the new Claude to read it. Either way the next Claude has what it needs. If the new project has memory, you can also ask the new Claude to seed memory from this handoff.

---

## SESSION UPDATE — 2026-05-29 (step 3 design phase complete; mid-implementation on task 5)

This section is additive to (not a replacement for) the prior sections of this document. The build sequence, intellectual thesis, tech stack, point of view, and step-2 design decisions are all still current. This section captures what changed during the 2026-05-29 session.

### Step 3 design conversations — all four locked

The four design conversations identified at the end of step 2 ("which inputs to perturb, what distribution shapes, correlation between inputs, sampling structure") are all settled and documented in detail in `design_decisions_mc_step3.md` (in Treeti's auto-memory directory). Headline:

**1. Perturbation scope.** Eight dials wiggle: `revenue_growth`, `operating_margin`, `capex_pct_revenue`, `da_pct_revenue`, `nwc_pct_revenue`, `terminal_growth`, `beta`, `equity_risk_premium`. Fields held fixed include `starting_revenue`, `net_debt`, `shares_outstanding`, `forecast_years`, `tax_rate`, `debt_to_total_capital`, `risk_free_rate`, `cost_of_debt`. The cost-of-capital ingredients held fixed (risk-free rate, cost of debt) could be revisited later but were deemed "roughly observable today" for v1.

**2. Distribution shapes.** Bell curve (normal) for seven dials; triangular for `terminal_growth` (TG sits in a narrow defensible band, roughly 1.5–3%, with no real "center plus noise" intuition). Skewness was REJECTED as its own modelling layer — most of the bad-side asymmetry it tries to capture (margin collapse, capex blowouts, recession sharpness) is event-driven and properly belongs to the step-5 shock overlay. Architecture is two clean layers — Gaussian noise + discrete shocks — not three. Treeti's instinct that per-variable "natural" shapes (triangular for business-process variables, skewed for asymmetric ones) are more realistic is acknowledged as correct but parked as future work for v1 debuggability.

**3. Correlation handling.** Pairwise rules. Three pairs in v1: `revenue_growth × operating_margin` (+0.5, operational leverage), `capex_pct_revenue × revenue_growth` (+0.4, growth needs investment), `beta × equity_risk_premium` (+0.1, weak shared market-stress driver — Treeti correctly pushed back on the initially-proposed +0.3, noting beta is firm-specific and ERP is market-wide). Coefficients are correlations of the *wiggle*, not of the *levels*. Flagged for later (Phase 2): `D&A × capex`, `NWC × revenue`. Full covariance matrix rejected as overkill; copulas as Phase 2/3 work.

**4. Sampling structure.** Hybrid: persistent trajectory perturbation + small per-year noise, applied to all five list-valued dials. Per-year independent rejected (radio-static behaviour misrepresents persistence); per-trajectory shock alone rejected (lockstep misses realistic year-to-year variation). Correlations attach at the trajectory-perturbation level, NOT the per-year noise level. Scalar dials (terminal_growth, beta, ERP) get a single draw per simulation. Terminology note: we deliberately use "perturbation" not "shock" — Treeti reserved "shock" for the step-5 micro shock overlay and potential regime modelling, to avoid naming collisions. Calibration widths (~10–15% trajectory perturbation, ~3–5% per-year noise) are INITIAL DEFAULTS subject to revision after first simulations, NOT permanent architecture.

### Implementation phase — mid-flight on task #5 (MCConfig)

After the design phase we started implementation, working through the teach-mode rhythm on `MCConfig`. The concept beat landed: MCConfig is a dataclass that holds per-run parameters.

Treeti caught an important over-engineering instinct in my first sketch — I had MCConfig holding the distribution shapes, widths, and correlations as user-supplied fields, even though those are locked design decisions. Treeti correctly pushed back: the user shouldn't have to re-specify what we already decided.

The revised shape that was agreed-in-principle but NOT yet implemented in code:

- `MCConfig` holds only `n_simulations` (required) and `random_seed` (optional).
- Distribution shapes, widths, correlations live as module-level defaults the runner reads automatically.
- Overrides exist via optional fields (`correlation_overrides`, `width_overrides`) but most simulations use defaults.
- The common-case call: `config = MCConfig(n_simulations=10000); results = run_monte_carlo(base_inputs, config)`.

### Two open questions at session close — UNRESOLVED, next Claude picks these up

Treeti raised both via a parallel "checker chat" and asked for my read; I dropped the message (see working pattern refinement #3 below). These need real engagement before code is written.

**Question A — Does MCConfig hold just architecture, or architecture + calibration defaults?** Reframed: should the calibration magnitudes (the ~10–15% / ~3–5% widths) live inside MCConfig (visible to the user as overridable knobs) or live in a separate module-level constants block (hidden from MCConfig, accessed by the runner)? The locked memory says the widths are "initial calibration defaults subject to validation, NOT permanent architecture" — that argues for them being visible and overridable. But making them visible in MCConfig pushes back toward the very ergonomic burden we just decided to avoid. A clean split might be: MCConfig holds only `n_simulations` + `random_seed` + optional override hooks; defaults live as named constants in a module called something like `mc_defaults.py` or at the top of the MC module. Worth deciding deliberately.

**Question B — Should each dial have its own specification object so future distribution upgrades (skew, Student-t, shocks, etc.) can be added cleanly without restructuring the config later?** Reframed: instead of dispatching by dial name with type-specific behaviour scattered across the runner, define a `DialSpec` abstraction (small dataclass per dial) that captures its distribution family, width parameters, and any future fields. The runner iterates `DialSpec`s rather than dial-specific branches. This is a YAGNI-vs-extensibility judgment call. Treeti seemed positive on it — it preserves clean future upgrades to richer distributions when Phase 2/3 work begins.

Treeti's last unanswered question was "where exactly do the defaults live?" That ties directly to Question A. The next Claude should pick this up with a clean concrete answer (name the file or module, name the constants, show the structure as code or pseudocode — not abstract architecture talk).

### Working pattern refinements from this session

Three working rules emerged during the session that the next Claude should carry forward. All three are also saved as separate feedback memories in Treeti's auto-memory directory.

**1. Anchor abstractions with concrete numbers first.** Treeti hit an abstraction wall during the distribution shapes conversation. Each remaining design question was anchored in a Steady Co worked example (with actual numbers, before-and-after tables, illustrative per-share values) BEFORE the abstract pitch. The next Claude should keep doing this for every remaining design question and every implementation beat. Memory file: `feedback_pacing_step3.md`.

**2. Show memory diffs (VS Code style) before locking a decision.** Don't just announce "memory updated" — show the unified diff with +/- markers so Treeti can verify the exact text being written. Treeti explicitly asked for the unified-diff format ("vs code thingy") after seeing a plain code block. The rule applies BEFORE marking a task complete or running the Edit tool on a memory file. Show, wait for explicit confirmation, then save. Memory file: `feedback_show_memory_diff.md`.

**3. Never respond "No response requested" to a user message.** That output is the harness's no-op for non-user system signals. It must never appear as a reply to Treeti. This was violated twice in the session (the "im still looking at them distributions" message on 2026-05-28, and the checker-chat-evaluation message on 2026-05-29); both times Treeti had to send follow-ups containing the same request more explicitly. Memory file: `feedback_no_response_requested.md`.

### Steady Co (the teaching device)

To anchor every design conversation in concrete numbers, the session introduced a fake company called "Steady Co." Central case:

- Revenue today: $1,000M
- Shares: 100M
- Net debt: $300M
- Forecast years: 5
- Revenue growth: 10%, 8%, 6%, 5%, 4% (slowing)
- Operating margin: 15% flat
- Capex %: 7% flat, D&A %: 5% flat, NWC %: 2% flat
- Terminal growth: 2.5%
- Beta: 1.1, Equity risk premium: 5.5%
- Risk-free: 4%, Cost of debt: 5%, Tax: 25%, D/V: 30%

Central run produces ~$12.77/share. This is purely a teaching device — NOT a real company we're building around. The engine remains general-purpose (per the original design philosophy). The next Claude can keep using Steady Co or substitute their own — the point is having SOMETHING concrete to point at when discussing perturbation, correlation, sampling structure, and so on.

### Task state at session close

Tasks 1–4 (the four step-3 design conversations) are complete. Task 5 (MCConfig implementation) is `in_progress` with the architecture agreed in principle but Questions A and B above unresolved before code can be written. Tasks 6–9 (`sample_inputs`, `run_monte_carlo`, diagnostics, smoke test) are pending.

### What the next Claude should do on resume

1. Read this entire HANDOFF.md before responding (especially this session update section — it captures the live state).
2. Read the memory files, especially `design_decisions_mc_step3.md`, for the full step-3 design record with reasoning.
3. Open with a brief check-in — Treeti may want a quick orient before diving in. Don't immediately re-explain things Treeti already knows.
4. Tackle Questions A (defaults location) and B (per-dial spec object) at the same depth and rhythm as the four design conversations that preceded them. Anchor with concrete code or pseudocode rather than abstract architecture talk. Treeti explicitly asked "where exactly do the defaults live" — that's the entry point.
5. Then write the actual Python for `MCConfig`, the defaults module, and any `DialSpec` abstraction — going through the teach-mode rhythm (concept → numerical example → pseudocode → Treeti reviews → code with rich bilingual comments → walkthrough).
6. Keep using the show-the-diff-before-lock rule throughout (also applies to memory writes).
7. Keep watching for the abstraction wall and any "No response requested" misreads.
8. Treeti is tired going into the next session — they put significant energy into the design phase. Pace gently and don't pile on more abstraction than necessary.

---

## SESSION UPDATE — 2026-05-30 (Questions A & B resolved, MCConfig + mc_defaults written, mid-teach-mode on sample_inputs)

This section is additive to (not a replacement for) the prior sections of this document. The build sequence, intellectual thesis, tech stack, point of view, step-2 design decisions, and step-3 design conversations are all still current. This section captures what changed during the 2026-05-30 session.

### Questions A and B from the 2026-05-29 close — both RESOLVED

**Question A (where calibration defaults live) → Option 3.** `MCConfig` stays small (`n_simulations` required, plus optional `random_seed`, `width_overrides`, `correlation_overrides`). Defaults live as module-level constants in `mc_defaults.py`. The runner reads each value via `(overrides or {}).get(key, defaults.KEY)` so an override transparently takes precedence. Common-case call is one line: `MCConfig(n_simulations=10000)`. Calibration sweep: `MCConfig(n_simulations=10000, width_overrides={"trajectory": 0.15})`.

Reasoning weighed against two alternatives. Option 1 (everything inside MCConfig as visible fields) forced every caller to know calibration knobs they shouldn't need to touch. Option 2 (defaults-only, no override mechanism) made calibration sweeps require either editing the defaults file or runtime monkey-patching — awkward for a thesis whose whole point is that the widths are tentative. Option 3 splits the concerns: design decisions visible in `mc_defaults.py`, per-run variability in `MCConfig`, escape hatch via overrides.

**Question B (per-dial DialSpec object) → flat constants for v1, DialSpec parked.** `mc_defaults.py` holds plain constants and lists. No `DialSpec` dataclass. The dials behave uniformly enough today (normal for seven, triangular for one) that a class would be ceremony without payoff. When Phase 2 adds per-dial skew, Student-t tails, or shock-specific parameters that don't apply uniformly, promote the constants into `DialSpec` dataclasses — a small refactor, not a redesign.

### Code written this session

Two new files in `/Users/treetisarkar/Documents/Claude/Projects/MC/`:

**`mc_config.py`** — `MCConfig` dataclass. Four fields. Required: `n_simulations`. Optional: `random_seed`, `width_overrides`, `correlation_overrides`. Rich bilingual docstring explaining usage, the common-case call, and calibration-sweep override mechanic.

**`mc_defaults.py`** — calibration constants in five sections:
- *Perturbation widths*: `TRAJECTORY_WIDTH = 0.12`, `PER_YEAR_NOISE_WIDTH = 0.04`
- *Correlations*: `CORRELATIONS` dict, three pairs (`operating_margin × revenue_growth = 0.5`, `capex_pct_revenue × revenue_growth = 0.4`, `beta × equity_risk_premium = 0.1`), keyed by alphabetically-sorted tuples. Phase 2 candidates listed in a trailing comment so they don't get lost.
- *Distribution shapes*: `NORMAL_DIALS` (seven names), `TRIANGULAR_DIALS` (just `terminal_growth`)
- *Triangular bounds*: `TERMINAL_GROWTH_LOW = 0.015`, `TERMINAL_GROWTH_HIGH = 0.030`
- *Fields held fixed*: documentation block listing the eight `DCFInputs` fields that stay at central-case values across every simulation, and why each one is fixed

`dcf.py` was not touched. The MC files import nothing from `dcf.py` yet; they're standalone configuration / constants.

### Terminology decision — "regime" is RESERVED

Treeti made an important terminology call mid-session: the word **"regime"** is RESERVED for a future modelling layer that may introduce true macro states (Expansion / Normal / Recession / Stress) with state-dependent distributions. What we have today is NOT regime modelling — it's persistent trajectory-level perturbation on top of central forecasts.

**Use:** "trajectory perturbation", "persistent trajectory perturbation", "trajectory-level uncertainty", "trajectory-level correlation".

**Avoid:** "regime shock", "regime uncertainty", "high-growth regime", "margin-compressed regime".

Status: the inline comment in `mc_defaults.py` (lines 38–43) was updated by Treeti to reflect this. Inline comments referencing a "persistent regime" elsewhere in `mc_defaults.py` (line 49) should be cleaned up in the next session. Future code comments, docstrings, and conversation should follow the rule. The terminology lives in memory as `terminology-regime-reserved.md`.

### Mid-flight: teach-mode beat on `sample_inputs`

When the session ended, I was partway through the teach-mode beat for `sample_inputs` — specifically the mechanics of correlation injection. Delivered so far:

- **Three layers** of perturbation, stacked per dial: regime draw (one number per dial per simulation, rescales whole trajectory for lists, IS the perturbation for scalars), per-year noise (small independent jitter on list dials), triangular for `terminal_growth` (independent, in defensible band).
- **2×2 Cholesky worked example** on revenue_growth × operating_margin with correlation 0.5. Showed L = [[1, 0], [0.5, 0.866]]. Walked through Z = [+1.0, −0.5] → W = [+1.0, +0.067] and explained how revenue's positive draw pulled margin upward despite margin's own independent draw being negative. Then converted to multiplicative scaling using `TRAJECTORY_WIDTH = 0.12` and applied to Steady Co's central revenue and margin trajectories.
- **7×7 matrix structure** sketched (1.0 on diagonal, three off-diagonal correlations, zeros elsewhere). Mentioned `numpy.linalg.cholesky` as the tool.
- **PSD constraint** flagged — the correlation matrix has to be positive semi-definite for Cholesky to work; v1 spec is fine but a future change could break it.

Note: the regime/terminology rule above arrived AFTER this teach-mode content was delivered, so the words "regime draw" and "high-growth regime" appear in the delivered explanation. Next Claude should re-frame as "persistent trajectory perturbation draw" / "high-growth trajectory" when continuing the beat.

**Where the conversation paused:** I asked "Want me to push forward to pseudocode, or pause here — anything in the Cholesky mechanic that didn't quite land?" Treeti then surfaced the regime/terminology issue, and shortly after asked for this handoff update. `sample_inputs` pseudocode and code have NOT been written yet.

### Working pattern violation this session — "No response requested" recurred TWICE

The 2026-05-29 session captured a feedback rule: never respond "No response requested" to a user message. This 2026-05-30 session VIOLATED that rule TWICE — once after Treeti's terminology suggestion (the message arrived with substantive content and "Continue from where you left off"; I should have acknowledged the terminology decision and continued the `sample_inputs` beat), and once after the first handoff-update request (Treeti explicitly asked to update the handoff and start in another chat; I should have started writing immediately).

**This is the FOURTH and FIFTH recurrence across sessions.** The next Claude must treat any Treeti message — including ones that arrive bundled with a system-reminder, including ones that end with editorial framing rather than a question mark — as requiring substantive engagement. If "No response requested" forms in the draft reply, stop, re-read the user message, and write a real response. Persisted in memory as `feedback-no-response-requested.md`.

### Task state at session close

- Task 1 (Question A — defaults location): completed
- Task 2 (Question B — DialSpec): completed
- Task 3 (MCConfig + defaults module): completed
- Task 4 (sample_inputs implementation): in progress — teach-mode partly delivered (concept + Cholesky math); pseudocode and code NOT yet written; terminology cleanup needed in the delivered narrative
- Task 5 (run_monte_carlo): pending
- Task 6 (diagnostic summaries): pending
- Task 7 (smoke test — zero-perturbation → deterministic): pending

### What the next Claude should do on resume

1. Read this entire HANDOFF.md, especially this 2026-05-30 update section.
2. Read `mc_config.py`, `mc_defaults.py`, and `dcf.py` in `/Users/treetisarkar/Documents/Claude/Projects/MC/` to ground in the current code state.
3. Read the memory files (`terminology-regime-reserved.md`, `project-mc-engine.md`, `design-decisions-mc-step3.md`, `feedback-no-response-requested.md`, `feedback-pacing-step3.md`, `feedback-show-memory-diff.md`). The embedded copies below also work if memory isn't carried across spaces.
4. Open with a brief check-in. Don't re-explain the four design conversations, Questions A/B, or the Cholesky concept beat — Treeti already has those.
5. Pick up the `sample_inputs` teach-mode beat where it paused. Cholesky math was delivered; next is pseudocode → Treeti reviews → Python with rich bilingual comments. **Re-frame the delivered narrative using "trajectory perturbation" language, not "regime".**
6. Honour the regime terminology rule everywhere — code comments, docstrings, conversation.
7. **Never write "No response requested" as a reply to Treeti.** Ever.
8. Anchor abstractions with concrete numbers (Steady Co central case ~$12.77/share — see `feedback-pacing-step3.md` for the parameter set).
9. Show memory diffs in VS Code unified-diff format (+/- markers) before locking memory writes.
10. Treeti was tired enough mid-session to ask for a handoff. Pace gently.

---

## EMBEDDED MEMORY (so memory travels with this document)

Memory files captured for the 2026-05-30 close. The next Claude should save these into its memory directory at the start of the conversation. If the new conversation is in the same memory space, they should already be present at the paths below.

### `memory/terminology-regime-reserved.md`

```markdown
---
name: terminology-regime-reserved
description: For the MC engine, "regime" is held for future macro-state modelling; use "trajectory perturbation" terminology for the current persistent perturbation layer.
metadata:
  type: feedback
---

For the Monte Carlo Valuation Engine, the word "regime" is RESERVED for a future modelling layer that may introduce true macro states (Expansion / Normal / Recession / Stress) with state-dependent distributions.

**Why:** Treeti can see themselves introducing genuine regime modelling later. Using "regime" today for what is actually persistent trajectory-level perturbation would force a painful rename when the real regime layer arrives, and risks the two concepts blurring.

**How to apply:** Use "trajectory perturbation", "persistent trajectory perturbation", "trajectory-level uncertainty", or "trajectory-level correlation" for the current layer. Avoid "regime shock", "regime uncertainty", "high-growth regime", "margin-compressed regime" — both in code comments and in conversation.
```

### `memory/feedback-no-response-requested.md`

```markdown
---
name: feedback-no-response-requested
description: Never respond "No response requested" to a Treeti message. That phrase is the harness's no-op for non-user signals; replying it to a user message is always a failure.
metadata:
  type: feedback
---

Never reply "No response requested" to a message from Treeti. That output is the harness's no-op for non-user system signals — it must NEVER appear as a reply to an actual user message.

**Why:** Treeti experienced this multiple times. The 2026-05-28 "im still looking at them distributions" incident, the 2026-05-29 checker-chat-evaluation incident, and a TRIPLE recurrence on 2026-05-30 (twice in one session — once after the regime/terminology message and once after the first handoff-update request). Every time, Treeti has to send a follow-up containing the same content more explicitly. It wastes the session and signals the assistant isn't reading carefully.

**How to apply:** Any message that came from Treeti — whether or not it ends with "Continue from where you left off", whether or not it's prefixed with a system-reminder, whether or not it explicitly asks a question — requires substantive engagement. The presence of editorial framing or a polite suggestion does NOT mean the user is signalling "no reply needed". If you see "No response requested" forming in your draft reply to Treeti, stop and write a real response.
```

### `memory/feedback-pacing-step3.md`

```markdown
---
name: feedback-pacing-step3
description: Anchor abstractions with concrete numbers (Steady Co) before the abstract pitch. Treeti hits an abstraction wall otherwise.
metadata:
  type: feedback
---

For design conversations and implementation beats, anchor abstract architecture with concrete numbers (Steady Co worked example) BEFORE the abstract pitch.

**Why:** Treeti hit an abstraction wall during the distribution-shapes conversation in the 2026-05-29 session. Switching the format — each design question opened with actual numbers, before-and-after tables, illustrative per-share values — restored momentum immediately.

**How to apply:** Whenever introducing a new technical concept, distribution, matrix operation, or architectural pattern, lead with a numerical example using the Steady Co central case (revenue 1000M, 100M shares, 300M net debt, 5-year forecast with growth [10,8,6,5,4]%, 15% margin flat, 7% capex, 5% D&A, 2% NWC, terminal 2.5%, beta 1.1, ERP 5.5%, rf 4%, cost of debt 5%, tax 25%, D/V 30%, central ≈ $12.77/share). Show the operation on Steady Co's numbers, THEN explain the abstract mechanic.
```

### `memory/feedback-show-memory-diff.md`

```markdown
---
name: feedback-show-memory-diff
description: Before locking a memory write or design decision, show the unified diff (+/- markers, VS Code style) so Treeti can verify the exact text being persisted.
metadata:
  type: feedback
---

Before marking a task complete or writing/editing a memory file, show the unified diff (+/- markers, VS Code style) of the change. Wait for explicit confirmation, then save.

**Why:** Treeti explicitly asked for the unified-diff format ("vs code thingy") in the 2026-05-29 session after seeing a plain code block. The reason is verification: a plain code block doesn't reveal what's being added vs removed, so Treeti can't catch a subtle wording shift in the locked text.

**How to apply:** When proposing a memory write, surface the change as a diff (`-` for removed lines, `+` for new lines, plain for unchanged context). For a new memory file, every line is `+`. The rule applies BEFORE running the Edit/Write tool, not after.
```

### `memory/design-decisions-mc-step3.md`

```markdown
---
name: design-decisions-mc-step3
description: Full record of the four locked design decisions for Monte Carlo step 3 (perturbation scope, distribution shapes, correlation, sampling structure) plus Questions A and B resolved 2026-05-30.
metadata:
  type: project
---

Six locked design decisions for step 3:

**1. Perturbation scope.** Eight dials: revenue_growth, operating_margin, capex_pct_revenue, da_pct_revenue, nwc_pct_revenue, terminal_growth, beta, equity_risk_premium. Held fixed: starting_revenue, net_debt, shares_outstanding, forecast_years, tax_rate, debt_to_total_capital, risk_free_rate, cost_of_debt.

**2. Distribution shapes.** Normal for seven; triangular for terminal_growth (band 1.5–3%). Skewness rejected as its own layer — asymmetric phenomena belong to step-5 shock overlay.

**3. Correlation handling.** Pairwise rules, three pairs: revenue_growth × operating_margin = +0.5, capex_pct_revenue × revenue_growth = +0.4, beta × equity_risk_premium = +0.1. Phase 2: D&A × capex, NWC × revenue. Correlations of the wiggle, not the levels. Applied at trajectory-perturbation layer only; per-year noise independent. Mechanic: Cholesky on a 7×7 matrix.

**4. Sampling structure.** Hybrid: persistent trajectory perturbation (one draw per dial per simulation, rescales whole trajectory) + per-year noise (independent draws, list dials only). Initial widths: ~12% trajectory, ~4% per-year. Subject to revision post-convergence.

**5. Question A — defaults location (Option 3).** MCConfig small (n_simulations + random_seed + override hooks). Defaults in mc_defaults.py. Runner reads `(overrides or {}).get(key, defaults.KEY)`.

**6. Question B — DialSpec (parked).** Flat constants in mc_defaults.py for v1. Promote to DialSpec dataclasses in Phase 2 if/when dial behaviour diverges.
```

### `memory/project-mc-engine.md`

```markdown
---
name: project-mc-engine
description: Monte Carlo Valuation Engine project — Treeti's flagship portfolio piece, currently mid-step-3 implementation. Engine is general-purpose; companies are case studies.
metadata:
  type: project
---

Treeti is building a Monte Carlo Valuation Engine as project #1 of a six-piece quant-finance portfolio. The engine produces a *distribution* of intrinsic values per share, not a point estimate, with two distinguishing features: a discrete micro shock event overlay (state-conditional probabilities) and a convergence analysis module (per-company empirical n*).

**Current state (2026-05-30):** Step 1 done, step 2 done (verified by sanity_check.py and textbook_verification.py at floating-point epsilon), step 3 mid-implementation (design locked, mc_config.py + mc_defaults.py written, sample_inputs teach-mode in progress). Steps 4–7 not started.

**Files of record (in /Users/treetisarkar/Documents/Claude/Projects/MC/):** dcf.py, sanity_check.py, textbook_verification.py, mc_config.py, mc_defaults.py, HANDOFF.md.

**Working patterns:** teach mode (concept → numerical example → pseudocode → review → Python with rich bilingual comments → walkthrough). Bilingual delivery. Push back when warranted. Save design decisions to memory and HANDOFF. Direct, honest, warm tone. Treeti is theory-strong, Python-light.
```

---

## SESSION UPDATE — 2026-05-30 (step 3 COMPLETE)

This section is additive. Everything above remains current. This update closes step 3 of the build sequence: the Monte Carlo machinery is written end-to-end and verified.

### Code written this session

**`mc_engine.py`** (new) — three pieces:

- `sample_inputs(base, config, rng)` — returns ONE perturbed DCFInputs from the central case. Implements the locked design: a correlated, persistent trajectory perturbation on the seven normal dials (Cholesky factorisation of the 7×7 correlation matrix, scaled by `TRAJECTORY_WIDTH`), plus independent per-year noise on the five list dials (scaled by `PER_YEAR_NOISE_WIDTH`), plus a triangular draw on `terminal_growth`. Perturbations are MULTIPLICATIVE (`value × (1 + draw)`) for the seven normal dials; terminal_growth is an absolute draw from its band. The eight fixed fields carry over via `dataclasses.replace`. Two private helpers: `_build_correlation_matrix` and `_correlated_normal_draw`.
- `run_monte_carlo(base, config)` — the thin n-loop. Creates ONE seeded numpy generator (from `config.random_seed`) and threads it through every `sample_inputs` call, then returns the list of `run_dcf` per-share values. Picks no n (step 4 sweeps it).
- Diagnostics: `MCSummary` dataclass, `summarize(results, market_price=None, percentiles=...)`, `format_summary`, `text_histogram`. The headline output is `market_percentile` — where today's price falls inside the simulated distribution (the project thesis: price vs distribution, not vs a point).

**`mc_smoke_test.py`** (new) — three tests, all PASS: (1) zero-perturbation collapse — both widths set to 0, every one of 1000 sims equals `run_dcf(base)` = $12.7662054824 exactly (spread 0.00e+00); (2) perturbation-on produces spread (std > 0.5, guards against a silently-broken perturbation faking determinism); (3) seed reproducibility (same seed identical, different seed differs).

`dcf.py`, `mc_config.py`, `mc_defaults.py` were not structurally changed.

### Design decision recorded this session — terminal_growth off-switch

`terminal_growth` is triangular, so its dispersion comes from the (1.5%, mode, 3.0%) band, not a width knob — zeroing the widths wouldn't otherwise freeze it. Decision: `sample_inputs` treats `TRAJECTORY_WIDTH == 0` as "perturbation off everywhere" and holds terminal_growth at its central (mode) value. This gives the engine a clean deterministic mode and is what makes the zero-perturbation smoke test collapse exactly. Claude's judgment call, accepted by Treeti at step-3 close. To revisit (e.g. make terminal_growth always-stochastic), see section 2c of `sample_inputs`. Also in memory: `design-decisions-mc-step3.md` (#7).

### Observed behaviour (Steady Co, n=10,000, seed 42)

Mean $12.72, median $12.38 (mild right-skew from multiplicative perturbation + DCF convexity — fat-tail behaviour emerging before any shock overlay), std $4.64, 5th–95th band $5.66–$20.85. The spread is WIDE (~36% of center). Not wrong, but a reminder that the v1 widths (12% / 4%) are tentative — tightening is a step-4 conversation once convergence shows how stable the distribution is. Do NOT retune widths before step 4.

### Process lesson — folder access at session start

This session opened with only the folder "MC block 3 Continuation" connected, which held just HANDOFF.md — none of the code. The actual code lives in `/Users/treetisarkar/Documents/Claude/Projects/MC/`, which had to be connected explicitly before any work could happen. Next session: if the mounted folder doesn't contain `dcf.py` / `mc_engine.py`, connect `Projects/MC` first. Saved in memory as `reference-mc-code-folder.md`.

### Housekeeping carried forward (not yet done)

The line-49 comment in `mc_defaults.py` still says "persistent regime" — needs the terminology cleanup (use "trajectory perturbation", per `terminology-regime-reserved.md`). Cosmetic; do it next time `mc_defaults.py` is opened.

### What the next Claude should do on resume — entering step 4

1. Read this update and the memory files (especially `design-decisions-mc-step3.md`, `reference-mc-code-folder.md`).
2. Connect `Projects/MC` if the code isn't already reachable.
3. Step 4 is **convergence analysis** — the headline thesis. Run `run_monte_carlo` at increasing n, plot the scatter of run-means against n, find Steady Co's empirical elbow (z) instead of defaulting to 10,000. `run_monte_carlo` is the engine the convergence step calls at varying n — it deliberately takes n as a config field, so nothing needs changing in step 3's code to support this.
4. Keep the teach-mode rhythm, bilingual delivery, Steady Co anchoring, regime-terminology rule, and never "No response requested".

### Task state at session close

Step 3 sub-tasks all complete: sample_inputs, run_monte_carlo, diagnostics, smoke test. Step 4 (convergence) not started.
```

---

## SESSION UPDATE — 2026-05-30 (step 4 COMPLETE and LOCKED; entering step 5 next)

This section is additive. Everything above remains current. Step 4 — convergence analysis, the project's headline feature — is now built, stress-tested, and locked. The next session starts step 5 (the micro-shock overlay). Read this section and `design-decisions-mc-step4.md` (memory) before responding.

### What got built

Three new files in `Projects/MC`:

- **`mc_convergence.py`** — the convergence module. Computes a per-company empirical sample size z* instead of defaulting to the folk-wisdom 10,000. Reuses `run_monte_carlo` untouched (convergence IS the engine called at varying n, never a second valuation path). Analysis and plotting are separate functions (mirrors `summarize`/`MCSummary`).
- **`mc_defaults.py`** — extended with the step-4 knobs: `N_GRID`, `BATCHES_PER_N` (=40), `CONVERGENCE_PRECISION_PCT` (=0.01), `CONVERGENCE_DECISION_SIGMAS` (=2.0), `MAX_REFINEMENT_BATCHES` (=250).
- Teaching plots: `steady_co_convergence.png` (production result, with error bars).

The deterministic engine (`dcf.py`) and MC machinery (`mc_engine.py`, `mc_config.py`) are unchanged. `mc_smoke_test.py` still PASSES after the `mc_defaults` additions.

### The locked architecture (do NOT re-open without cause)

    default pass → estimate z* → estimate recommended batch count
                 → ONE refinement pass at the (capped) recommended count → STOP.

No iterative self-calibration loop. The refinement is a VALIDATION step, not the start of a recursion. The endpoint is fixed and explicit. Treeti was firm on this.

How z* is defined — layered and conservative: **z* = max(z_pct, z_elbow)**.
- `z_pct` (precision rule): smallest grid n where the scatter of run-means stays below 1% of the valuation, using MONOTONE CLEARANCE — "first n after which it AND all larger n remain under the bar", not "first crossing" (first-crossing gets fooled by the noise in the scatter estimate). This is the scale-free anchor.
- `z_elbow` (diminishing-returns rule): the kneedle bend of the decay curve. Sensitive to the n-range, which is why `N_GRID` is fixed.
- `max()` combiner: an unstable criterion can only ever make us MORE conservative.

The scatter curve tracks σ/√n (CLT) — the engine self-checks against first principles, the same flavour of verification as the Gordon-limit test for the DCF.

### Batch count is graded, not asserted (the deepest idea this session)

`BATCHES_PER_N` is the measurement apparatus. Treating it as a universal constant would just relocate the 10,000-folklore one level up — Treeti caught this. So the engine grades it per company. Each scatter estimate carries closed-form fuzz: a sample standard deviation of B values has SE/s = 1/√(2(B−1)) (~11% at B=40). From that, `batches_recommended = sigmas²/(2·margin²)+1`, where `margin` is how far the z* point clears the bar. Points sitting ~on the bar are irreducible (the `borderline` flag) — a fact about the company, not a defect.

**Why the recursion terminates (the defensible interview one-liner):** closed-form per-point reliability (→ recommended batch count) COMBINED WITH a single empirical z*-stability check (did z* move after refining?). Precision point Treeti insisted on: z* is a nonlinear threshold-crossing of several scatter points, so its reliability is NOT itself the closed form — which is exactly why ONE empirical refinement is the right tool there, not another simulation layer. It is "closed-form + one empirical probe," not "purely analytic."

### The honest-verdict fix (from the stress-test)

`adequately_resolved` and `final_recommendation` are sourced from the pass we END on (refined if present, else default), never assumed. If the refined pass STILL wants more batches than it used, that is reported as a residual and the user decides — the engine does NOT auto-launch another cycle. This was the one substantive gap the stress-test found; it is now closed.

### Public API of `mc_convergence.py`

- `convergence_analysis(base, config=None, batches=None) -> ConvergenceResult` — one sweep; `batches` is a per-run knob (defaults to `BATCHES_PER_N`).
- `convergence_with_recommendation(base, config=None, batches=None, rerun=True) -> ConvergencePair` — the locked two-pass endpoint.
- `plot_convergence(result, save_path, title) -> str` — decay curve + σ/√n overlay + error bars + rule markers. matplotlib imported lazily so the analysis half stays importable without it.
- `format_convergence(result) -> str` and `format_pair(pair) -> str` — text reports.
- `ConvergenceResult` fields: n_grid, scatter, center, sigma_estimate, z_pct, z_elbow, z_star, precision_bar, batch_rel_se, batches_used, batches_recommended, decision_margin_pct, borderline.
- `ConvergencePair` fields: default, refined, z_star_moved, z_star, adequately_resolved, final_recommendation, refinement_capped.

### Steady Co result (the teaching fixture — not a real company)

σ≈$4.60, center≈$12.75. Production grid at 40 batches → z* = 2,000 (monotone clearance is conservative near a wobble at n=1,500; the smooth σ/√n theory crosses ~1,400). ~5x less compute than the folk 10,000. 40 batches graded "a touch under" the ~47 a 2σ-clean call wants — the engine refusing to flatter its own default. Demo at a coarse 12-batch apparatus showed z* read 1,000, then MOVED to 2,000 when re-run at the recommended count — apparatus resolution genuinely changes the answer.

### Documented caveats (implementation details, NOT architecture — don't re-litigate)

- **Grid quantization:** z* can only take values in `N_GRID`; "z* moved" detects grid-cell jumps. True resolution is the grid spacing.
- **Compute cap:** two production-grid sweeps ≈ 2.7M valuations (minutes-scale). The refinement pass is clamped to `MAX_REFINEMENT_BATCHES`; a larger recommendation is reported as a residual. If speed ever matters, parallelize the batch loop or thin the reference run — a later optimization, not a design change.
- **Borderline cutoff** (`batches_recommended > 1000`) is a pragmatic knob; defensible but faintly the kind of round number the project is philosophically against. Could later be re-expressed as "margin below X%".
- The line-49 `mc_defaults.py` "persistent regime" comment cleanup from last session — check whether still outstanding (per `terminology-regime-reserved.md`).

### What the next Claude should do on resume — entering step 5

1. Read this update and the memory files, especially `design-decisions-mc-step4.md`, `design-decisions-mc-step3.md`, `reference-mc-code-folder.md`, and the feedback memories.
2. Connect `Projects/MC` if the code isn't already reachable (the continuation folder may mount with only HANDOFF.md).
3. **Step 5 is the micro-shock overlay** — discrete, state-conditional binary events (CEO departure, regulatory action, customer loss, patent expiry, supply-chain failure) layered onto the continuous distribution, with probabilities that RISE on already-stressed simulation paths (the death-spiral mechanic). This is layer two of the deliberately-two-layer design (Gaussian perturbation + discrete shocks; skew was rejected as a third layer in step 3). Reserve the word "shock" for this layer; "regime" stays reserved for future macro-state modelling.
4. Then **step 6** re-runs convergence with shocks: σ rises, tails fatten, z* shifts up to z**. The gap between the continuous-only z* and the post-shock z** is itself a headline finding worth reporting.
5. Keep the teach-mode rhythm (concept → Steady-Co numerical anchor → pseudocode → Treeti reviews → Claude writes Python with bilingual comments → walkthrough), anchor abstractions with concrete numbers FIRST, show memory diffs (VS Code style) before locking, and never reply "No response requested".

### Optional un-banked demonstration (parked, not required)

A contrasting-company comparison — a tame firm vs a deliberately fat-tailed one — run through the convergence engine to SHOW z* and the recommended batch count both move across companies. Would bank a clean visual that the step-4 thesis generalizes beyond Steady Co before shocks are added. Treeti chose to defer this to a future chat; pick it up only if Treeti wants it.

### Task state at session close

Step 4 COMPLETE and LOCKED (all four sub-tasks: concept beat, elbow-definition decision, pseudocode, Python + plot + honesty fix + compute cap + caveats). Smoke tests pass. Step 5 (micro-shock overlay) not started — it is the next session's work.

---

## SESSION UPDATE — 2026-05-31 (step 5 PHILOSOPHY phase — channels + three-layer architecture + fragility fork; NO code yet)

This section is additive. Everything above remains current. This session wrote NO code — `dcf.py`, `mc_engine.py`, etc. are untouched. It was pure first-principles architecture for step 5 (the micro-shock overlay). Treeti is DELIBERATELY building the conceptual architecture before any mechanics, probabilities, or code — honour that ordering. Read this whole section before responding; do not jump to hazard rates or implementation.

### The framing Treeti insisted on (and was right about)

Step 5 must stay **industry-agnostic**. NOT a giant list of real-world events (customer loss, patent expiry, recall, regulatory action). Those explode in complexity and become sector-specific. Instead: a SMALL set of universal **transmission channels** — the distinct ways value gets damaged — and real-world events are just *manifestations* of those channels. Steady Co remains a pure teaching prop; Treeti re-affirmed this session that the engine is NOT shaped around it.

### The five shock channels (provisionally locked)

Each channel = an exogenous damage mechanism entering the DCF at a structurally distinct point:

1. **Revenue shock** -> `revenue_growth` (top of operating cascade; scales everything below).
2. **Margin shock** -> `operating_margin` (profit conversion; independent of volume).
3. **Funding / credit shock** -> WACC via `cost_of_debt` (and arguably `beta`) — the *denominator*, not cash flow.
4. **One-off cash shock** -> a *level* hit (net debt / direct value deduction), not a rate.
5. **Strategic growth shock** -> `terminal_growth` (permanent franchise impairment, not an in-forecast dip).

Real events map onto these: customer loss -> revenue; new competitor -> revenue and/or margin; recall -> margin and/or cash; patent expiry -> revenue + margin + terminal; downgrade -> funding.

### The selection principle and its stress-test (intellectual core of the session)

Treeti's first proposal: *"a channel is legitimate iff it maps to a distinct DCF entry point."* Treeti then asked me to BREAK it. Four attacks:
1. **Over-generation** — literally it yields ~16 channels (every `DCFInputs` field is a distinct entry point), not 5. So it's necessary but NOT sufficient: a well-formedness check, not a generator.
2. **Funding already bundles entry points** (`cost_of_debt` + `beta`) — so we're really grouping by *economic mechanism*, not entry point.
3. **Distinct entry point != distinct effect** — TV is anchored on FCF_N, so a late-year revenue shock also drags terminal value; channels are coupled through the engine's own plumbing (matters later for escalation/correlation).
4. **(The important one.) Some value destruction has NO DCF entry point** — bankruptcy / going-concern collapse / fraud / delisting. Gordon growth assumes a surviving perpetuity, so a pure dial-perturbation framework structurally CANNOT produce true zeros — which is exactly the fat left tail step 5 exists to create. Default is a discontinuity / absorbing state, not a deep dial draw.

**Resolution — the real selection rule: a channel must be EXOGENOUS, FIRST-ORDER, and ECONOMICALLY DISTINCT.** The entry-point principle survives but DEMOTED to a non-redundancy guardrail (every channel hits a real transmission point; no two claim the same one). The generator is the three-part rule:
- *First-order*: revenue sits atop the waterfall; capex/D&A/NWC are modeled as % of revenue so they're DOWNSTREAM consequences, not primitive sources -> no capex channel.
- *Exogenous*: did it happen TO the company (channel) or did the company CHOOSE it (response)? Sorts dilution and default OUT of the channel layer.
- *Economically distinct*: groups entry points into mechanisms (funding = cost_of_debt + beta).

### The three-layer architecture (session's main product — provisional)

    Layer 1  CHANNEL     = exogenous damage. How damage ENTERS the valuation. (The five above.)
    Layer 2  ABSORPTION  = endogenous response. How strongly THIS company feels the damage
                           (customer concentration, balance-sheet strength, cash buffer).
                           Same shock, different damage. DILUTION lives here.
    Layer 3  OUTCOME     = endogenous terminal state. What accumulated stress PRODUCES
                           (recover / struggle / distress / DEFAULT). Default is an ABSORBING STATE
                           here — NOT a channel, NOT absorption.

The **exogeneity test** sorts the three: channels happen *to* the firm; dilution and default happen *because of how the firm absorbs* — so dilution -> absorption, default -> outcome. This answered Treeti's long-standing "are we modelling the shock or how much the company can take before bankruptcy?" — BOTH, but in different layers.

### Dilution verdict + cash-shock wrinkle

- **Dilution -> (b) absorption layer**, not a sixth channel. Qualifies under the strict entry-point rule (`shares_outstanding`) but FAILS the exogeneity test — rescue equity is a *response*, not an initiating shock.
- **Cash shock is the odd one out for implementation:** FCF is built bottom-up from revenue x margin; there is NO existing slot for "subtract $X in year t." The cash channel will need a NEW transmission point added to the engine, unlike the other four which ride existing dials. Bank this before pseudocode.

### Damage-model vs narrative-model fork — RESOLVED as a false dichotomy

Treeti (via a parallel checker chat) leaned toward "possible outcomes / branching futures" over a fixed mechanical hit, but worried it means authoring outcome trees (Path A recover / B struggle / C distress) -> complexity explosion. **Resolution: in a Monte Carlo the two designs are the SAME engine at two zoom levels.** You do NOT author branches. Make each shock STOCHASTIC (random whether it fires, random magnitude) + STATE-CONDITIONAL (an already-hit path is likelier to be hit again), run 10,000 paths, and outcome clusters EMERGE:
- most paths: no shock -> cluster ~$12.75 ("recover")
- some: one revenue shock -> ~$9-11 ("struggle")
- few: revenue shock raises hazard -> funding shock follows -> ~$5-7 ("distress")
- thin sliver: cascade -> absorbing default -> ~$0-3
Nobody writes A/B/C. The histogram IS the set of stories. One path = "damage"; 10,000 paths = "stories." Design 2 richness with Design 1 simplicity, for free. The fat tail is produced by the escalation rule, not authored narratives.

### THE OPEN QUESTION — fragility / escalation mechanic (this is where to RESUME)

The one load-bearing decision left: **after a path is hit, what exactly makes it more fragile (raises the probability of the next shock)?** Two candidates discussed, NOT decided (Treeti was too tired to lock; explicitly deferred to next session):

- **V1 — event counting.** Fragility = number of prior shocks. 0 shocks normal; 1 shock -> future probs x1.5; 2 -> x2.0; 3 -> x3.0. Pros: trivial to explain/code. Con: a tiny shock and a massive shock count equally.
- **V2 — value deterioration.** Fragility = current path value / starting value. Still at 95% -> not fragile; down to 40% -> very fragile. Pros: reuses a number the engine ALREADY computes (no separate counter), big hits matter more than small ones, economically sensible. Con: must decide *when* in the path to evaluate value.
- **V3 — financial fragility (FUTURE, way later).** Fragility driven by genuine financial deterioration: interest coverage weakening, debt burden rising, margins collapsing. Closest to reality, but much more machinery (effectively a balance-sheet/coverage sub-model). Explicitly OUT of scope for v1 — Treeti wants to revisit it in a much later iteration. Keep the conversation open; do NOT build it now.

**CONFIRMED 2026-05-31 (Treeti locked the verdict):**
- **V2 is the default fragility metric** (value deterioration). One philosophy, NOT a user-selectable mode — do NOT offer V1/V2 as "basic vs advanced" knobs (that's the ergonomic trap step 3 rejected).
- **V1 is the back-pocket fallback** — used only if V2 misbehaves once we see real path behaviour.
- **V3 is kept explicitly open for "way later"** — a future richer iteration, not v1.
Open sub-question still to settle when coding V2: *at what point(s) in the path is value evaluated* to compute the current/starting ratio (each forecast year? a running re-valuation? a checkpoint?). Decide this with Treeti during the fragility-mechanic beat.

### Parked future layer — recovery / management-response (CONFIRMED 2026-05-31: SEPARATE PROJECT, not step 5, not a layer of the engine)

Treeti surfaced an idea: something AFTER the MC giving "direction on how to recover" — what management should DO to change the odds. **Decision settled 2026-05-31: this is a SEPARATE PROJECT, not a layer in the valuation engine.** The test that settled it: this engine answers a *descriptive* question ("what is the company worth / what can happen to it?"); the recovery idea answers a *prescriptive* one ("what should management do?"). They differ on every axis — output (valuation distribution vs ranked actions), user (investor/analyst vs strategist/management), method (forward simulation vs re-running counterfactual interventions and comparing). Different question + user + output + method = different project.

**Important distinction NOT to conflate (two things both called "recovery"):**
- *Recovery as path dynamics* — after a shock, does a path partially HEAL over later years instead of decaying forever? This is descriptive (still "what can happen") and is a legitimate small candidate to live INSIDE step 5's outcome modelling, so shocked paths don't only ever fall. This stays in scope for the step-5 discussion.
- *Recovery as prescription* — "what action should the company take, re-run, compare before/after." THIS is the separate project. Treeti's phrasing ("direction on how to recover", "what should the company do") is squarely this one.

**Where it belongs in the portfolio:** Shock-Analyser-ADJACENT, or its own standalone piece — TO BE DISCUSSED LATER. The Shock Analyser project is already the analytical-shock sibling to this engine's event overlay, so a mitigation/decision extension is a natural neighbour. NOT decided whether it folds into Shock Analyser or stands alone — park that for a future portfolio conversation.

**The only thing step 5 must respect to keep this door open:** the engine already supports re-running with modified `DCFInputs` (an intervention = altered inputs, re-valued). Nothing to build now — just don't bake in any assumption that inputs are fixed across a run. Current design already honours this.

NOTE: Treeti believes there is a standalone "six-projects portfolio" file (lists MC engine, Shock Analyser, Annual Report Dissection, Expectations Gap Model, Sector Deep Dive Dashboard, Excel Data Toolkit). It is NOT in the connected folders (MC, MC block 3 Continuation) as of 2026-05-31 — it likely lives in another, unconnected folder. This recovery/decision-analysis idea should be copied into that portfolio file once it's located. Captured here in the meantime so it isn't lost.

### Still open (lower priority than the fragility question)

- Pressure-test the exogeneity test itself (is "did the company choose it" always cleanly decidable?).
- Hazard / base probabilities per channel per year — explicitly DEFERRED until fragility is settled. Do not raise early.
- Whether the absorption MIDDLE layer is needed in v1 or deferred to v2 (leaning defer — random shock magnitude already captures "how hard it hit," escalation captures "now fragile").
- Default/going-concern absorbing-state mechanics (agreed it belongs in outcome layer; mechanics unspecified).

### Pacing note — IMPORTANT

Treeti was tiring throughout and repeatedly said they needed sleep. Pace gently; anchor abstractions in concrete Steady Co numbers FIRST (per `feedback-pacing-step3.md`); don't pile abstraction; don't rush to probabilities/code. Treeti is correctly building architecture before mechanics. NEVER reply "No response requested" (this rule was violated again earlier this session — see `feedback-no-response-requested.md`; treat EVERY Treeti message, including ones bundled with system-reminders or ending in editorial framing, as requiring a substantive reply). Show memory diffs (VS Code unified-diff style) before locking any memory write.

### Memory NOT yet updated this session

Next Claude should propose memory writes as diffs and lock with Treeti: (1) step-5 channel taxonomy + the exogenous/first-order/economically-distinct selection rule; (2) the three-layer channel/absorption/outcome architecture + exogeneity test; (3) the fragility V1/V2 fork with V2-default recommendation; (4) parked recovery layer as a future project. Consider folding into a new `design-decisions-mc-step5.md`.

### Task state at session close

Step 5 in PHILOSOPHY/architecture phase. Provisionally locked: 5 channels (via exogenous/first-order/distinct rule); three-layer architecture; damage-vs-narrative fork resolved (emergent outcomes from stochastic state-conditional shocks). NOT locked: the fragility/escalation mechanic (V1 vs V2 — leaning V2). NO pseudocode, NO code. RESUME AT: settle the fragility mechanic, then pseudocode -> Treeti reviews -> Python with bilingual comments -> verify.

---

## SESSION UPDATE — 2026-05-31 (step 5 BUILT, VERIFIED, and LOCKED; ready for step 6)

This section is additive and SUPERSEDES the open questions left by the philosophy update above. Step 5 is now complete: pseudocode reviewed, Python written with bilingual comments, smoke test written and passing. `dcf.py` and `mc_engine.py` were NOT touched — the overlay is a clean add-on, exactly as the architecture promised.

### IMPORTANT — the fragility mechanic EVOLVED past the philosophy update

The philosophy update above (and an earlier read of the fork) leaned toward **V2 = value-deterioration** as the default fragility metric (re-value the path, fragility = current/starting value). **That was reconsidered and REJECTED during implementation.** A parallel checker chat correctly flagged it as turning fragility into a "real-time path-valuation engine" — relocating to a harder problem out of attachment to elegance (the same trap as the convergence-recursion mistake). The LOCKED V1 mechanic is instead a **severity-weighted damage tally**, no re-valuation inside a path:

- Each path carries a running `stress` number. Every shock that fires adds its **severity** (a unit-free 0..1 draw, the ignorance prior) to stress: `stress += weight * severity`, equal weights in V1.
- Stress raises future hazard linearly: `adjusted_hazard = base_hazard * (1 + sensitivity * stress)`, clamped at 1.0. A wounded path is likelier to be wounded again — the death spiral.
- Stress = accumulated FRAGILITY (how primed for the next hit). It is NOT a value estimate and NOT itself a probability. One stress number, two readers: fragility reads it now to raise odds; the V2 outcome layer (deferred) will read the same number for distress/default.

So if the next Claude reads "V2 value-deterioration is the default" anywhere above, that is STALE — the damage-tally approach replaced it. The full current design lives in memory `design-decisions-mc-step5.md` (authoritative over this handoff on any conflict).

### What was built (all in the MC folder)

- **`mc_shocks.py`** — the overlay. `ShockEvent` / `ShockOutcome` dataclasses; `_interp` helper; `apply_shocks(inputs, rng, *, enabled=True, hazards/bands/stress_sensitivity/fragility_weights overrides)` walks each forecast year x each channel, rolls against the stress-adjusted hazard, applies channel-specific damage, accrues stress; `sample_inputs_with_shocks` (perturb-THEN-shock ordering, locked); `run_monte_carlo_with_shocks` (the n-loop, one seeded generator, reuses `run_dcf` untouched). `enabled=False` is the deterministic escape hatch.
- **`mc_defaults.py`** — added the shock knobs: `SHOCK_CHANNELS`, `SHOCK_BASE_HAZARD = 0.0115` (-> `BASE_HAZARDS` per channel), `STRESS_SENSITIVITY = 1.0`, `DAMAGE_BANDS` (revenue/margin 0.15-0.50, funding 0.20-0.80, strategic 0.20-0.60, cash 0.05-0.25), `FRAGILITY_WEIGHTS` (all 1.0). Base hazard tuned so Steady Co stays ~75% shock-free: (1-0.0115)^25 ≈ 0.747.
- **`mc_shocks_smoke_test.py`** — 3 assertions + 1 diagnostic.

### Damage transmission per channel (units differ — this was the key fix)

- **revenue**: persistent haircut on revenue LEVEL, folded into year-t growth (`revenue_growth[t] = (1+g)*(1-damage)-1`) so later years compound off the lowered base ("customer gone for good"). (Earlier bug: haircutting the growth RATE was too weak / indistinguishable from step-3 weather — fixed.)
- **margin**: multiplicative compression from year t onward (`operating_margin[k] *= (1-damage)` for k>=t).
- **funding**: `cost_of_debt *= (1+damage)` (hits WACC, the denominator).
- **strategic**: `terminal_growth *= (1-damage)` (permanent franchise impairment).
- **cash**: one-off outflow `net_debt += damage * revenue_for_sizing[t]`, sized off pre-shock perturbed revenue, undiscounted (documented V1 simplification — PV-ing at WACC is a later refinement). This is the NEW transmission point the philosophy phase flagged (FCF is bottom-up, no slot for a one-off outflow).

### Verification results (smoke test, all PASS)

1. **disabled == pure step-3** — `enabled=False` reproduces `run_monte_carlo` IDENTICALLY under one seed (overlay consumes no RNG, mutates nothing when off).
2. **shocks-on bites ASYMMETRICALLY** — std 4.65->4.94, mean 12.73->11.72, 5th pct 5.58->3.85, floor -0.48->-5.77. Damage lands on the LEFT — fat left tail, not symmetric widening.
3. **seed reproducible** — same seed identical, different seed different.
4. **calibration** — 75.4% shock-free, matching the ~75% Steady Co target.

### TRIP-WIRE FIRED (the documented V2 signal — do NOT "fix" before V2)

Channels fire near-equally (~20% each, by design: equal hazards + equal weights). But among the WORST 5% of paths the mix is lopsided: **margin 47.2%, revenue 21.3%, cash 15.0%, strategic 10.0%, funding 6.6%.** The channels the design said threaten SURVIVAL most (funding/cash) barely drive the worst cascades; margin dominates because its compression is persistent AND multiplicative across every remaining year, while funding only nudges WACC through the 30% debt weight. This is NOT a bug — it is exactly the data-grounded observation V1 was built to expose, and it is the concrete reason to differentiate fragility weights and/or funding/cash damage bands IN V2 (observe-first discipline, same as healing). The equal-weight V1 baseline is the reference point; do not re-tune it before V2.

### V2 backlog (designed, deferred — NOT built)

Healing (stress drifts down on quiet years; only ever REDUCES cascades, so un-healed V1 is the upper-bound baseline); break/distress absorbing outcome states reading the same stress number; differentiated fragility weights / per-channel damage bands (now with the trip-wire as the motivating evidence); per-company hazard calibration (EXOGENOUS — a separate project: Company Characteristics -> Hazard Calibration Layer -> Base Hazards -> Engine; the engine already consumes hazards as a clean input, needs no change). Recovery-as-prescription remains a separate portfolio project.

### RESUME AT — step 6

Convergence round two WITH shocks -> find post-shock sample size z** by running `run_monte_carlo_with_shocks` at varying n and locating the elbow (reuse `mc_convergence.py` machinery from step 4). **The gap between z* (continuous-only, step 4) and z** (shocked) is itself a headline finding** — adding shocks fattens the tails, which should raise the required n. After step 6: step 7 (full input validation layer). Teach-mode rhythm still applies: concept -> Steady Co numbers -> pseudocode -> review -> code -> verify. Show memory diffs before locking. NEVER reply "No response requested."

---

## SESSION UPDATE — 2026-05-31 (step 4 PROPERLY closed — production synthesis + benchmark added)

This section is additive and supersedes the "step 4 COMPLETE" claim where they conflict. Step 4 had found z* but never built the second half the build sequence calls for ("find n* -> RUN the production Monte Carlo at n*"). Treeti caught this gap on resume (reviewer instinct, not confusion): convergence MEASURES the ruler, production USES it — and the use-it arrow had no code. `convergence_with_recommendation` returned z* to nobody; `summarize` was only ever called in smoke tests at a hardcoded n. Now closed.

### The conceptual frame that unlocked it (Treeti's own synthesis, worth preserving)

The engine carried TWO inherited folk numbers, and the project's thesis is challenging BOTH:
- **n = 10,000** (simulations per run) -> replaced by company-specific **z*** (convergence, step 4).
- **batches = 40** (`BATCHES_PER_N`, the measurement apparatus) -> replaced by company-specific **recommended batch count** (the `initial_result` / `refined_result` two-pass in `ConvergencePair`).

Neither a `ConvergenceResult` nor a `ConvergencePair` is a valuation — both are convergence studies. The valuation only exists once you run the engine at z* and `summarize`. That `find z -> use z` arrow was the missing piece.

### Code added to `mc_convergence.py` (no other files structurally changed)

- **`production_valuation(base, convergence, market_price=None, config=None, percentiles=None) -> MCSummary`** — the find-it->use-it arrow. Reads `.z_star` off EITHER a `ConvergenceResult` or a `ConvergencePair` (helper `_z_star_of`), runs `run_monte_carlo` ONCE at n=z*, returns the `MCSummary`. Picks no n itself; never defaults to 10,000. Threads seed/overrides from an optional config (its `n_simulations` is ignored — z* sets n).
- **`benchmark_against_folk(base, convergence, market_price=None, folk_n=10_000, seed=42) -> BenchmarkResult`** + **`format_benchmark`** — the thesis PROOF exhibit. Runs production at z* AND at folk_n under the SAME seed (so only n differs, not RNG luck), reports both summaries side by side plus `compute_ratio` and `mean_gap_pct`. `BenchmarkResult` dataclass holds both `MCSummary`s.
- **Report line** `-> run production MC at : n = z*` now prints in both `format_convergence` and `format_pair` (both branches), so the find-it->use-it link is visible in the text report and never gets lost again.

### Verified (Steady Co, seed 42)

Production at z*=2000: mean 12.731, median 12.402, std 4.596, 5th-95th 5.71-21.01, market $11 sits at the 36.4th percentile (model reads slightly cheap). Benchmark z* vs 10,000, same seed: **20% of the compute, mean moved 0.12%**, percentiles near-identical — the thesis demonstrated, not just asserted. All existing smoke tests still PASS; production runs seed-reproducible. NOTE: a full convergence SWEEP is minutes-scale (millions of valuations), so the new functions were verified against a fixed z*=2000 stand-in; the sweep machinery itself is unchanged from step 4.

### Honest framing for interviews (agreed this session)

The underlying statistics (MC standard error, convergence, sigma/sqrt(n) stopping rules) is well-established in computational fields — NOT invented here. The distinctive contribution is making per-company convergence a FIRST-CLASS step in DCF valuation (where convention just picks 10,000), reporting z*, and later reporting the z*->z** shift that shocks induce. Strong claim, honestly bounded: "nobody in valuation does this per company, and the shock-driven z-shift is a finding standard practice can't even see."

### RESUME AT — step 6 (now genuinely the easy overlay)

Point `production_valuation` and `benchmark_against_folk` at the shocked runner (`run_monte_carlo_with_shocks`) and run convergence with shocks to find z**. Because the production/benchmark layer only reads `.z_star` and takes the engine as given, the shocked path reuses all of it. The z*->z** gap is the headline. Teach-mode rhythm, Steady Co anchoring, show memory diffs before locking, NEVER "No response requested".


---

## SESSION UPDATE — 2026-05-31 (step 6 CLOSED — shocked convergence wired + seed study)

This section supersedes the earlier "z** > z*" expectation wherever they conflict. That expectation turned out to be NOT what the data shows — see below.

### What got wired (mc_convergence.py)

The runner-injection seam from step 4 made step 6 a thin overlay, exactly as predicted. `convergence_analysis` and `convergence_with_recommendation` take a `runner` param (default `run_monte_carlo`); `convergence_with_shocks(base, **kwargs)` is the only seam to `mc_shocks` (lazy import) and just calls `convergence_with_recommendation(base, runner=run_monte_carlo_with_shocks, **kwargs)`. Convergence stays engine-blind: z* and z** come out of an identical code path, the only difference being which engine it drives. No structural change to any other file.

### Convergence is now SEEDED BY DEFAULT (bug fix)

Previously `config=None` ran the sweep fully unseeded, so every call returned a different z*/rec_batches — the recommendation looked like a property of the random draw, not the company. A convergence study is a MEASUREMENT and must be reproducible. Fix: `mc_defaults.CONVERGENCE_DEFAULT_SEED = 42`; when no config is passed, the sweep falls back to it. Pass an explicit `config` with `random_seed=None` for a deliberately fresh draw. The seed is NOT a model parameter and must never be tuned to produce a preferred answer — it only fixes which random stream the measurement uses.

### The seed-sensitivity finding (the real Step-6 result)

Spot-check on the Steady Co FIXTURE, full N_GRID, B=40, four seeds (42/99/123/7):

| seed | CONT z* | CONT batches | SHOCK z** | SHOCK margin | SHOCK batches |
|------|---------|--------------|-----------|--------------|---------------|
| 42  | 2000 | 30 | 2000 | 10.8% | 171  |
| 99  | 2000 | 35 | 2000 | 5.9%  | 575  |
| 123 | 1500 | 29 | 1500 | 3.7%  | 1464 |
| 7   | 1500 | 77 | 1500 | 3.7%  | 1438 |

Three conclusions, deliberately scoped to the fixture and the architecture (NOT universal laws):

1. **z is robust; continuous and shocked move TOGETHER.** Both land in the 1500-2000 band (two adjacent grid rungs) on every seed. The earlier "shocks raise required n -> z** > z*" expectation did NOT hold. The honest statement is neither "z** > z*" nor "z** = z*" but: **for the Steady Co fixture, the shock's effect on required sample size is below the current grid resolution** — if a difference exists, this grid cannot see it.

2. **rec_batches is NOT a robust number — it is seed-sensitive once margins get small.** Continuous swings 29->77 (2.7x); shocked swings 171->1464 (8.6x). This is the structural `1/margin^2` fragility: shocks collapse the decision margin (~27% -> ~4%), and the formula amplifies that violently. **Do NOT elevate 171 (or 575/1464) into a project conclusion — they are fixture- and seed-specific realizations, not architectural truths.** The architectural finding is the SENSITIVITY ITSELF.

3. **What shocks actually do:** they don't change how many simulations you need (z), they change how hard the answer is to grade cleanly (margin -> batches). Batch direction is consistent (shocked > continuous always) but magnitude is not quotable as a single integer.

### CRITICAL framing — Steady Co is a FIXTURE, not the architecture

Every number here is the test dummy. The findings are about what the ARCHITECTURE can do, not about Steady Co's values: the engine can derive a company-specific z, and can test whether shocks move it. A real case-study company (utility, staple, biotech, leveraged turnaround) may well show z** >> z* — we don't know yet, and the framework is built to find out. Wording discipline: write "for the Steady Co fixture, shocks did not move the recommendation beyond grid resolution," NEVER "shocks do not increase required simulations." One is an observation from a fixture; the other is a false general law.

### FUTURE DESIGN NOTE (deferred — NOT a build task, do not open a rabbit hole)

The seed study surfaced a deeper modelling question: margin may be the more FUNDAMENTAL quantity than rec_batches. rec_batches is derived (`1/margin^2`), so it inherits and amplifies margin's noise; under shocks margin stays interpretable (4% = "hard to grade") while rec_batches explodes into noise. A future redesign could lead the output with margin and demote rec_batches to a secondary diagnostic (or report it as a range/order-of-magnitude, not a single integer). RECORDED AS A NOTE ONLY. rec_batches reporting is left UNCHANGED for now. Decision (Treeti, 2026-05-31): lock Step 6 honestly and avoid spawning seed-study / batch-study / margin-study frameworks or a "Step 6.5." Enough has been learned.

### RESUME AT — beyond the engine

The engine architecture is now complete and validated: per-company z, shock overlay, shocked re-convergence, seeded reproducibility. Two things remain to make this PORTFOLIO PIECE #1 done (NOT engine work): (1) run the REAL case-study company (not Steady Co) through the finished pipeline — its own z, its own shock behaviour, which unlike the fixture may show a visible z*->z** shift; (2) the writeup/narrative (two folk numbers challenged, find-z/use-z synthesis, shock overlay, margin-vs-batches insight). Teach-mode rhythm still applies; show memory diffs before locking; NEVER reply "No response requested."

---

## Case-Study Assumptions Log (added 2026-06-09)

Purpose: put every case-study input assumption — and the *reasoning* behind the
most sensitive one, terminal growth — on the record, so each valuation is
defensible and reproducible. The engine is mathematically validated (smoke
tests pass; MSFT reproduces $263.74 to the cent); any difference between our
numbers and external platforms lives entirely in these *input assumptions*, not
in the engine.

### Terminal growth — why we use 2.5%, and why it is defensible

Terminal growth (`terminal_growth`) is the rate the business is assumed to grow
**forever**, after the explicit forecast window ends. It feeds the Gordon
terminal value, which for low-WACC companies is the *majority* of intrinsic
value — so it is the single most sensitive input in the model.

**The hard ceiling (finance theory):** a company cannot grow faster than the
economy in perpetuity, or it eventually becomes larger than the entire economy —
impossible. So terminal growth must be capped at or below **long-run nominal GDP
growth** ≈ long-run inflation (~2%) + long-run real growth (~1.5–2%). The
defensible band is therefore roughly **2–3%**.

**Our choice — 2.5%** sits squarely in that band; it is essentially the
long-run inflation assumption and is the most common professional default. It is
the *conservative-but-standard* choice, not a lowball.

**Why external platforms read higher.** AlphaSpread ($88.38) and Yahoo
($88–96) for KO implicitly use ~3.5–4% terminal growth. 4% sits at the
*aggressive* edge of the band — it assumes Coca-Cola out-grows the U.S. economy
forever (a real bet on enduring global pricing power, not a neutral default).
Neither is "wrong"; ours is the more conservative and arguably the more
defensible. Confirmed numerically: changing **only** KO's terminal growth
2.5% → 4.0% (WACC and all else unchanged) moves intrinsic value $57.83 → $83.71,
landing in the external band.

### Reconciliation to external estimates (what drives each gap)

| Company | Our central | External DCF range | Dominant lever behind the gap |
|---|---|---|---|
| KO  | $57.83 | $80–96 | **Terminal growth** (2.5% vs ~4%); low WACC makes terminal value dominate |
| AMZN | $96.52 | $199–211 (earnings-DCF) | **Capex drag + higher WACC + FCFF-vs-earnings methodology** |
| MSFT | $263.74 | n/a (validation fixture) | — (reproduces known-good value exactly) |

Key methodology note for AMZN: external "DCF (earnings/EPS)" models value
*earnings*, which are currently far above Amazon's free cash flow because of the
AI/datacenter capex spike. Our unlevered-FCFF model deliberately subtracts that
capex, so it reads lower until the capex wave passes. Different question, not a
worse model.

### KO fixture assumptions (FY2025 actuals → forward view)

Built from reported FY2025 actuals: revenue $47.9B, net income $13.1B, capex
$2.1B, ~4.30B shares, long-term debt ~$42B (net debt ~$31B after cash/
investments), beta ~0.55. Market price $79.86 (2026-06-03). Fixture:
`ko_fixture.json`.

| Input | Value | Rationale |
|---|---|---|
| starting_revenue | 47,900 ($M) | FY2025 reported net revenue |
| net_debt | 31,000 ($M) | ~$42B LT debt + current portion − cash & ST investments |
| shares_outstanding | 4,300 (M) | Reported diluted share count |
| forecast_years | 7 | Standard explicit window used across case studies |
| revenue_growth | 5.0% → 3.5% | Mid-single-digit, fading toward terminal; conservative vs KO's 4–6% organic guide |
| operating_margin | 29.5% → 31.0% | Modest expansion off KO's high-20s/low-30s underlying operating margin |
| capex_pct_revenue | ~4.4–4.5% | Capital-light; $2.1B / $47.9B ≈ 4.4% |
| da_pct_revenue | 2.4% | Approx. reported D&A / revenue |
| nwc_pct_revenue | 0.0% | KO runs efficient/near-neutral working capital |
| tax_rate | 19% | Approx. effective rate |
| terminal_growth | 2.5% | Conservative, in the 2–3% defensible band (see above) |
| risk_free_rate | 4.3% | Consistent with the other case studies |
| equity_risk_premium | 5.5% | Standard long-run ERP |
| beta | 0.55 | KO is a low-beta defensive staple |
| cost_of_debt | 5.0% | Investment-grade issuer |
| debt_to_total_capital | 11% | Debt ÷ (debt + market equity ≈ $343B) |

Result (engine as-is, no logic modified): WACC **6.97%**, central DCF
**$57.83**. Continuous MC (z*=3,000): median $56.14, 0% negative. Shocked MC
(z**=2,000): median $52.94, 0% negative. Market $79.86 ≈ 95th percentile of the
intrinsic-value distribution → engine reads KO as fully-to-richly valued on
conservative cash-flow assumptions (market pays a quality/dividend premium).

**Discipline reminder:** every figure here is an *assumption-driven* output. The
engine produces a distribution and compares it to market price precisely because
no single intrinsic-value number is "the truth" — it is only as good as these
inputs. A platform quoting "$88.38" is quoting *its* assumptions, not a fact.
