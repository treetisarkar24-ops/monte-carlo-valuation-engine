"""
Chunked seed-shock driver for NVIDIA.

Runs convergence_with_shocks for seeds [99, 123, 7], each in its own
cache directory, and writes shock_z/shock_batches/shock_margin/shock_zpct
into nvda_results.json["seeds"][seed].

Run repeatedly until all three seeds show DONE.
"""

# --- engine path bootstrap (auto-added during reorg; frozen engine lives in ../engine) ---
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "engine"))
# --- end bootstrap ---
import os, sys, time, json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mc_config import MCConfig
from mc_shocks import run_monte_carlo_with_shocks
from mc_convergence import convergence_with_recommendation
from case_study_runner import get_base, load, save

BUDGET = float(sys.argv[1]) if len(sys.argv) > 1 else 38.0
START = time.time()
SEEDS = [99, 123, 7]


def make_memo_runner(cache_dir):
    os.makedirs(cache_dir, exist_ok=True)

    def memo_runner(base, cfg):
        key = f"{cfg.n_simulations}_{cfg.random_seed}.npy"
        path = os.path.join(cache_dir, key)
        if os.path.exists(path):
            return np.load(path)
        if time.time() - START > BUDGET:
            raise TimeoutError("budget exhausted")
        res = np.asarray(run_monte_carlo_with_shocks(base, cfg))
        np.save(path, res)
        return res

    return memo_runner


def main():
    slug = "nvda"
    base = get_base(slug)
    d = load(slug)
    seeds_done = []

    for seed in SEEDS:
        rec = d.setdefault("seeds", {}).setdefault(str(seed), {})
        if "shock_z" in rec:
            seeds_done.append(seed)
            continue  # already complete

        cache_dir = f"nvda_shock_seed_{seed}"
        runner = make_memo_runner(cache_dir)
        cfg = MCConfig(n_simulations=0, random_seed=seed)

        try:
            t = time.time()
            s = convergence_with_recommendation(
                base, config=cfg, rerun=False, runner=runner
            )
            rec.update(
                shock_z=s.z_star,
                shock_batches=s.final_recommendation,
                shock_margin=s.default.decision_margin_pct,
                shock_zpct=s.default.z_pct,
            )
            save(slug, d)
            elapsed = time.time() - t
            print(f"seed {seed} shock z**={s.z_star} "
                  f"margin={s.default.decision_margin_pct:.1f} in {elapsed:.1f}s")
            seeds_done.append(seed)
        except TimeoutError as e:
            cached = len(os.listdir(cache_dir))
            print(f"seed {seed} PARTIAL: {e} ({cached} cached)")
            save(slug, d)
            return  # exit; next call resumes from cache

    print(f"All seeds done: {seeds_done}")


if __name__ == "__main__":
    main()
