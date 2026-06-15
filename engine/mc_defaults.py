"""
Monte Carlo Defaults — initial calibration values
==================================================

The widths, correlations, and distribution-shape assignments that drive
perturbation, all sitting in one obvious place so they can be tuned
without surgery elsewhere in the codebase.

These values are INITIAL CALIBRATION — defensible v1 starting points
locked during the step-3 design phase, NOT permanent architectural
commitments. After the first convergence runs they may shift. To
override per-run without editing this file, use the `width_overrides`
and `correlation_overrides` hooks in MCConfig.

The split (defaults here, MCConfig small): users running the engine in
the common case should not have to re-specify decisions already made
during design. Tuning is for calibration sweeps, not for every call.
"""

from typing import Dict, List, Tuple


# ============================================================
#  PERTURBATION WIDTHS
# ============================================================
#  How big the random kicks are. The hybrid sampling structure
#  (locked in step-3 design) applies BOTH a persistent
#  trajectory-level perturbation AND a smaller per-year noise
#  to every list-valued dial. Scalar dials (terminal_growth,
#  beta, ERP) get a single draw per simulation, using the
#  trajectory width as their dispersion parameter.
# ============================================================


# Trajectory width — the persistent per-simulation rescaling on a dial.
# One draw per simulation per dial; rescales the WHOLE trajectory by
# roughly ±12% (one standard deviation, under a normal distribution).
# Captures persistent trajectory-level uncertainty: "this simulation
# walks a high-growth trajectory" or "this simulation walks a margin-
# compressed trajectory". NOT regime modelling — true regimes
# (Expansion / Normal / Recession / Stress states with state-dependent
# distributions) are a distinct future layer; the vocabulary is kept
# separate on purpose.
TRAJECTORY_WIDTH: float = 0.12

# Per-year noise width — small jitter layered on top of the trajectory
# perturbation, drawn independently for each forecast year. Captures
# realistic year-to-year wobble around a persistent regime (the world
# isn't a smooth ride even within a single macro story).
PER_YEAR_NOISE_WIDTH: float = 0.04


# ============================================================
#  CORRELATIONS
# ============================================================
#  Three pairs locked in the step-3 design phase. Correlations
#  of the WIGGLE (the per-simulation perturbation), NOT of the
#  underlying levels. Applied at the trajectory-perturbation
#  layer only; per-year noise stays independent.
#
#  Key tuples are sorted alphabetically so lookups are
#  unambiguous regardless of which order the caller writes
#  the pair in.
# ============================================================


CORRELATIONS: Dict[Tuple[str, str], float] = {
    ("operating_margin", "revenue_growth"): 0.5,
    # Operational leverage — when revenue surges, fixed costs spread
    # over a larger base, lifting margin. They wiggle in the same
    # direction more often than not. Strong-ish positive correlation.

    ("capex_pct_revenue", "revenue_growth"): 0.4,
    # Growth needs investment — high-growth years tend to coincide
    # with elevated capex intensity. Real but weaker than the
    # revenue/margin link because some growth comes from existing
    # capacity utilisation, not new capex.

    ("beta", "equity_risk_premium"): 0.1,
    # Weak shared market-stress driver. Beta is firm-specific and
    # ERP is market-wide, so the dependence is small but non-zero
    # (when the market gets jittery, both tend to drift up).
    # Treeti correctly pushed back on the initially-proposed 0.3.
}

# Flagged for Phase 2 (NOT in v1):
#   - ("capex_pct_revenue", "da_pct_revenue")  — capex feeds D&A with a lag
#   - ("nwc_pct_revenue", "revenue_growth")    — working capital scales w/ sales


# ============================================================
#  DISTRIBUTION SHAPES
# ============================================================
#  Locked in the step-3 design phase. Seven dials use normal
#  (bell curve around the central case). Terminal growth uses
#  triangular because it sits in a narrow defensible band
#  (~1.5-3%) with no real "center plus noise" intuition.
#
#  Skewness was REJECTED as its own modelling layer — the
#  asymmetric phenomena (margin collapse, capex blowouts,
#  recession sharpness) are event-driven and belong to the
#  step-5 micro shock overlay. Two clean layers (Gaussian
#  noise + discrete shocks), not three.
# ============================================================


NORMAL_DIALS: List[str] = [
    "revenue_growth",
    "operating_margin",
    "capex_pct_revenue",
    "da_pct_revenue",
    "nwc_pct_revenue",
    "beta",
    "equity_risk_premium",
]

TRIANGULAR_DIALS: List[str] = [
    "terminal_growth",
]


# ============================================================
#  TRIANGULAR BOUNDS — for terminal_growth specifically
# ============================================================
#  The triangular distribution needs (low, mode, high). Mode
#  comes from the central case in DCFInputs; low and high are
#  set here as the defensible band.
# ============================================================


TERMINAL_GROWTH_LOW: float = 0.015   # 1.5% — roughly long-run inflation floor
TERMINAL_GROWTH_HIGH: float = 0.030  # 3.0% — roughly long-run GDP ceiling


# ============================================================
#  FIELDS HELD FIXED (NOT perturbed)
# ============================================================
#  Reference list for documentation purposes. These DCFInputs
#  fields are held at their central-case values across every
#  simulation. The runner shouldn't touch them.
#
#    starting_revenue        — observable today, not a forecast
#    net_debt                — observable today
#    shares_outstanding      — observable today
#    forecast_years          — structural choice
#    tax_rate                — held flat by design (block 2)
#    debt_to_total_capital   — capital structure assumption
#    risk_free_rate          — roughly observable today (v1)
#    cost_of_debt            — roughly observable today (v1)
#
#  The risk-free rate and cost of debt could be promoted to
#  perturbed dials in a future revision.
# ============================================================


# ============================================================
#  CONVERGENCE ANALYSIS — step 4
# ============================================================
#  The knobs for finding a company's empirical sample size z*
#  instead of defaulting to the folk-wisdom 10,000. The headline
#  feature of the project. All three live here so they tune in
#  one obvious place, same as the perturbation widths above.
# ============================================================


# The candidate sample sizes we test. Convergence is measured AT each of
# these n values. The grid is explicit (not auto-generated) on purpose: the
# geometric "elbow" of the decay curve is sensitive to the range of n you
# look at, so pinning the grid makes the elbow — and therefore z* —
# reproducible run-to-run. Spaced denser at the low end (where the curve
# bends hardest) and sparser up top (where it has flattened out).
N_GRID: List[int] = [100, 250, 500, 1000, 1500, 2000, 3000, 5000, 7500, 10000]

# How many times we re-run the WHOLE engine at each candidate n. Each re-run
# produces one run-mean; the scatter (standard deviation) of these run-means
# at a given n is the convergence signal. 40 is enough to estimate that
# scatter stably without making the sweep crawl. More batches = a smoother
# scatter estimate but a linearly slower sweep.
BATCHES_PER_N: int = 40

# Default seed for a convergence sweep when the caller passes no config. A
# convergence study is a MEASUREMENT and must be reproducible: an unseeded sweep
# returns a different z*/rec_batches on every run, which makes the recommendation
# look like a property of the random draw rather than the company. Seed-sweeps
# on the Steady Co fixture (2026-05-31) showed z* clusters tightly (1500-2000
# band) across seeds, while rec_batches is seed-sensitive once margins are small
# (esp. under shocks). A fixed default makes the headline number reproducible;
# pass config=MCConfig(..., random_seed=None) for an intentionally fresh draw, or
# vary the seed deliberately to spot-check robustness. The seed is NOT a model
# parameter and must never be tuned to produce a preferred answer.
CONVERGENCE_DEFAULT_SEED: int = 42

# Decision margin for the batch-count recommendation. The apparatus grades
# whether BATCHES_PER_N was "enough" for THIS company by asking whether the
# chosen z* point clears the precision bar by this many of its own error bands
# (1/sqrt(2(B-1)) relative). 2 = a "2-sigma-clean" call. This is how 40 stops
# being folklore: it gets validated per company rather than assumed universal.
CONVERGENCE_DECISION_SIGMAS: float = 2.0

# Compute cap on the single refinement pass. The recommended batch count can,
# for an awkward company, come back large — and a re-run scales linearly with
# it, so an uncapped refinement could grind for many minutes. The refinement
# batch count is clamped to this ceiling; if the recommendation exceeds it, the
# engine refines at the cap and reports the residual recommendation honestly
# rather than silently running forever. A documented operational guard, not an
# architectural choice — the endpoint is still ONE refinement pass.
MAX_REFINEMENT_BATCHES: int = 250

# Rule 2 — the precision bar. Convergence requires the scatter of run-means
# to fall below this FRACTION of the valuation (i.e. the relative standard
# error of the mean). 1% means "the answer is pinned to within 1% of its own
# value". Expressed as a ratio (not a dollar amount) deliberately, so the
# same bar travels across companies of very different share prices — a $12
# stock and a $500 stock are both held to 1% of themselves.
CONVERGENCE_PRECISION_PCT: float = 0.01


# ============================================================
#  MICRO-SHOCK OVERLAY — step 5
# ============================================================
#  Layer two of the deliberately-two-layer design: discrete,
#  state-conditional events layered on top of the continuous
#  perturbation. Where step-3 perturbation is the "weather"
#  (normal variation), these shocks are the "earthquakes"
#  (discrete events larger than the weather can produce). They
#  produce cascades and the fat left tail.
#
#  EVERYTHING in this section is a V1 PLACEHOLDER. The base
#  hazards are calibrated to a defensible aggregate (Steady Co
#  stays ~75% shock-free over its horizon) rather than guessed
#  per cell; the damage bands have pinned UNITS but placeholder
#  magnitudes. Both are meant to be re-calibrated against the
#  first shocked histogram. See design-decisions-mc-step5.
# ============================================================


# The five shock channels — the universal transmission routes by which
# exogenous damage enters the valuation. NOT a list of real-world events;
# real events (customer loss, recall, downgrade, lawsuit, disruption) are
# manifestations that map onto these. Selection rule: each channel is
# EXOGENOUS, FIRST-ORDER, and ECONOMICALLY DISTINCT.
SHOCK_CHANNELS: List[str] = [
    "revenue",     # -> persistent haircut on the revenue LEVEL
    "margin",      # -> persistent multiplicative compression of operating margin
    "funding",     # -> relative increase in cost_of_debt (hits WACC, the denominator)
    "strategic",   # -> relative reduction in terminal_growth (permanent franchise impairment)
    "cash",        # -> one-off cash outflow, a % of that year's revenue (new transmission point)
]

# Base hazards — the per-channel, per-YEAR probability a shock fires when the
# company is healthy (stress = 0). Equal across channels in V1 (the ignorance
# prior: we don't yet claim to know which channel is more likely). Calibrated
# so a 5-year, 5-channel Steady Co path stays shock-free ~75% of the time:
#   P(no shock) = (1 - 0.0115)^(5 channels x 5 years) ~= 0.747.
# This 75% is Steady Co's illustrative setting, NOT a universal constant — in
# the general engine hazards are a per-company input. Deriving them from
# company characteristics (leverage, concentration, industry) is a SEPARATE
# FUTURE PROJECT; the engine only CONSUMES them.
SHOCK_BASE_HAZARD: float = 0.0115
BASE_HAZARDS: Dict[str, float] = {ch: SHOCK_BASE_HAZARD for ch in SHOCK_CHANNELS}

# Stress sensitivity — how hard accumulated fragility raises future shock odds.
# adjusted_hazard = base_hazard * (1 + STRESS_SENSITIVITY * stress), clamped to
# 1.0. Linear (the "I don't know the curvature" choice); a steeper curve only
# ever accelerates cascades, so we start calm and steepen only if the histogram
# shows spirals are too rare. With sensitivity 1.0: stress 0.5 -> x1.5 odds,
# stress 1.0 -> x2, stress 2.0 -> x3.
STRESS_SENSITIVITY: float = 1.0

# Damage bands — (floor, ceiling) per channel. A shock's uniform-[0,1] severity
# draw interpolates linearly between floor and ceiling to set the damage
# magnitude. The FLOOR sits just past what step-3 perturbation (~12% trajectory
# width) can produce, so every shock is genuinely bigger than "weather". UNITS
# are locked and DIFFER per channel (see design-decisions-mc-step5); the
# magnitudes are placeholders:
#   revenue   -> fraction the revenue LEVEL drops, persistently (customer gone)
#   margin    -> fraction operating margin is multiplied down by, persistently
#   funding   -> fraction cost_of_debt is increased by (relative)
#   strategic -> fraction terminal_growth is reduced by (relative)
#   cash      -> fraction of that year's revenue removed as a one-off outflow
DAMAGE_BANDS: Dict[str, Tuple[float, float]] = {
    "revenue":   (0.15, 0.50),
    "margin":    (0.15, 0.50),
    "funding":   (0.20, 0.80),
    "strategic": (0.20, 0.60),
    "cash":      (0.05, 0.25),
}

# Fragility weights — how much each channel's severity contributes to the stress
# tally. EQUAL in V1 (stress += severity for every channel), justified as the
# ignorance prior. The principle for future differentiation: a channel's
# contribution should track its threat to SURVIVAL, not value lost (funding/cash
# threaten solvency most). Trip-wire: if funding/cash cascades look implausibly
# rare in the first histogram, that's the data-grounded reason to differentiate.
FRAGILITY_WEIGHTS: Dict[str, float] = {ch: 1.0 for ch in SHOCK_CHANNELS}
