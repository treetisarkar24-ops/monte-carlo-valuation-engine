"""
Monte Carlo Engine — micro-shock overlay (step 5)
=================================================

Layer two of the deliberately-two-layer design. Step 3 gave every path a
continuous, correlated perturbation (the "weather" — normal variation around
the forecast). This module adds discrete, state-conditional shocks on top (the
"earthquakes" — events larger than the weather can produce). Together they
generate cascades and the fat LEFT tail that a continuous-only model cannot.

What a shock IS, precisely: a discrete event whose magnitude lands OUTSIDE the
range step-3 perturbation can plausibly reach. Below that line it's already
modelled as continuous noise; above it, it's a shock. The two layers partition
the world, no double-counting.

The five channels (universal transmission routes; real events like customer
loss / downgrade / recall map onto them):

    revenue    -> persistent haircut on the revenue LEVEL
    margin     -> persistent multiplicative compression of operating margin
    funding    -> relative increase in cost_of_debt (hits WACC, the denominator)
    strategic  -> relative reduction in terminal_growth (franchise impairment)
    cash       -> one-off cash outflow, a % of that year's revenue

The fragility mechanic (why shocks cluster into death spirals):

    Each path carries a STRESS number — accumulated FRAGILITY, i.e. how primed
    the company is to take the NEXT hit. It is NOT a value estimate and NOT
    itself a probability. Every shock that fires adds its severity to stress
    (equal weight across channels in V1), and stress raises the probability of
    future shocks:  adjusted_hazard = base * (1 + sensitivity * stress).
    A wounded path is likelier to be wounded again — the death spiral — and the
    left tail emerges from the minority of paths that cascade. Nobody authors
    "recover / struggle / distress" branches; those clusters EMERGE across many
    paths, and the histogram IS the set of stories.

ORDERING — shocks land on the step-3 PERTURBED trajectory, not the central
case. So the same shock bites harder on a path step-3 already made weak than on
a strong one (drowning-company logic), and the engine's own nonlinearity
amplifies it. `sample_inputs_with_shocks` does perturb-then-shock in that order.

The deterministic engine (dcf.run_dcf) and the step-3 sampler
(mc_engine.sample_inputs) are NOT touched. Shocks ride existing DCFInputs
dials wherever possible; only the cash channel needs a new transmission point
(it accrues to net_debt, since FCF is built bottom-up with no slot for a
one-off outflow).

DEFERRED to V2 (designed, not built — see design-decisions-mc-step5):
  - healing: stress drifting back down on quiet years (here it only accrues);
  - break/distress absorbing states reading the same stress number;
  - differentiated fragility weights and per-company hazard calibration.
Each is a small, marked insertion, not a restructure.
"""

from dataclasses import dataclass, field, replace
from typing import Dict, List, Optional, Tuple

import numpy as np

from dcf import DCFInputs, run_dcf, project_revenue
from mc_config import MCConfig
from mc_engine import sample_inputs
import mc_defaults


# ============================================================
#  SHOCK RECORD + OUTCOME
# ============================================================
#  Lightweight bookkeeping so a single path's shock history is
#  inspectable (used by the smoke test and any diagnostics).
#  None of this feeds the valuation — run_dcf only ever sees the
#  shocked DCFInputs.
# ============================================================


@dataclass
class ShockEvent:
    """One shock that fired on one path."""
    year: int          # forecast year it struck (1-based)
    channel: str       # which transmission channel
    severity: float    # the uniform-[0,1] draw
    damage: float      # the interpolated damage magnitude (channel-specific units)


@dataclass
class ShockOutcome:
    """The result of overlaying shocks on one perturbed DCFInputs.

    Fields:
        inputs:       the shocked DCFInputs, ready for run_dcf.
        events:       every shock that fired, in time order.
        final_stress: the accumulated fragility at path end.
    """
    inputs: DCFInputs
    events: List[ShockEvent] = field(default_factory=list)
    final_stress: float = 0.0


# ============================================================
#  THE OVERLAY
# ============================================================
#  Walk the forecast year by year. Each year, each channel rolls
#  against its stress-adjusted hazard. A fired shock draws a
#  severity, applies channel-specific damage to the inputs, and
#  adds to the running stress (raising later years' odds).
# ============================================================


def _interp(band: Tuple[float, float], severity: float) -> float:
    """Linear interpolation: severity 0 -> floor, severity 1 -> ceiling."""
    floor, ceiling = band
    return floor + severity * (ceiling - floor)


def apply_shocks(
    inputs: DCFInputs,
    rng: np.random.Generator,
    *,
    enabled: bool = True,
    hazards: Optional[Dict[str, float]] = None,
    bands: Optional[Dict[str, Tuple[float, float]]] = None,
    stress_sensitivity: Optional[float] = None,
    fragility_weights: Optional[Dict[str, float]] = None,
) -> ShockOutcome:
    """Overlay discrete shocks on ONE already-perturbed DCFInputs.

    Walks each forecast year and rolls every channel against its current
    stress-adjusted hazard. Damage rides existing dials (revenue_growth,
    operating_margin, cost_of_debt, terminal_growth) except the cash channel,
    which accrues to net_debt. `inputs` is never mutated — a shocked copy is
    returned inside the ShockOutcome.

    `enabled=False` is the deterministic escape hatch: no shock can fire, the
    inputs come back untouched, and the result is identical to the pure step-3
    path. The smoke test uses it to prove the overlay adds nothing when off.

    The override args (hazards / bands / stress_sensitivity / fragility_weights)
    exist for calibration sweeps and for forcing shocks in tests; production
    runs leave them None and read mc_defaults.
    """
    if not enabled:
        return ShockOutcome(inputs=inputs, events=[], final_stress=0.0)

    # Resolve calibration: defaults unless this call overrides.
    hazards = hazards if hazards is not None else mc_defaults.BASE_HAZARDS
    bands = bands if bands is not None else mc_defaults.DAMAGE_BANDS
    sensitivity = (
        stress_sensitivity
        if stress_sensitivity is not None
        else mc_defaults.STRESS_SENSITIVITY
    )
    weights = (
        fragility_weights
        if fragility_weights is not None
        else mc_defaults.FRAGILITY_WEIGHTS
    )

    # Working copies of every dial a shock can touch. Lists are copied so the
    # caller's perturbed trajectory is never mutated in place.
    revenue_growth = list(inputs.revenue_growth)
    operating_margin = list(inputs.operating_margin)
    cost_of_debt = inputs.cost_of_debt
    terminal_growth = inputs.terminal_growth
    net_debt = inputs.net_debt

    # Revenue trajectory used ONLY to size the cash channel (a % of that year's
    # revenue). Computed once from the perturbed-but-not-yet-shocked inputs — a
    # V1 simplification: the cash hit is sized off the pre-shock revenue level,
    # not re-derived after each shock. Good enough for a placeholder layer.
    revenue_for_sizing = project_revenue(inputs)

    stress = 0.0
    events: List[ShockEvent] = []

    # forecast_years is the horizon; trajectories have exactly that length.
    for t in range(inputs.forecast_years):
        for channel in mc_defaults.SHOCK_CHANNELS:
            # Wounded paths are likelier to be hit again. Clamp at 1.0 so a very
            # fragile path can't exceed a certain hit.
            adjusted = hazards[channel] * (1.0 + sensitivity * stress)
            if adjusted > 1.0:
                adjusted = 1.0

            if rng.random() >= adjusted:
                continue  # no shock on this channel this year

            # A shock fires. Draw severity (uniform 0..1, the ignorance prior)
            # and interpolate the channel's damage magnitude.
            severity = rng.random()
            damage = _interp(bands[channel], severity)

            # --- Apply channel-specific damage (units differ per channel) ---
            if channel == "revenue":
                # Persistent haircut on the revenue LEVEL. Folding it into year
                # t's growth rate drops revenue[t] by `damage` and, because
                # later years compound off the lowered base, keeps it lower for
                # the rest of the horizon — the customer is gone for good.
                g = revenue_growth[t]
                revenue_growth[t] = (1.0 + g) * (1.0 - damage) - 1.0

            elif channel == "margin":
                # Persistent multiplicative compression from year t onward.
                for k in range(t, inputs.forecast_years):
                    operating_margin[k] *= (1.0 - damage)

            elif channel == "funding":
                # Relative increase in the cost of debt (feeds WACC, the
                # denominator). Scalar, so it applies to the whole valuation.
                cost_of_debt *= (1.0 + damage)

            elif channel == "strategic":
                # Relative reduction in terminal growth — permanent franchise
                # impairment. Small in absolute terms but moves value hard via
                # the terminal value.
                terminal_growth *= (1.0 - damage)

            elif channel == "cash":
                # One-off cash outflow, sized as a % of that year's revenue.
                # No bottom-up FCF slot exists, so it accrues to net_debt
                # (reducing equity value at the bridge). V1 applies it
                # undiscounted — a documented simplification; PV-ing it at WACC
                # is a later refinement.
                net_debt += damage * revenue_for_sizing[t]

            # The wound: add to stress (equal weight in V1), raising later odds.
            stress += weights[channel] * severity
            events.append(
                ShockEvent(year=t + 1, channel=channel, severity=severity, damage=damage)
            )

            # NOTE (V2 healing): a quiet-year decay of `stress` would go in the
            # per-year scope, just outside this channel loop. Omitted in V1 so
            # the un-healed run is the upper bound on cascade frequency.

    shocked = replace(
        inputs,
        revenue_growth=revenue_growth,
        operating_margin=operating_margin,
        cost_of_debt=cost_of_debt,
        terminal_growth=terminal_growth,
        net_debt=net_debt,
    )
    return ShockOutcome(inputs=shocked, events=events, final_stress=stress)


# ============================================================
#  THE SHOCKED SAMPLER + RUNNER
# ============================================================
#  Perturb-then-shock for one path, and the n-loop that collects
#  the shocked distribution. Mirrors mc_engine.run_monte_carlo;
#  reuses run_dcf and sample_inputs untouched.
# ============================================================


def sample_inputs_with_shocks(
    base: DCFInputs,
    config: MCConfig,
    rng: np.random.Generator,
    *,
    enabled: bool = True,
) -> ShockOutcome:
    """One path: step-3 perturbation FIRST, then shocks on top.

    The ordering is the locked design — shocks must land on the perturbed
    trajectory so an already-weak path takes a heavier blow than a strong one.
    """
    perturbed = sample_inputs(base, config, rng)
    return apply_shocks(perturbed, rng, enabled=enabled)


def run_monte_carlo_with_shocks(
    base: DCFInputs,
    config: MCConfig,
    *,
    enabled: bool = True,
) -> List[float]:
    """Run `config.n_simulations` perturbed-and-shocked DCF valuations.

    Identical in spirit to mc_engine.run_monte_carlo, but each path also gets
    the shock overlay. One seeded generator threads through every path, so
    same seed + same inputs => identical distribution. Returns the list of
    per-share values — the shocked distribution. Step 6 (convergence round two)
    will call this at varying n to find the post-shock sample size z**.

    `enabled=False` reduces this to the pure continuous-only run, which is how
    the smoke test proves the overlay is a clean add-on.
    """
    rng = np.random.default_rng(config.random_seed)
    return [
        run_dcf(sample_inputs_with_shocks(base, config, rng, enabled=enabled).inputs)
        for _ in range(config.n_simulations)
    ]
