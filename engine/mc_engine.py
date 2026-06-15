"""
Monte Carlo Engine — perturbation layer
=======================================

This module wraps the deterministic DCF (`dcf.run_dcf`) in a perturbation
loop. Step 3 of the build sequence. The first piece, written here, is
`sample_inputs`: take the central-case DCFInputs and return ONE perturbed
copy. Run it thousands of times (the job of `run_monte_carlo`, next beat)
and the collected per-share values form the distribution that is the whole
point of the engine.

Design recap (all locked in the step-3 design phase, see HANDOFF.md):

  - Eight dials wiggle. Five are trajectories (lists): revenue_growth,
    operating_margin, capex_pct_revenue, da_pct_revenue, nwc_pct_revenue.
    Two are scalar normals: beta, equity_risk_premium. One is scalar
    triangular: terminal_growth.

  - Hybrid sampling. Each list dial gets a PERSISTENT trajectory
    perturbation (one draw, rescales the whole line) PLUS small per-year
    noise (a fresh independent draw each forecast year). Scalar normals get
    the trajectory draw only. terminal_growth is drawn from a triangular
    band on its own.

  - Correlation. The seven normal dials' trajectory perturbations are drawn
    together so they move in step per the rules in mc_defaults.CORRELATIONS
    (revenue x margin +0.5, capex x revenue +0.4, beta x ERP +0.1). The
    mechanic is a Cholesky factorisation of the 7x7 correlation matrix.
    Per-year noise stays INDEPENDENT — correlation lives at the trajectory
    layer only. terminal_growth (triangular) sits outside the correlated
    block entirely.

Terminology note: what this module calls a "trajectory perturbation" is a
persistent per-simulation rescaling of a whole dial. It is NOT regime
modelling — true macro regimes (Expansion / Recession / Stress states with
state-dependent distributions) are a separate future layer, and the word
"regime" is reserved for that. See HANDOFF.md.
"""

from dataclasses import dataclass, field, replace
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from dcf import DCFInputs, run_dcf
from mc_config import MCConfig
import mc_defaults


# ============================================================
#  CORRELATION SCAFFOLDING
# ============================================================
#  The seven normal dials' trajectory perturbations are drawn
#  as one correlated vector. Two helpers build that machinery:
#  one assembles the correlation matrix from the pairwise rules,
#  the other turns a vector of independent standard-normal draws
#  into a correlated one via the Cholesky factor.
# ============================================================


def _build_correlation_matrix(
    dials: List[str],
    correlations: Dict[Tuple[str, str], float],
) -> np.ndarray:
    """Assemble the NxN correlation matrix for the given normal dials.

    Starts from the identity (every dial perfectly correlated with itself,
    1.0 on the diagonal; uncorrelated with everything else, 0 off-diagonal)
    and then writes in each pairwise correlation from `correlations`.

    The matrix is symmetric: corr(a, b) == corr(b, a), so each rule fills in
    BOTH the (i, j) and (j, i) cells. Keys in `correlations` are sorted
    alphabetically (the mc_defaults convention), so we sort each (i, j)
    dial-name pair the same way before looking it up.

    Example for Steady Co's seven dials, the only non-zero off-diagonal
    entries are the three locked pairs:

        revenue_growth x operating_margin   = 0.5
        capex_pct_revenue x revenue_growth  = 0.4
        beta x equity_risk_premium          = 0.1

    everything else stays 0. Returns an NxN numpy array.
    """
    n = len(dials)
    matrix = np.eye(n)  # identity: 1.0 diagonal, 0 elsewhere

    # Walk every unique pair (i < j) of dials and, if a correlation rule
    # exists for that pair, write it into both symmetric cells.
    for i in range(n):
        for j in range(i + 1, n):
            key = tuple(sorted((dials[i], dials[j])))  # alphabetical, matches mc_defaults
            rho = correlations.get(key)
            if rho is not None:
                matrix[i, j] = rho
                matrix[j, i] = rho

    return matrix


def _correlated_normal_draw(
    dials: List[str],
    correlations: Dict[Tuple[str, str], float],
    rng: np.random.Generator,
) -> Dict[str, float]:
    """Draw one correlated standard-normal value per normal dial.

    The recipe (this is the Cholesky mechanic from the teach-mode beat):

        1. Build the correlation matrix C (above).
        2. Factor it: C = L @ L.T, where L is lower-triangular.
           numpy.linalg.cholesky does this.
        3. Draw z = N independent standard normals (mean 0, sd 1).
        4. w = L @ z. The vector w now has the target correlation
           structure baked in, while each component still has sd 1.

    Why it works, in one line: multiplying independent unit-variance noise
    by L mixes the components in exactly the proportions that reproduce C
    as the covariance of the result. Revenue's draw bleeds into margin's
    (weighted by 0.5), and so on.

    PSD caveat: cholesky requires the correlation matrix to be positive
    semi-definite. The three-pair v1 spec is comfortably PSD. A future
    change (more pairs, stronger coefficients) could break that; comprehensive
    validation is deferred to step 7, but np.linalg.cholesky will raise a
    LinAlgError if it ever happens, so it won't fail silently.

    Returns a dict: dial name -> one standard-normal draw (sd 1, not yet
    scaled by any width). The caller scales each by the trajectory width.
    """
    matrix = _build_correlation_matrix(dials, correlations)
    L = np.linalg.cholesky(matrix)        # lower-triangular factor
    z = rng.standard_normal(len(dials))   # independent unit normals
    w = L @ z                             # correlated unit normals

    # Pair each correlated draw back up with its dial name.
    return {dial: w[i] for i, dial in enumerate(dials)}


# ============================================================
#  THE SAMPLER
# ============================================================
#  One perturbed DCFInputs from the central case. The heart of
#  step 3. run_monte_carlo (next beat) calls this n times.
# ============================================================


def sample_inputs(
    base: DCFInputs,
    config: MCConfig,
    rng: np.random.Generator,
) -> DCFInputs:
    """Return ONE perturbed DCFInputs drawn from the central case.

    Applies the locked perturbation design: a persistent, correlated
    trajectory perturbation on the seven normal dials; small independent
    per-year noise on the five list dials; a triangular draw on
    terminal_growth; and the eight fixed fields left untouched.

    The random generator `rng` is passed in (not created here) so that
    run_monte_carlo can own a single seeded generator and draw every
    simulation from the same reproducible stream. Passing it in is what
    makes `MCConfig.random_seed` actually reproducible end-to-end — if each
    call made its own generator, the seed couldn't thread through.

    Perturbations are MULTIPLICATIVE: each value is scaled by (1 + draw),
    so a +12% trajectory draw means a +12% RELATIVE lift whether the dial
    sits at 4% (a growth rate) or 15% (a margin). This keeps the kick
    proportional across dials of very different magnitudes.

    Returns a new DCFInputs; `base` is never mutated.
    """
    # ---- 0. Resolve calibration: defaults, unless this run overrides ----
    # MCConfig stays small; the design knobs live in mc_defaults. An override
    # dict (for calibration sweeps) transparently takes precedence per key.
    width_overrides = config.width_overrides or {}
    traj_width = width_overrides.get("trajectory", mc_defaults.TRAJECTORY_WIDTH)
    per_year_width = width_overrides.get("per_year_noise", mc_defaults.PER_YEAR_NOISE_WIDTH)

    # Merge correlation overrides on top of the locked defaults.
    correlations = dict(mc_defaults.CORRELATIONS)
    if config.correlation_overrides:
        correlations.update(config.correlation_overrides)

    # ---- 1. One correlated trajectory draw per normal dial ----
    # NORMAL_DIALS is the canonical ordering (five list dials, then beta, ERP).
    # raw_draw[dial] has sd 1; multiply by traj_width to get the actual
    # proportional lift (~+/-12% at one standard deviation).
    raw_draw = _correlated_normal_draw(mc_defaults.NORMAL_DIALS, correlations, rng)
    traj_lift = {dial: raw_draw[dial] * traj_width for dial in mc_defaults.NORMAL_DIALS}

    # ---- 2a. List dials: persistent lift + independent per-year noise ----
    # Each of the five trajectories is rescaled by its (constant across years)
    # trajectory lift, then each year additionally jittered by a fresh draw.
    # The lift captures persistence ("this simulation walks a high-growth
    # trajectory"); the jitter captures year-to-year wobble within it.
    list_dials = [
        "revenue_growth",
        "operating_margin",
        "capex_pct_revenue",
        "da_pct_revenue",
        "nwc_pct_revenue",
    ]
    perturbed_lists: Dict[str, List[float]] = {}
    for dial in list_dials:
        lift = traj_lift[dial]
        central_trajectory = getattr(base, dial)
        new_trajectory: List[float] = []
        for yearly_value in central_trajectory:
            # Per-year noise: fresh, independent, NOT correlated. Each year
            # jitters off its own central value (not off last year's perturbed
            # value), so the noise doesn't compound down the trajectory.
            jitter = rng.standard_normal() * per_year_width
            new_trajectory.append(yearly_value * (1 + lift) * (1 + jitter))
        perturbed_lists[dial] = new_trajectory

    # ---- 2b. Scalar normal dials: trajectory lift only ----
    # No trajectory to rescale, no per-year loop — the trajectory lift IS the
    # whole perturbation. Still correlated, because beta and ERP came out of
    # the same Cholesky-mixed vector as the list dials (beta x ERP = 0.1).
    perturbed_beta = base.beta * (1 + traj_lift["beta"])
    perturbed_erp = base.equity_risk_premium * (1 + traj_lift["equity_risk_premium"])

    # ---- 2c. terminal_growth: triangular, independent ----
    # Outside the correlated normal block. Drawn from the defensible band
    # (low, mode, high) = (1.5%, central case, 3.0%). The mode is the central
    # input; the bounds come from mc_defaults. This is an absolute draw, not a
    # multiplicative scaling — terminal_growth lives in a fixed economic band,
    # so we sample the band directly rather than lifting the central value.
    #
    # Off-switch convention: terminal_growth's dispersion comes from the band,
    # not from a width knob, so a zero trajectory width wouldn't otherwise
    # freeze it. We treat traj_width == 0 as "perturbation off everywhere" and
    # hold terminal_growth at its central (mode) value. That gives the engine a
    # clean deterministic mode — zero widths => every simulation reproduces
    # run_dcf(base) exactly — which is what the zero-perturbation smoke test
    # checks.
    if traj_width == 0:
        perturbed_tg = base.terminal_growth
    else:
        perturbed_tg = rng.triangular(
            left=mc_defaults.TERMINAL_GROWTH_LOW,
            mode=base.terminal_growth,
            right=mc_defaults.TERMINAL_GROWTH_HIGH,
        )

    # ---- 3. Build the perturbed copy ----
    # dataclasses.replace makes a new DCFInputs from `base`, overriding only
    # the perturbed fields. Everything not named here — starting_revenue,
    # net_debt, shares_outstanding, forecast_years, tax_rate,
    # debt_to_total_capital, risk_free_rate, cost_of_debt — carries over
    # unchanged. Those are the eight fixed fields, held at central case.
    return replace(
        base,
        revenue_growth=perturbed_lists["revenue_growth"],
        operating_margin=perturbed_lists["operating_margin"],
        capex_pct_revenue=perturbed_lists["capex_pct_revenue"],
        da_pct_revenue=perturbed_lists["da_pct_revenue"],
        nwc_pct_revenue=perturbed_lists["nwc_pct_revenue"],
        beta=perturbed_beta,
        equity_risk_premium=perturbed_erp,
        terminal_growth=perturbed_tg,
    )


# ============================================================
#  THE RUNNER
# ============================================================
#  The n-simulation loop. Conceptually thin: own one seeded
#  random generator, perturb-and-value n times, collect the
#  per-share results into a list. That list IS the distribution
#  — all downstream analysis (percentiles, histogram, comparison
#  to market price) reads from it.
# ============================================================


def run_monte_carlo(base: DCFInputs, config: MCConfig) -> List[float]:
    """Run `config.n_simulations` perturbed DCF valuations.

    Each simulation draws one perturbed DCFInputs from the central case
    (`sample_inputs`) and runs it through the deterministic engine
    (`run_dcf`), producing one per-share intrinsic value. The returned list
    of those values is the Monte Carlo distribution — the engine's actual
    output, replacing the single point estimate a plain DCF would give.

    Reproducibility lives here. This function creates ONE numpy generator
    (seeded from `config.random_seed` when provided) and threads it through
    every `sample_inputs` call, so all n draws come from a single
    deterministic stream. Same seed + same inputs => identical distribution,
    every time. When `random_seed` is None the generator is seeded from the
    OS entropy pool, so each production run gets a fresh draw.

    Deliberately NOT in this function: any choice of n. `n_simulations` is a
    config field precisely because step 4 (convergence analysis) sweeps it —
    running this engine at increasing n and watching the distribution settle
    to find the per-company elbow. So the runner takes n as given and never
    hard-codes a default like the folk-wisdom 10,000.

    Returns a list of floats, length `config.n_simulations`, each a per-share
    intrinsic value. Order carries no meaning — the values are exchangeable
    draws from the same distribution.
    """
    # One generator for the whole run. None seed -> nondeterministic (fresh
    # entropy); an int seed -> fully reproducible stream.
    rng = np.random.default_rng(config.random_seed)

    # Perturb-and-value, n times. sample_inputs advances the generator's
    # state on every call, so each iteration draws a genuinely new sample
    # from the same reproducible stream.
    return [
        run_dcf(sample_inputs(base, config, rng))
        for _ in range(config.n_simulations)
    ]


# ============================================================
#  DIAGNOSTICS
# ============================================================
#  Turn the raw list of per-share values into the things an
#  analyst actually reports: a center, a spread, the percentile
#  band, and — the headline signal — where the market price
#  sits inside the simulated distribution. Plus a text histogram
#  so the shape (skew, fat tails) is visible at a glance.
# ============================================================


# The percentiles reported by default. The 5th/95th frame the "90% of the
# mass lands between here and here" band; 25/50/75 give the interquartile
# shape; 50 is the median. Override per call if you want a different cut.
DEFAULT_PERCENTILES: Tuple[int, ...] = (5, 10, 25, 50, 75, 90, 95)


@dataclass
class MCSummary:
    """A compact summary of one Monte Carlo distribution.

    Holds the headline statistics over the list of per-share values, plus —
    when a market price is supplied — where that price falls inside the
    simulated distribution. Everything here is read-only description; no
    perturbation or valuation logic lives in this object.

    Fields:
        n:              number of simulations behind the summary.
        mean, median:   the two centers. mean above median signals right-skew.
        std:            standard deviation — the raw spread.
        minimum, maximum: the realised extremes across all draws.
        percentiles:    {percentile -> per-share value}, e.g. {5: 5.66, ...}.
        market_price:   the comparison benchmark, if provided (else None).
        market_percentile:
            the share of simulations valued BELOW market_price, as a percent.
            "Market sits at the 18th percentile" means 18% of our simulated
            valuations came in below today's price — i.e. the model thinks the
            stock is cheap relative to most of the distribution. None when no
            market price was supplied.
    """

    n: int
    mean: float
    median: float
    std: float
    minimum: float
    maximum: float
    percentiles: Dict[int, float]
    market_price: Optional[float] = None
    market_percentile: Optional[float] = None


def summarize(
    results: Sequence[float],
    market_price: Optional[float] = None,
    percentiles: Sequence[int] = DEFAULT_PERCENTILES,
) -> MCSummary:
    """Compute summary statistics over a Monte Carlo result list.

    `results` is the list returned by run_monte_carlo — one per-share value
    per simulation. Optionally pass `market_price` to locate today's quoted
    price inside the distribution (the actionable comparison from the project
    thesis: price vs the whole distribution, not vs a single point estimate).

    Returns an MCSummary. Pure description — does not run the engine.
    """
    arr = np.asarray(results, dtype=float)

    # {percentile -> value}. np.percentile interpolates between draws, which
    # is fine for a continuous valuation distribution.
    pct_map = {p: float(np.percentile(arr, p)) for p in percentiles}

    market_pctile: Optional[float] = None
    if market_price is not None:
        # Share of simulations valued strictly below the market price, as a
        # percent. Low percentile => model values the firm above market on
        # most paths (looks cheap); high percentile => looks rich.
        market_pctile = float((arr < market_price).mean() * 100.0)

    return MCSummary(
        n=arr.size,
        mean=float(arr.mean()),
        median=float(np.median(arr)),
        std=float(arr.std()),
        minimum=float(arr.min()),
        maximum=float(arr.max()),
        percentiles=pct_map,
        market_price=market_price,
        market_percentile=market_pctile,
    )


def text_histogram(
    results: Sequence[float],
    bins: int = 20,
    width: int = 50,
) -> str:
    """Render the distribution shape as a plain-text bar histogram.

    Buckets the per-share values into `bins` equal-width intervals and draws
    a horizontal bar per bucket, the longest bar `width` characters wide.
    No plotting library — readable straight in a terminal or a code review,
    which is the point: a hiring manager skimming the file sees the shape
    (the right-skew, the fat tail) without running anything.

    Returns a multi-line string; the caller prints it.
    """
    arr = np.asarray(results, dtype=float)
    counts, edges = np.histogram(arr, bins=bins)
    busiest = counts.max() if counts.max() > 0 else 1  # avoid div-by-zero

    lines: List[str] = []
    for i, count in enumerate(counts):
        # Bucket label is the left edge of the interval.
        label = f"{edges[i]:8.2f}"
        bar = "#" * int(round(count / busiest * width))
        lines.append(f"{label} | {bar} {count}")
    return "\n".join(lines)


def format_summary(summary: MCSummary) -> str:
    """Render an MCSummary as a readable multi-line block.

    Pure formatting — turns the numbers into the lines you'd paste into a
    report. The caller prints the returned string.
    """
    lines = [
        f"Monte Carlo summary  (n = {summary.n:,})",
        f"  mean   : {summary.mean:8.3f}",
        f"  median : {summary.median:8.3f}",
        f"  std    : {summary.std:8.3f}",
        f"  range  : {summary.minimum:8.3f}  to  {summary.maximum:8.3f}",
        "  percentiles:",
    ]
    for p in sorted(summary.percentiles):
        lines.append(f"    {p:3d}th : {summary.percentiles[p]:8.3f}")
    if summary.market_price is not None:
        lines.append(f"  market price : {summary.market_price:8.3f}")
        lines.append(
            f"  -> sits at the {summary.market_percentile:.1f}th percentile "
            f"of the simulated distribution"
        )
    return "\n".join(lines)
