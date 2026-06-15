"""
Chunked, resumable driver for the MSFT seed-robustness sweeps.

Mirrors case_study_runner.stage_seed exactly (same convergence calls, same seeds,
rerun=False), but wraps the runner in a disk memo so each <45s call resumes from
cache. Cache is namespaced per engine ('cont' vs 'shock') because the two engines
share (n, seed) keys but produce different draws. No engine/convergence/grid/
shock-calibration logic is modified — only run scheduling.

Usage:  python3 msft_seed_driver.py <cont|shock> <seed> [budget_secs]
"""

# --- engine path bootstrap (auto-added during reorg; frozen engine lives in ../engine) ---
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "engine"))
# --- end bootstrap ---
import os, sys, time
import numpy as np

from mc_config import MCConfig
from mc_engine import run_monte_carlo
from mc_shocks import run_monte_carlo_with_shocks
from mc_convergence import convergence_with_recommendation
from case_study_runner import get_base, load, save

which = sys.argv[1]          # 'cont' or 'shock'
seed = int(sys.argv[2])
BUDGET = float(sys.argv[3]) if len(sys.argv) > 3 else 40.0
START = time.time()

CACHE = f"msft_seed_cache_v2/{which}_{seed}"
os.makedirs(CACHE, exist_ok=True)
ENGINE = run_monte_carlo if which == "cont" else run_monte_carlo_with_shocks


def memo_runner(base, cfg):
    key = f"{cfg.n_simulations}_{cfg.random_seed}.npy"
    path = os.path.join(CACHE, key)
    if os.path.exists(path):
        return np.load(path)
    if time.time() - START > BUDGET:
        raise TimeoutError("budget exhausted; resume next call")
    res = np.asarray(ENGINE(base, cfg))
    np.save(path, res)
    return res


def main():
    base = get_base("msft")
    cfg = MCConfig(n_simulations=0, random_seed=seed)
    try:
        r = convergence_with_recommendation(
            base, config=cfg, rerun=False, runner=memo_runner
        )
    except TimeoutError as e:
        print("PARTIAL:", e, "cached:", len(os.listdir(CACHE)))
        return

    d = load("msft")
    rec = d.setdefault("seeds", {}).setdefault(str(seed), {})
    if which == "cont":
        rec.update(cont_z=r.z_star, cont_batches=r.final_recommendation,
                   cont_margin=r.default.decision_margin_pct, cont_zpct=r.default.z_pct)
        print(f"DONE seed {seed} cont z*={r.z_star} batches={r.final_recommendation} "
              f"margin={r.default.decision_margin_pct:.1f}")
    else:
        rec.update(shock_z=r.z_star, shock_batches=r.final_recommendation,
                   shock_margin=r.default.decision_margin_pct, shock_zpct=r.default.z_pct)
        print(f"DONE seed {seed} shock z**={r.z_star} batches={r.final_recommendation} "
              f"margin={r.default.decision_margin_pct:.1f}")
    save("msft", d)


if __name__ == "__main__":
    main()
