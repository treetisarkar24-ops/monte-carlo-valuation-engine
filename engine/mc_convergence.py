"""
Monte Carlo Convergence Analysis — step 4 (the headline feature)
================================================================

Standard practice runs a Monte Carlo DCF at n = 10,000 simulations. That
number is folk wisdom inherited from 1990s computational finance — it is NOT
derived from any particular company's variance profile. This module replaces
the folk number with a per-company EMPIRICAL sample size, z*, found by
measuring how the engine's answer settles as n grows.

The diagnostic — peak vs elbow, hold the distinction
----------------------------------------------------
One Monte Carlo run returns a bell-shaped distribution of per-share values;
its PEAK is the company's most-likely worth (that is the engine's answer, and
it is NOT what this module computes). Convergence is a DIFFERENT object: at
each candidate n we run the whole engine many times, and ask how much those
runs' MEANS disagree with each other. That disagreement — the "scatter of
run-means" — shrinks as n grows. Plot scatter against n and you get a decay
curve that falls toward zero. The bell has a peak; the decay curve has an
ELBOW. We hunt the elbow.

Why the scatter shrinks, exactly (CLT)
--------------------------------------
The Central Limit Theorem says the spread of an average of n draws is the
per-simulation spread sigma divided by sqrt(n):  SE(n) = sigma / sqrt(n).
Note the SQUARE ROOT — to halve the wobble you need 4x the simulations. That
square-root is the whole reason convergence has diminishing returns, and the
whole reason a per-company z* beats a fixed 10,000. This module estimates
sigma from one large run and reports it, so the empirical scatter can be
checked against the sigma/sqrt(n) law — the engine verifying its own
convergence behaviour against first-principles statistics.

Defining z* — a layered, conservative rule
-------------------------------------------
A sigma/sqrt(n) curve is smooth: it has no sharp corner, so "the elbow" must
be DEFINED, not eyeballed. We layer two criteria and take the more
conservative (larger) one:

  Rule 2 (z_pct)   — precision bar. Smallest grid n whose scatter falls below
                     CONVERGENCE_PRECISION_PCT (=1%) of the valuation. This is
                     a RATIO, so it travels across companies of different
                     share prices — the scale-free anchor.

  Rule 3 (z_elbow) — the geometric bend (kneedle). The point of the curve
                     furthest below the straight line joining its endpoints —
                     i.e. where buying more steadiness suddenly costs a lot
                     more n. Most faithful to the "where do extra simulations
                     stop paying off" thesis, but sensitive to the n-range,
                     which is why N_GRID is fixed in mc_defaults.

  z* = max(z_pct, z_elbow)

Taking the max means a wobbly criterion can only ever make us MORE
conservative, never less — a defensible story.

Two passes across the build: this step finds z** for the continuous-only
engine. After the step-5 micro-shock overlay fattens the tails, sigma rises
and z* shifts up; the gap between the two is itself a reportable finding.

Design echo: like summarize/MCSummary in mc_engine, analysis and plotting are
SEPARATE — convergence_analysis() computes and returns a ConvergenceResult;
plot_convergence() draws it. Keeps the diagnostic testable and the rendering
swappable. The sweep reuses run_monte_carlo untouched: convergence IS the
engine called at varying n, never a second valuation path.

Locked architecture (the endpoint is fixed and explicit)
--------------------------------------------------------
    default pass -> estimate z* -> estimate recommended batch count
                 -> ONE refinement pass at the recommended count -> stop.

There is NO iterative self-calibration loop. The refinement is a VALIDATION
step, not the start of a recursion. The recursion terminates because we combine
a closed-form per-point reliability (the SD of B batch-means has known sampling
error 1/sqrt(2(B-1)) -> the recommended batch count) with a SINGLE empirical
z*-stability check (did z* move after refining?). Note the precision: z* itself
is a nonlinear threshold-crossing of several scatter points, so its reliability
is NOT directly the closed form — which is exactly why one empirical refinement
pass is the right tool there, rather than another simulation layer. If the
refined pass still appears under-resolved, that fact is reported
(ConvergencePair.adequately_resolved=False, final_recommendation exposes the
residual) and the user decides — the engine does not auto-launch another cycle.

Documented caveats (implementation details, not architecture)
-------------------------------------------------------------
  - Grid quantization: z* can only take values in N_GRID, so "z* moved" detects
    grid-cell jumps; near a grid boundary noise could flip it. The true z*
    resolution is the grid spacing. Refinement reduces spurious flips but cannot
    beat the grid.
  - Compute cap: the refinement pass scales linearly with its batch count, so it
    is clamped to MAX_REFINEMENT_BATCHES; a larger recommendation is reported as
    a residual rather than ground out.
  - Borderline: when z* converges so near the bar that the clean-call batch
    count is implausibly large, the company is genuinely borderline and the
    refinement is skipped — more batches cannot sharpen an on-the-bar decision.
"""

from dataclasses import dataclass
from typing import List, Optional, Sequence

import numpy as np

from dcf import DCFInputs
from mc_config import MCConfig
from mc_engine import run_monte_carlo, summarize, MCSummary, format_summary
import mc_defaults


# ============================================================
#  THE RESULT OBJECT
# ============================================================
#  Everything the sweep learned, in one read-only container —
#  enough to report z* AND to redraw the diagnostic plot without
#  re-running the (expensive) sweep. Pure description; no engine
#  logic lives here.
# ============================================================


@dataclass
class ConvergenceResult:
    """The outcome of one convergence sweep.

    Fields:
        n_grid:
            the candidate sample sizes tested (mc_defaults.N_GRID), in order.
        scatter:
            scatter[i] = standard deviation of the run-means at n_grid[i].
            This is the decay curve — the y-values plotted against n_grid.
        center:
            center[i] = average of the run-means at n_grid[i]. ~the valuation
            at that n; used to set the relative-precision bar (rule 2).
        sigma_estimate:
            per-simulation standard deviation from one large reference run.
            Lets the caller overlay the theoretical sigma/sqrt(n) curve and
            confirm the empirical scatter tracks it (the CLT self-check).
        z_pct:
            rule 2 — smallest grid n whose scatter < precision bar. None if no
            grid point clears the bar (grid too small for this company).
        z_elbow:
            rule 3 — the kneedle elbow of the scatter curve.
        z_star:
            the headline answer: max(z_pct, z_elbow), the conservative combine.
        precision_bar:
            the dollar value of the 1%-of-valuation bar, for plotting/reporting.
        batch_rel_se:
            the relative sampling error of EACH scatter estimate,
            1/sqrt(2(B-1)). The closed-form fuzz on every dot — the reason the
            curve wobbles. Used to draw error bars and to grade B.
        batches_used:
            BATCHES_PER_N actually used for this sweep.
        batches_recommended:
            how many batches THIS company's variance profile actually wants,
            so the z* point clears the bar by CONVERGENCE_DECISION_SIGMAS of its
            own error bands. The anti-folklore output: 40 graded, not assumed.
        decision_margin_pct:
            how far (as a %) the z* scatter point sits below the bar. Drives the
            recommendation; large = comfortable, near-zero = borderline company.
        borderline:
            True when z* converges so close to the bar that no practical batch
            count can sharpen the call — a property of the company, not a defect.
    """

    n_grid: List[int]
    scatter: List[float]
    center: List[float]
    sigma_estimate: float
    z_pct: Optional[int]
    z_elbow: int
    z_star: int
    precision_bar: float
    batch_rel_se: float
    batches_used: int
    batches_recommended: int
    decision_margin_pct: float
    borderline: bool


# ============================================================
#  THE ELBOW FINDER  (rule 3)
# ============================================================
#  Kneedle, the simple geometric version: for a convex,
#  decreasing curve, the "knee" is the point sitting furthest
#  BELOW the straight chord joining the first and last points.
#  We normalise both axes to [0, 1] first so the distance is
#  measured fairly regardless of the raw scales (n runs into the
#  thousands; scatter is under a dollar).
# ============================================================


def _find_elbow(n_grid: List[int], scatter: List[float]) -> int:
    """Return the n in `n_grid` at the elbow of the scatter curve.

    Recipe:
      1. Normalise n_grid -> x in [0, 1] and scatter -> y in [0, 1].
      2. Draw the chord from the first point (x=0, y=1 for a decreasing
         curve) to the last (x=1, y~0).
      3. For each point, measure how far BELOW the chord it sits.
      4. The elbow is the point with the largest such gap.

    Why "below the chord": a convex decreasing curve bows downward beneath
    its endpoints; the deepest bow is the bend where the steep early decline
    gives way to the slow tail — exactly the diminishing-returns point.
    """
    x = np.asarray(n_grid, dtype=float)
    y = np.asarray(scatter, dtype=float)

    # Normalise both axes to [0, 1] so neither dominates the distance.
    x_norm = (x - x.min()) / (x.max() - x.min())
    y_norm = (y - y.min()) / (y.max() - y.min())

    # The chord's height at each x: straight line from first point to last.
    chord = y_norm[0] + (y_norm[-1] - y_norm[0]) * x_norm

    # Gap = how far each point sits below that chord. Biggest gap = the elbow.
    gap = chord - y_norm
    return int(n_grid[int(np.argmax(gap))])


# ============================================================
#  THE SWEEP
# ============================================================
#  Walk the grid, measure scatter at each n, then apply the two
#  rules. The only expensive part is the nested loop: for each of
#  the ~10 grid points we run the full engine BATCHES_PER_N times.
# ============================================================


def convergence_analysis(
    base: DCFInputs,
    config: Optional[MCConfig] = None,
    batches: Optional[int] = None,
    runner=run_monte_carlo,
) -> ConvergenceResult:
    """Find the per-company convergence sample size z* for `base`.

    For every candidate n in mc_defaults.N_GRID, run the engine `batches`
    times and record the scatter (std) and center (mean) of those run-means.
    Then apply the layered rule: z* = max(z_pct, z_elbow).

    `runner` is the engine the sweep measures — a function (base, config) ->
    list of per-share values. It defaults to run_monte_carlo (the continuous
    step-3 engine, giving z*). Pass run_monte_carlo_with_shocks to measure the
    shocked engine instead (giving z**). Convergence stays blind to WHICH engine
    it's driving — it just measures whatever function it's handed — so the same
    machinery produces z* and z** through an identical code path, and the only
    difference between the two answers is the engine's own noise profile. This
    is the dependency-injection seam: the convergence module imports no engine
    but run_monte_carlo, and the caller supplies anything richer.

    `batches` is the size of the measurement apparatus — how many times the
    engine is re-run at each n to estimate the scatter. It defaults to
    mc_defaults.BATCHES_PER_N, but is a PER-RUN KNOB on purpose: the project's
    whole thesis is that sample sizes should be chosen empirically, not
    inherited, and that applies to the measuring layer too. The companion
    `convergence_with_recommendation` uses this hook to re-run at the
    apparatus-recommended batch count.

    The optional `config` lets a caller thread a random_seed (for a
    reproducible sweep) or calibration overrides (width/correlation) through
    to every underlying run. n_simulations on a passed-in config is IGNORED —
    the sweep sets n itself from the grid, since sweeping n IS the job. When
    config is None the sweep is seeded with mc_defaults.CONVERGENCE_DEFAULT_SEED
    so the study is reproducible by default; pass an explicit config with
    random_seed=None for an intentionally fresh, nondeterministic draw.

    Returns a ConvergenceResult holding the full curve plus z_pct, z_elbow,
    z_star and the sigma estimate. Computation only — call plot_convergence
    to draw it.
    """
    # Resolve the apparatus size: explicit arg wins, else the labelled default.
    n_batches = mc_defaults.BATCHES_PER_N if batches is None else batches
    # Base config to clone per grid point. We copy its seed + overrides but
    # swap in each grid n. A fixed seed makes the entire sweep reproducible;
    # within a sweep we offset the seed per batch so the batches differ.
    # Seeded by default for reproducibility: a convergence study is a MEASUREMENT
    # and must return the same z*/rec_batches on every call, so with no config we
    # fall back to the labelled default seed rather than None. A caller wanting a
    # fresh nondeterministic draw passes an explicit config with random_seed=None.
    seed = config.random_seed if config is not None else mc_defaults.CONVERGENCE_DEFAULT_SEED
    width_ov = config.width_overrides if config is not None else None
    corr_ov = config.correlation_overrides if config is not None else None

    n_grid = list(mc_defaults.N_GRID)
    scatter: List[float] = []
    center: List[float] = []

    # ---- 1. Sweep the grid ----
    for gi, n in enumerate(n_grid):
        run_means: List[float] = []
        for b in range(n_batches):
            # Per-batch seed: derived from the base seed (if any) so the whole
            # sweep is reproducible, but distinct per (grid point, batch) so no
            # two batches are identical draws. None stays None (nondeterministic).
            batch_seed = None if seed is None else seed + gi * 1000 + b
            batch_cfg = MCConfig(
                n_simulations=n,
                random_seed=batch_seed,
                width_overrides=width_ov,
                correlation_overrides=corr_ov,
            )
            results = runner(base, batch_cfg)
            run_means.append(float(np.mean(results)))

        means = np.asarray(run_means)
        scatter.append(float(means.std()))   # the decay-curve y-value at this n
        center.append(float(means.mean()))   # ~the valuation at this n

    # ---- 2. Per-simulation sigma, from one large reference run ----
    # Used only for the sigma/sqrt(n) self-check overlay. n = 4x the biggest
    # grid point gives a stable sigma without dominating the sweep's runtime.
    ref_seed = None if seed is None else seed + 999_999
    ref = np.asarray(
        runner(
            base,
            MCConfig(
                n_simulations=4 * n_grid[-1],
                random_seed=ref_seed,
                width_overrides=width_ov,
                correlation_overrides=corr_ov,
            ),
        )
    )
    sigma_estimate = float(ref.std())

    # ---- 3. Rule 2: the precision bar (scale-free), monotone clearance ----
    # Bar = 1% of the valuation. Use the center at the largest n (the most
    # settled estimate of the valuation) so the bar itself isn't noisy.
    #
    # The rule is NOT "first n under the bar". That is just the first CROSSING,
    # and it gets fooled by noise: we measure scatter from only BATCHES_PER_N
    # batches, so the scatter ESTIMATE wobbles and the curve isn't perfectly
    # monotone (n=1000 can dip under the bar while n=1500 pops back over it).
    # Picking 1000 there is logically inconsistent — a larger n then fails.
    #
    # Convergence must mean "stays converged": z_pct is the smallest grid n
    # such that it AND every larger grid point remain under the bar. This
    # survives the inherent wobble of measuring Monte Carlo output with another
    # Monte Carlo process layered on top — the definition is robust to noise
    # rather than depending on the noise being absent. Clean one-liner for the
    # write-up: "the first candidate sample size after which the precision
    # criterion remains satisfied for all larger sample sizes".
    precision_bar = mc_defaults.CONVERGENCE_PRECISION_PCT * center[-1]
    z_pct: Optional[int] = None
    for i, n in enumerate(n_grid):
        # Does this point and every larger grid point stay under the bar?
        if all(s < precision_bar for s in scatter[i:]):
            z_pct = n
            break  # ascending grid -> first such n is the smallest

    # ---- 4. Rule 3: the elbow ----
    z_elbow = _find_elbow(n_grid, scatter)

    # ---- 5. Layer them — conservative combine ----
    # If no grid point cleared the precision bar, fall back to the elbow alone
    # (and the caller can read z_pct=None as "widen the grid for this company").
    z_star = z_elbow if z_pct is None else max(z_pct, z_elbow)

    # ---- 6. Grade the apparatus: was BATCHES_PER_N enough for THIS company? ----
    # Every scatter estimate has a known relative sampling error, because the
    # sample standard deviation of B numbers is itself a random quantity with
    # SE/s = 1/sqrt(2(B-1)). THIS is the closed form that stops the
    # "convergence of convergence" regress from going infinite: the inner loop
    # (the valuation distribution) has an unknown shape and must be simulated,
    # but the outer loop (the SD of B batch-means) has a known sampling
    # distribution, so its reliability is a formula, not another simulation.
    B = n_batches
    batch_rel_se = 1.0 / np.sqrt(2.0 * (B - 1))

    # How far below the bar does the point we actually rely on (z_star) sit?
    # That margin — not the wobble of points sitting ON the bar — is what the
    # recommendation targets. A point straddling the bar is genuinely borderline
    # and no batch count resolves it; that's a fact about the company.
    z_star_idx = n_grid.index(z_star)
    z_star_scatter = scatter[z_star_idx]
    # Relative distance of the z* scatter from the bar. Positive = under the bar
    # (the normal, healthy case). Guard against a zero/over-bar pathology.
    margin = (precision_bar - z_star_scatter) / z_star_scatter if z_star_scatter > 0 else 0.0
    decision_margin_pct = margin * 100.0

    # Recommended B: enough batches that the z* point clears the bar by
    # CONVERGENCE_DECISION_SIGMAS of its own error bands. Invert
    # 1/sqrt(2(B-1)) <= margin / sigmas  ->  B >= sigmas^2 / (2 margin^2) + 1.
    sigmas = mc_defaults.CONVERGENCE_DECISION_SIGMAS
    if margin <= 0:
        # z* sits at/above the bar — should not happen given how z* is chosen,
        # but if it does the decision is unresolved at any practical B.
        borderline = True
        batches_recommended = B
    else:
        batches_recommended = int(np.ceil(sigmas**2 / (2.0 * margin**2) + 1))
        # "Borderline" when z* converges so near the bar that the clean-call
        # batch count is implausibly large — the company genuinely settles right
        # at the threshold and more batches won't sharpen it.
        borderline = batches_recommended > 1000

    return ConvergenceResult(
        n_grid=n_grid,
        scatter=scatter,
        center=center,
        sigma_estimate=sigma_estimate,
        z_pct=z_pct,
        z_elbow=z_elbow,
        z_star=z_star,
        precision_bar=precision_bar,
        batch_rel_se=batch_rel_se,
        batches_used=B,
        batches_recommended=batches_recommended,
        decision_margin_pct=decision_margin_pct,
        borderline=borderline,
    )


# ============================================================
#  TWO-PASS: DEFAULT + RECOMMENDED BATCH COUNT
# ============================================================
#  The apparatus grades its own batch count (above). This runs
#  the natural follow-up: if the default batch count wasn't the
#  recommended one, re-run the WHOLE sweep at the recommended
#  size and hand back BOTH results so the user sees the default
#  and the better-resolved answer side by side. General-purpose:
#  works for any DCFInputs, not just the teaching fixture.
# ============================================================


@dataclass
class ConvergencePair:
    """A default-batch sweep plus an optional re-run at the recommended size.

    The endpoint of the convergence architecture: default pass -> z* ->
    recommended batch count -> ONE refinement pass -> stop. There is no
    iterative self-calibration loop. If the refinement pass still appears
    under-resolved, that fact is reported (adequately_resolved=False,
    final_recommendation exposes the residual) but NO further pass is launched.
    The refinement is a validation step, not the start of a recursion.

    Fields:
        default:
            the sweep at the default (or caller-supplied) batch count.
        refined:
            the sweep re-run at the (capped) recommended batch count, or None
            when no re-run was needed (default already met the recommendation),
            the company is borderline, or re-run was switched off.
        z_star_moved:
            True when the refined sweep produced a different z* than the
            default — i.e. the extra resolution actually changed the answer.
            None when there was no refined pass.
        z_star:
            the final answer — the refined pass's z* if there was one, else the
            default's. This is the number to report downstream.
        adequately_resolved:
            the HONEST final verdict, sourced from the pass we actually ended on
            (refined if present, else default): did that pass use at least as
            many batches as it then re-recommends? False means even after
            refinement the apparatus wants more — reported, not auto-fixed.
        final_recommendation:
            the batches_recommended from the pass we ended on. When
            adequately_resolved is False, this is the residual ask the user can
            act on deliberately.
        refinement_capped:
            True when the recommended batch count exceeded MAX_REFINEMENT_BATCHES
            and the refinement pass ran at the cap instead. Signals that
            adequately_resolved / final_recommendation should be read knowing the
            re-run was compute-limited.
    """

    default: ConvergenceResult
    refined: Optional[ConvergenceResult]
    z_star_moved: Optional[bool]
    z_star: int
    adequately_resolved: bool
    final_recommendation: int
    refinement_capped: bool


def convergence_with_recommendation(
    base: DCFInputs,
    config: Optional[MCConfig] = None,
    batches: Optional[int] = None,
    rerun: bool = True,
    runner=run_monte_carlo,
) -> ConvergencePair:
    """Run the convergence sweep, then optionally re-run at the recommended B.

    Pass one runs at the default (or supplied) batch count and produces a
    recommendation — how many batches THIS company's variance profile wants
    for a clean call. Pass two, when `rerun` is True and the recommendation
    exceeds the batches just used, re-runs the entire sweep at the recommended
    count so the user gets the better-resolved answer alongside the default.

    Only ONE refinement pass is taken, not an iterative loop. That is the
    deliberate, bounded choice: the closed-form recommendation already tells us
    the size sufficient for a clean call, so re-deriving it again would be the
    infinite-regress we explicitly avoid. (A caller who wants to inspect
    stability further can still call convergence_analysis at any batch count.)

    Borderline companies (z* converging right at the bar) are NOT re-run: more
    batches cannot sharpen a genuinely on-the-bar decision, so a second pass
    would just burn compute. The default result carries the borderline flag.

    The final verdict (adequately_resolved, final_recommendation) is sourced
    from the pass we END on — the refined pass when there is one, else the
    default. If the refined pass STILL wants more batches than it used, that is
    reported honestly; the engine does NOT launch another cycle. Endpoint fixed.

    Returns a ConvergencePair. General-purpose — any DCFInputs.
    """
    default = convergence_analysis(base, config=config, batches=batches, runner=runner)

    # Decide whether a second pass is warranted: only when asked, only when the
    # company isn't borderline, and only when more batches were actually
    # recommended than we just used (otherwise the default already suffices).
    needs_rerun = (
        rerun
        and not default.borderline
        and default.batches_recommended > default.batches_used
    )
    if not needs_rerun:
        # No refinement: the verdict is the default pass's own self-assessment.
        resolved = default.batches_used >= default.batches_recommended
        return ConvergencePair(
            default=default,
            refined=None,
            z_star_moved=None,
            z_star=default.z_star,
            adequately_resolved=resolved or default.borderline,
            final_recommendation=default.batches_recommended,
            refinement_capped=False,
        )

    # Compute cap: the single refinement pass scales linearly with its batch
    # count, so clamp it. If the recommendation exceeds the cap we refine at the
    # cap and let the refined pass's own (possibly still-unmet) recommendation
    # surface as the residual — honest, and still exactly ONE pass.
    refine_batches = min(default.batches_recommended, mc_defaults.MAX_REFINEMENT_BATCHES)
    refinement_capped = default.batches_recommended > mc_defaults.MAX_REFINEMENT_BATCHES

    refined = convergence_analysis(base, config=config, batches=refine_batches, runner=runner)

    # HONEST FINAL VERDICT — sourced from the refined pass, not assumed. The
    # refined pass re-measured the margin at higher resolution and produced its
    # OWN recommendation; adequacy is whether it used at least that many. If not,
    # we report it and expose the residual; we do NOT loop again.
    resolved = refined.batches_used >= refined.batches_recommended
    return ConvergencePair(
        default=default,
        refined=refined,
        z_star_moved=(refined.z_star != default.z_star),
        z_star=refined.z_star,
        adequately_resolved=resolved,
        final_recommendation=refined.batches_recommended,
        refinement_capped=refinement_capped,
    )


# ============================================================
#  PLOTTING  (separate from analysis, on purpose)
# ============================================================
#  Draws the decay curve, the measured scatter dots, the
#  theoretical sigma/sqrt(n) overlay, and the two rule markers.
#  Returns the saved path; never recomputes the sweep.
# ============================================================


def plot_convergence(
    result: ConvergenceResult,
    save_path: str = "convergence.png",
    title: str = "Monte Carlo convergence",
) -> str:
    """Render a ConvergenceResult to a PNG and return the file path.

    Shows four things: the measured scatter at each grid n (dots), the
    theoretical sigma/sqrt(n) curve (line — the CLT self-check), the 1%
    precision bar (horizontal), and vertical markers at z_pct, z_elbow and
    z_star. Plotting only; all numbers come from `result`.
    """
    # Imported here, not at module top: the analysis half of this file must
    # stay importable (and testable) on machines without matplotlib.
    import matplotlib
    matplotlib.use("Agg")  # headless backend — write a file, open no window
    import matplotlib.pyplot as plt

    n_grid = np.asarray(result.n_grid, dtype=float)

    # Smooth theoretical curve sigma/sqrt(n) across the grid's span.
    fine = np.linspace(n_grid.min(), n_grid.max(), 400)
    theory = result.sigma_estimate / np.sqrt(fine)

    plt.figure(figsize=(9, 5.5))
    plt.plot(fine, theory, color="#4C6EF5", lw=2,
             label=r"theory: $\sigma/\sqrt{n}$")
    # Error bars: each scatter dot carries 1/sqrt(2(B-1)) relative fuzz — the
    # closed-form reason the curve wobbles. Drawing it makes the apparatus's
    # own resolution visible, so a dot straddling the bar reads as "can't call
    # this one" rather than a hard pass/fail.
    yerr = np.asarray(result.scatter) * result.batch_rel_se
    plt.errorbar(result.n_grid, result.scatter, yerr=yerr, fmt="o",
                 color="#E8590C", ecolor="#E8590C", elinewidth=1, capsize=3,
                 markersize=6, zorder=5,
                 label=f"measured scatter ({result.batches_used} batches, "
                       f"±{result.batch_rel_se*100:.0f}%)")
    plt.axhline(result.precision_bar, color="#2F9E44", ls="--", lw=1.2,
                label=f"1% precision bar (${result.precision_bar:.3f})")

    if result.z_pct is not None:
        plt.axvline(result.z_pct, color="#2F9E44", ls=":", lw=1.2)
        plt.scatter([result.z_pct],
                    [result.sigma_estimate / np.sqrt(result.z_pct)],
                    color="#2F9E44", marker="s", s=90, zorder=6,
                    label=f"precision (rule 2): n={result.z_pct}")
    plt.axvline(result.z_elbow, color="#9C36B5", ls=":", lw=1.4)
    plt.scatter([result.z_elbow],
                [result.sigma_estimate / np.sqrt(result.z_elbow)],
                color="#9C36B5", marker="D", s=90, zorder=6,
                label=f"elbow (rule 3): n={result.z_elbow}")
    plt.axvline(result.z_star, color="black", lw=2.2, alpha=0.8)
    plt.text(result.z_star + n_grid.max() * 0.01,
             max(result.scatter) * 0.85,
             f"z* = {result.z_star}", fontsize=11, fontweight="bold")

    plt.xlabel("n  (simulations per run)")
    plt.ylabel("scatter of run-means  ($/share)")
    plt.title(title)
    plt.legend(fontsize=9)
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(save_path, dpi=130)
    plt.close()
    return save_path


# ============================================================
#  TEXT REPORT
# ============================================================
#  The numbers an analyst reads off the sweep, including the
#  batch-count grade — the apparatus reporting its own
#  reliability for THIS company rather than asserting a default.
# ============================================================


def format_convergence(result: ConvergenceResult) -> str:
    """Render a ConvergenceResult as a readable multi-line block.

    Pure formatting; the caller prints the returned string. The headline line
    is the anti-folklore grade: how many batches were used vs how many this
    company's variance profile actually wants.
    """
    lines = [
        f"Convergence analysis",
        f"  per-simulation sigma   : {result.sigma_estimate:8.3f}",
        f"  precision bar (1%)      : {result.precision_bar:8.3f}",
        f"  z_pct  (precision rule) : {result.z_pct}",
        f"  z_elbow (diminishing)   : {result.z_elbow}",
        f"  z*  = max(...)          : {result.z_star}",
        f"  -> run production MC at : n = {result.z_star} simulations",
        "",
        f"  batches used            : {result.batches_used}"
        f"  (each scatter ±{result.batch_rel_se*100:.0f}%)",
        f"  z* clears bar by        : {result.decision_margin_pct:.1f}%",
        f"  batches recommended     : {result.batches_recommended}"
        f"  (for a {mc_defaults.CONVERGENCE_DECISION_SIGMAS:.0f}-sigma-clean call)",
    ]
    if result.borderline:
        lines.append("  note: z* converges near the bar — this company is "
                     "genuinely borderline; more batches won't sharpen it.")
    else:
        verdict = ("adequate" if result.batches_used >= result.batches_recommended
                   else f"under-resolved — bump to {result.batches_recommended}")
        lines.append(f"  verdict                 : {verdict}")
    return "\n".join(lines)


def format_pair(pair: ConvergencePair) -> str:
    """Render a ConvergencePair: the default pass and the recommended re-run.

    Shows both sweeps so the user can see what the default batch count gave AND
    what the better-resolved (recommended) batch count gave — plus, crucially,
    whether z* actually moved between them. Pure formatting.
    """
    lines = ["=" * 52,
             f"PASS 1 — default apparatus ({pair.default.batches_used} batches)",
             "=" * 52,
             format_convergence(pair.default)]

    if pair.refined is None:
        lines += ["", "(no second pass — default already meets the "
                  "recommendation, or the company is borderline / re-run off)",
                  "-" * 52,
                  f"FINAL z*               : {pair.z_star}",
                  f"-> run production MC at : n = {pair.z_star} simulations",
                  f"adequately resolved?   : {'yes' if pair.adequately_resolved else 'no'}",
                  f"final recommendation   : {pair.final_recommendation} batches"]
        return "\n".join(lines)

    lines += ["",
              "=" * 52,
              f"PASS 2 — recommended apparatus ({pair.refined.batches_used} batches)"
              + ("  [capped]" if pair.refinement_capped else ""),
              "=" * 52,
              format_convergence(pair.refined),
              "",
              "-" * 52,
              f"z* default             : {pair.default.z_star}",
              f"z* refined (FINAL)     : {pair.refined.z_star}",
              f"-> run production MC at : n = {pair.z_star} simulations",
              f"z* moved?              : {'YES — extra resolution changed the answer' if pair.z_star_moved else 'no — answer stable under finer measurement'}",
              f"adequately resolved?   : {'yes' if pair.adequately_resolved else 'NO — still under-resolved'}",
              f"final recommendation   : {pair.final_recommendation} batches"
              + ("  (refinement was compute-capped)" if pair.refinement_capped else "")]
    if not pair.adequately_resolved:
        lines.append("  -> reported as residual, NOT auto-refined further "
                     "(endpoint is fixed at one refinement pass).")
    return "\n".join(lines)


# ============================================================
#  STEP 6 — SHOCKED CONVERGENCE  (the only seam to mc_shocks)
# ============================================================
#  Convergence stays engine-blind (see the `runner` arg). These
#  thin wrappers are the SINGLE place this module reaches toward
#  the step-5 shock layer, and they do it by lazy import so the
#  decoupling holds at import time too: you can import and use the
#  continuous convergence path on a machine that never loads
#  mc_shocks. Finding z** is just finding z* with a noisier engine.
# ============================================================


def convergence_with_shocks(base: DCFInputs, **kwargs) -> ConvergencePair:
    """Convergence on the SHOCKED engine -> the post-shock sample size z**.

    Identical machinery to convergence_with_recommendation; only the engine
    swapped to run_monte_carlo_with_shocks. Shocks fatten the left tail, so the
    per-run noise (sigma) rises and the scatter = sigma/sqrt(n) curve crosses
    the precision bar later -> z** typically exceeds z*. The z*->z** gap is a
    headline finding: it quantifies how much the discrete-event risk costs in
    required sample size, something a fixed-10,000 convention can't even see.

    All other knobs (config, batches, rerun) pass straight through.
    """
    from mc_shocks import run_monte_carlo_with_shocks
    return convergence_with_recommendation(
        base, runner=run_monte_carlo_with_shocks, **kwargs
    )


# ============================================================
#  PRODUCTION SYNTHESIS  (the find-it -> use-it arrow)
# ============================================================
#  Convergence MEASURES the ruler (how many simulations this
#  company needs); production USES the ruler (runs the engine at
#  that count and reports the valuation distribution). They are
#  two different jobs and were always meant to be two steps — the
#  build sequence pairs "find n*" with "run production at n*".
#  Everything below consumes z* and produces the actual answer;
#  it picks no n of its own and never touches the folk 10,000.
# ============================================================


def _z_star_of(convergence) -> int:
    """Read the headline sample size off either convergence object.

    Accepts a ConvergenceResult (one sweep) OR a ConvergencePair (the two-pass
    default+refined endpoint). Both expose `z_star`; for a pair that is already
    the FINAL z* (the refined pass's value when a refinement happened). The
    production layer needs nothing else from convergence — just the number.
    """
    return int(convergence.z_star)


def production_valuation(
    base: DCFInputs,
    convergence,
    market_price: Optional[float] = None,
    config: Optional[MCConfig] = None,
    percentiles: Optional[Sequence[int]] = None,
    runner=run_monte_carlo,
) -> MCSummary:
    """Run the PRODUCTION Monte Carlo at the convergence-derived sample size.

    This is the step the architecture was missing: convergence found z*, and
    THIS runs the engine once at n = z* to produce the valuation distribution
    an analyst actually reports (mean, median, percentile band, and — the
    headline thesis signal — where today's market price falls inside the
    simulated distribution).

    `convergence` is whatever the convergence step returned — a
    ConvergenceResult or a ConvergencePair. We read z* off it and run at that n.
    We do NOT default to 10,000; the whole point of step 4 is that the company,
    not folklore, sets the sample size.

    The optional `config` threads a random_seed / calibration overrides through
    to the production run; its n_simulations is IGNORED because z* sets n. When
    omitted, an unseeded config is used (a fresh, nondeterministic draw).

    Returns an MCSummary. Pure orchestration: it calls run_monte_carlo + summarize.
    """
    z = _z_star_of(convergence)
    seed = config.random_seed if config is not None else None
    width_ov = config.width_overrides if config is not None else None
    corr_ov = config.correlation_overrides if config is not None else None
    prod_cfg = MCConfig(
        n_simulations=z,
        random_seed=seed,
        width_overrides=width_ov,
        correlation_overrides=corr_ov,
    )
    results = runner(base, prod_cfg)
    # When percentiles is None, defer to summarize's own DEFAULT_PERCENTILES
    # rather than re-importing the constant here.
    if percentiles is None:
        return summarize(results, market_price=market_price)
    return summarize(results, market_price=market_price, percentiles=percentiles)


# ============================================================
#  BENCHMARK  (the thesis proof exhibit)
# ============================================================
#  Runs production at z* AND at the folk 10,000 under the SAME
#  seed, so the comparison is fair (only n differs — not the RNG
#  luck). The payoff: near-identical mean/median/percentiles at a
#  fraction of the compute. This is what turns "I built a
#  convergence module" into "here is proof the 10,000 is waste".
# ============================================================


@dataclass
class BenchmarkResult:
    """A z* production run set against the folk-10,000 production run.

    Both runs use the SAME base inputs and the SAME seed; only n differs, so any
    difference in the summaries is attributable to sample size alone, not to
    different random draws. The story: the two distributions agree to within
    sampling noise while z* uses `compute_ratio` of the simulations.

    Fields:
        z_star:        the convergence-derived sample size used by the cheap run.
        folk_n:        the convention being challenged (default 10,000).
        z_summary:     MCSummary of the production run at n = z*.
        folk_summary:  MCSummary of the production run at n = folk_n.
        compute_ratio: z_star / folk_n — e.g. 0.20 means "20% of the work".
        mean_gap_pct:  |mean_z - mean_folk| as a % of the folk mean — how little
                       precision the extra simulations actually bought.
    """

    z_star: int
    folk_n: int
    z_summary: MCSummary
    folk_summary: MCSummary
    compute_ratio: float
    mean_gap_pct: float


def benchmark_against_folk(
    base: DCFInputs,
    convergence,
    market_price: Optional[float] = None,
    folk_n: int = 10_000,
    seed: Optional[int] = 42,
    runner=run_monte_carlo,
) -> BenchmarkResult:
    """Compare the z* production run to the folk-`folk_n` run under one seed.

    Runs the engine at n = z* and at n = folk_n (default 10,000) with the SAME
    random seed, so the only difference between the two summaries is the sample
    size. Returns a BenchmarkResult holding both summaries plus the compute
    ratio and the mean gap — the numbers that demonstrate the step-4 thesis:
    the folk number buys ~nothing the company-specific number didn't already have.

    A fixed default seed (42) makes the exhibit reproducible; pass seed=None for
    a fresh draw or another int to check the gap is stable across seeds.
    """
    z = _z_star_of(convergence)
    z_results = runner(base, MCConfig(n_simulations=z, random_seed=seed))
    folk_results = runner(base, MCConfig(n_simulations=folk_n, random_seed=seed))

    z_sum = summarize(z_results, market_price=market_price)
    folk_sum = summarize(folk_results, market_price=market_price)

    compute_ratio = z / folk_n
    mean_gap_pct = (
        abs(z_sum.mean - folk_sum.mean) / abs(folk_sum.mean) * 100.0
        if folk_sum.mean != 0 else 0.0
    )
    return BenchmarkResult(
        z_star=z,
        folk_n=folk_n,
        z_summary=z_sum,
        folk_summary=folk_sum,
        compute_ratio=compute_ratio,
        mean_gap_pct=mean_gap_pct,
    )


def format_benchmark(bench: BenchmarkResult) -> str:
    """Render a BenchmarkResult as a side-by-side table. Pure formatting.

    The headline lines at the bottom are the thesis in two numbers: how much
    less compute z* used, and how little the answer moved because of it.
    """
    z, f = bench.z_summary, bench.folk_summary

    def row(label: str, zv: float, fv: float) -> str:
        return f"  {label:<14}{zv:>14.4f}{fv:>14.4f}"

    lines = [
        "=" * 46,
        "BENCHMARK — z* vs folk-10,000 (same seed)",
        "=" * 46,
        f"  {'metric':<14}{'z* run':>14}{'folk run':>14}",
        f"  {'n':<14}{bench.z_star:>14d}{bench.folk_n:>14d}",
        row("mean", z.mean, f.mean),
        row("median", z.median, f.median),
        row("std", z.std, f.std),
    ]
    for p in sorted(z.percentiles):
        if p in f.percentiles:
            lines.append(row(f"p{p}", z.percentiles[p], f.percentiles[p]))
    if z.market_percentile is not None and f.market_percentile is not None:
        lines.append(row("mkt pctile", z.market_percentile, f.market_percentile))
    lines += [
        "-" * 46,
        f"  compute used   : {bench.compute_ratio * 100:.0f}% of the folk run "
        f"({bench.z_star} vs {bench.folk_n} simulations)",
        f"  mean moved by  : {bench.mean_gap_pct:.2f}%  "
        f"<- what the extra {bench.folk_n - bench.z_star} sims bought",
    ]
    return "\n".join(lines)
