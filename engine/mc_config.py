"""
Monte Carlo Configuration
==========================

Per-run knobs for the Monte Carlo machinery. Kept deliberately small:
the four step-3 design conversations locked the architecture (which
dials wiggle, what distribution shapes, correlation pairs, sampling
structure), so the USER of one MC run only specifies how many
simulations to run and the random seed for reproducibility.

For calibration experiments — tuning a width or a correlation per-run
without permanently editing `mc_defaults.py` — pass override dicts.
The runner reads each setting via `overrides.get(key, defaults.KEY)`
so an override transparently takes precedence.

The common-case call:

    config = MCConfig(n_simulations=10000)
    results = run_monte_carlo(base_inputs, config)

Calibration sweep — widen the trajectory perturbation for this run:

    config = MCConfig(
        n_simulations=10000,
        width_overrides={"trajectory": 0.15},
    )

Reproducibility — pin the seed so repeated runs match exactly:

    config = MCConfig(n_simulations=10000, random_seed=42)
"""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple


@dataclass
class MCConfig:
    """Per-run configuration for the Monte Carlo machinery.

    Holds ONLY the things that vary per run, not per design. The locked
    design (which dials wiggle, distribution shapes, correlation pairs,
    sampling structure) lives in `mc_defaults.py` so callers don't have
    to re-specify decisions already made.

    Step 4 of the build (convergence analysis) sweeps `n_simulations`
    to find the empirical elbow — so this field MUST be a per-run knob,
    not a constant. Everything else here is optional escape-hatch
    territory for calibration experiments.

    Fields:
        n_simulations:
            How many DCF runs to execute. Required. Step 4 sweeps this
            value to locate the per-company convergence elbow (z*).

        random_seed:
            Optional integer seed for reproducibility. When set, repeated
            runs with identical inputs produce identical output. When
            None (default), each call is nondeterministic — useful for
            production runs where you want a fresh draw, painful for
            debugging where you want to reproduce a specific scatter.

        width_overrides:
            Optional {name: float} dict overriding specific widths from
            mc_defaults.py for this run only. Supported keys:
                "trajectory"      — overrides TRAJECTORY_WIDTH
                "per_year_noise"  — overrides PER_YEAR_NOISE_WIDTH
            Unrecognised keys are ignored by the runner. Defaults to
            None, meaning "use everything from mc_defaults.py".

        correlation_overrides:
            Optional {(dial_a, dial_b): float} dict overriding specific
            correlations from mc_defaults.py for this run only. Tuples
            should be sorted alphabetically to match the keys in
            mc_defaults.CORRELATIONS. Defaults to None.

    Validation deferred to step 7 of the build sequence (same principle
    as DCFInputs). Math first, validation later — comprehensively.
    """

    n_simulations: int
    random_seed: Optional[int] = None
    width_overrides: Optional[Dict[str, float]] = None
    correlation_overrides: Optional[Dict[Tuple[str, str], float]] = None
