"""
Case-Study Runner — one identical pipeline for every stress-test candidate
==========================================================================

The engine is general-purpose; companies are case studies. This runner is the
canonical tool for putting any candidate through the SAME staged pipeline that
Candidate #1 (Carvana) went through, so every company's outputs are directly
comparable and every chat produces an identically-structured results file.

Each candidate is a FIXTURE for architecture exploration, NOT an investment
call. Outputs are case-study observations, never architecture truths.

------------------------------------------------------------------
HOW TO RUN A NEW CANDIDATE (do this in its own chat)
------------------------------------------------------------------
1. Add the company's inputs to the CANDIDATES dict below (or pass a JSON
   fixture file with --fixture). Give it a short slug, e.g. "candidate2".
2. Run the stages (each convergence sweep is ~30-45s, so they are split to
   fit one shell call apiece):

       python3 case_study_runner.py central   <slug>
       python3 case_study_runner.py cont      <slug>
       python3 case_study_runner.py shock     <slug>
       python3 case_study_runner.py seed42    <slug>
       python3 case_study_runner.py seedc:99  <slug>
       python3 case_study_runner.py seedk:99  <slug>
       python3 case_study_runner.py seedc:123 <slug>
       python3 case_study_runner.py seedk:123 <slug>
       python3 case_study_runner.py seedc:7   <slug>
       python3 case_study_runner.py seedk:7   <slug>
       python3 case_study_runner.py dump      <slug>     # prints everything

   Results accrue in <slug>_results.json.
3. Write the per-candidate research log (Candidate_N_<Name>.md) from that JSON,
   using Candidate_1_Carvana.md as the template (same section order).
4. Add a row to STRESS_TEST_TRACKER.md and fold any architecture-level finding
   into that doc's findings ledger.
------------------------------------------------------------------
"""

# --- engine path bootstrap (auto-added during reorg; frozen engine lives in ../engine) ---
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "engine"))
# --- end bootstrap ---

import sys
import json
import time
import numpy as np

from dcf import DCFInputs, run_dcf, compute_wacc
from mc_config import MCConfig
from mc_engine import run_monte_carlo, summarize, text_histogram
from mc_shocks import run_monte_carlo_with_shocks, sample_inputs_with_shocks
from mc_convergence import (
    convergence_with_recommendation,
    convergence_with_shocks,
    benchmark_against_folk,
)
import mc_defaults

SEED = 42


# ------------------------------------------------------------------
#  FIXTURE REGISTRY  — add new candidates here
# ------------------------------------------------------------------
CANDIDATES = {
    "steady_co": DCFInputs(
        starting_revenue=1000, net_debt=300, shares_outstanding=100, forecast_years=5,
        revenue_growth=[0.10, 0.08, 0.06, 0.05, 0.04], operating_margin=[0.15] * 5,
        capex_pct_revenue=[0.07] * 5, da_pct_revenue=[0.05] * 5, nwc_pct_revenue=[0.02] * 5,
        tax_rate=0.25, terminal_growth=0.025, risk_free_rate=0.04,
        equity_risk_premium=0.055, beta=1.1, cost_of_debt=0.05, debt_to_total_capital=0.30,
    ),
    "candidate1": DCFInputs(  # Carvana-inspired fragile fixture
        starting_revenue=20300, net_debt=5000, shares_outstanding=220, forecast_years=5,
        revenue_growth=[0.20, 0.15, 0.10, 0.06, 0.04],
        operating_margin=[0.04, 0.05, 0.06, 0.07, 0.08],
        capex_pct_revenue=[0.03] * 5, da_pct_revenue=[0.015] * 5, nwc_pct_revenue=[0.03] * 5,
        tax_rate=0.25, terminal_growth=0.025, risk_free_rate=0.04,
        equity_risk_premium=0.055, beta=2.2, cost_of_debt=0.085, debt_to_total_capital=0.55,
    ),
    "candidate2": DCFInputs(  # Rivian-inspired fragile fixture (early losses, positive ramp)
        starting_revenue=5500, net_debt=1000, shares_outstanding=1200, forecast_years=5,
        revenue_growth=[0.35, 0.30, 0.25, 0.18, 0.12],
        operating_margin=[-0.12, -0.05, 0.01, 0.05, 0.08],
        capex_pct_revenue=[0.10, 0.09, 0.08, 0.07, 0.06],
        da_pct_revenue=[0.04] * 5, nwc_pct_revenue=[0.03] * 5,
        tax_rate=0.25, terminal_growth=0.025, risk_free_rate=0.04,
        equity_risk_premium=0.055, beta=2.0, cost_of_debt=0.07, debt_to_total_capital=0.25,
    ),
    "candidate3": DCFInputs(  # CloudGrow — boundary-crossing test: positive-centre fragile
        # High beta (1.9), thin early margins (5% ramping to 13%), elevated cost of debt (6.5%)
        # but revenues are modest ($3bn) and net debt is manageable ($500m on 500m shares).
        # Designed to sit on the positive side of the valuation zero boundary while remaining
        # genuinely fragile — the critical test for whether B1/B2 are negative-centre phenomena.
        starting_revenue=3000, net_debt=500, shares_outstanding=500, forecast_years=5,
        revenue_growth=[0.25, 0.22, 0.18, 0.14, 0.10],
        operating_margin=[0.05, 0.07, 0.09, 0.11, 0.13],
        capex_pct_revenue=[0.04] * 5, da_pct_revenue=[0.03] * 5, nwc_pct_revenue=[0.02] * 5,
        tax_rate=0.25, terminal_growth=0.025, risk_free_rate=0.04,
        equity_risk_premium=0.055, beta=1.9, cost_of_debt=0.065, debt_to_total_capital=0.20,
    ),
    "candidate4b": DCFInputs(  # MedTechX — second positive-centre fragile fixture (beta 2.4, WACC ~15%)
        # High-growth MedTech: revenue $4bn, net_debt only $300m on 400m shares (low leverage).
        # Strong revenue ramp (28%→10%) with thin but positive margins (6%→14%).
        # Beta 2.4 produces a very high WACC (~15%) — the highest of any positive-centre candidate.
        # Designed to test F8 reproduction (thin shocked margin), z**>z* at higher sigma,
        # and whether low leverage kills cash-channel dominance.
        starting_revenue=4000, net_debt=300, shares_outstanding=400, forecast_years=5,
        revenue_growth=[0.28, 0.24, 0.20, 0.15, 0.10],
        operating_margin=[0.06, 0.08, 0.10, 0.12, 0.14],
        capex_pct_revenue=[0.05] * 5, da_pct_revenue=[0.03] * 5, nwc_pct_revenue=[0.03] * 5,
        tax_rate=0.25, terminal_growth=0.025, risk_free_rate=0.04,
        equity_risk_premium=0.055, beta=2.4, cost_of_debt=0.065, debt_to_total_capital=0.18,
    ),
    "candidate5": DCFInputs(  # RetailRollup — boundary-testing: high-revenue/equity, positive-centre fragile
        # High revenue ($18bn) on thin share count (250m) and $2.5bn net debt.
        # Margin ramp 9%→13%, moderate growth 12%→4%, beta 2.2, WACC ~12.78%.
        # Designed to push revenue/equity ratio further than CloudGrow/MedTechX
        # and test whether cash becomes the dominant worst-5% channel for a
        # positive-centre company. Primary question: does cash dominate as F4 predicts?
        starting_revenue=18000, net_debt=2500, shares_outstanding=250, forecast_years=5,
        revenue_growth=[0.12, 0.10, 0.08, 0.06, 0.04],
        operating_margin=[0.09, 0.10, 0.11, 0.12, 0.13],
        capex_pct_revenue=[0.06, 0.06, 0.05, 0.05, 0.05],
        da_pct_revenue=[0.03, 0.03, 0.03, 0.03, 0.03],
        nwc_pct_revenue=[0.03, 0.03, 0.03, 0.03, 0.03],
        tax_rate=0.25, terminal_growth=0.025, risk_free_rate=0.04,
        equity_risk_premium=0.055, beta=2.2, cost_of_debt=0.07, debt_to_total_capital=0.30,
    ),
    "candidate8b": DCFInputs(  # ThinEquity (C8B) — leverage-driven CV amplification, calibrated
        # LeveragedRetail (C8) operating template with net_debt calibrated to EV breakeven.
        # C8 failed gate (net_debt $21,000 > EV $17,682). C8B sets net_debt=$16,000 (91% of EV),
        # giving equity cushion $1,682M (9.51% of EV), central value $8.41/share.
        # Same D/V=0.75 / cod=7.5% / shares=200 / all operating inputs as C8.
        # Sigma survey shows sigma=$31.48/share FIXED, mean=$7.51, CV=419% at net_debt=16,000.
        # CV > 100% guarantees n_true >> 10,000 — grid saturation expected.
        # Primary question: does leverage-driven CV amplification produce z* > 10,000?
        starting_revenue=18000, net_debt=16000, shares_outstanding=200, forecast_years=5,
        revenue_growth=[0.12, 0.10, 0.08, 0.06, 0.04],
        operating_margin=[0.09, 0.10, 0.11, 0.12, 0.13],
        capex_pct_revenue=[0.06, 0.06, 0.05, 0.05, 0.05],
        da_pct_revenue=[0.03, 0.03, 0.03, 0.03, 0.03],
        nwc_pct_revenue=[0.03, 0.03, 0.03, 0.03, 0.03],
        tax_rate=0.25, terminal_growth=0.025, risk_free_rate=0.04,
        equity_risk_premium=0.055, beta=2.2, cost_of_debt=0.075, debt_to_total_capital=0.75,
    ),
    "candidate6": DCFInputs(  # Project Doom — convergence stress test (beta 4.0)
        # Extreme beta (4.0) producing WACC ~21.4% — the highest of any candidate.
        # Hyper-growth (60%→15%) with very thin early margins (1%→12%).
        # Small revenue base ($1.5bn) on a thin share count (50m), light net debt ($100m).
        # Designed to push z* and z** to the top of N_GRID and test whether the current
        # grid is sufficient to resolve convergence. Primary question: does the architecture
        # recognise when the grid itself becomes the binding constraint?
        starting_revenue=1500, net_debt=100, shares_outstanding=50, forecast_years=5,
        revenue_growth=[0.60, 0.45, 0.35, 0.25, 0.15],
        operating_margin=[0.01, 0.03, 0.05, 0.08, 0.12],
        capex_pct_revenue=[0.08, 0.08, 0.07, 0.06, 0.05],
        da_pct_revenue=[0.02, 0.02, 0.02, 0.02, 0.02],
        nwc_pct_revenue=[0.06, 0.06, 0.06, 0.05, 0.05],
        tax_rate=0.25, terminal_growth=0.025, risk_free_rate=0.04,
        equity_risk_premium=0.055, beta=4.0, cost_of_debt=0.10, debt_to_total_capital=0.25,
    ),
    "candidate8": DCFInputs(  # LeveragedRetail — leverage-driven CV amplification test
        # RetailRollup operating template (same revenue profile, margins, capex, D&A, NWC)
        # with capital structure dramatically altered: net_debt raised to $21,000M (from $2,500M),
        # shares_outstanding cut to 200M (from 250M), debt_to_total_capital raised to 0.75,
        # beta raised to 2.2 (unchanged), cost_of_debt raised to 7.5%.
        # Primary question: can a legitimate positive-centre company produce z* > 10,000
        # via leverage-driven CV amplification through the equity bridge?
        # The equity value = EV - net_debt is thin on a 200M share count;
        # small EV perturbations translate to very large per-share swings (high CV).
        starting_revenue=18000, net_debt=21000, shares_outstanding=200, forecast_years=5,
        revenue_growth=[0.12, 0.10, 0.08, 0.06, 0.04],
        operating_margin=[0.09, 0.10, 0.11, 0.12, 0.13],
        capex_pct_revenue=[0.06, 0.06, 0.05, 0.05, 0.05],
        da_pct_revenue=[0.03, 0.03, 0.03, 0.03, 0.03],
        nwc_pct_revenue=[0.03, 0.03, 0.03, 0.03, 0.03],
        tax_rate=0.25, terminal_growth=0.025, risk_free_rate=0.04,
        equity_risk_premium=0.055, beta=2.2, cost_of_debt=0.075, debt_to_total_capital=0.75,
    ),
    "candidate4": DCFInputs(  # PowerGridCo — second positive-centre fragile fixture
        # High beta (1.8), elevated capex (12% declining to 8%), thin early margins (8% to 12%).
        # Large revenue ($12bn) on a thin share count (350m) creates a high revenue/equity ratio.
        # Heavy debt ($7bn net debt, 45% D/V). Designed to test: F8 reproduction, z**>z*,
        # cash-channel dominance on a positive-centre company, revenue/equity ratio mechanism.
        starting_revenue=12000, net_debt=7000, shares_outstanding=350, forecast_years=5,
        revenue_growth=[0.10, 0.08, 0.07, 0.05, 0.04],
        operating_margin=[0.08, 0.09, 0.10, 0.11, 0.12],
        capex_pct_revenue=[0.12, 0.11, 0.10, 0.09, 0.08],
        da_pct_revenue=[0.05] * 5, nwc_pct_revenue=[0.03] * 5,
        tax_rate=0.25, terminal_growth=0.025, risk_free_rate=0.04,
        equity_risk_premium=0.055, beta=1.8, cost_of_debt=0.08, debt_to_total_capital=0.45,
    ),
}


def get_base(slug):
    """Resolve a candidate fixture by slug, or load it from <slug>_fixture.json."""
    if slug in CANDIDATES:
        return CANDIDATES[slug]
    try:
        with open(f"{slug}_fixture.json") as f:
            return DCFInputs(**json.load(f))
    except FileNotFoundError:
        raise SystemExit(
            f"Unknown candidate '{slug}'. Add it to CANDIDATES in "
            f"case_study_runner.py, or create {slug}_fixture.json."
        )


def results_path(slug):
    return f"{slug}_results.json"


def load(slug):
    try:
        with open(results_path(slug)) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save(slug, d):
    with open(results_path(slug), "w") as f:
        json.dump(d, f, indent=2)


def summ_dict(s):
    return {"n": s.n, "mean": s.mean, "median": s.median, "std": s.std,
            "min": s.minimum, "max": s.maximum,
            "pct": {str(k): v for k, v in s.percentiles.items()}}


def pair_dict(p):
    d = p.default
    return {"z_star": p.z_star, "z_star_moved": p.z_star_moved,
            "adequately_resolved": p.adequately_resolved,
            "final_recommendation": p.final_recommendation,
            "refinement_capped": p.refinement_capped,
            "z_pct": d.z_pct, "z_elbow": d.z_elbow,
            "decision_margin_pct": d.decision_margin_pct,
            "precision_bar": d.precision_bar, "sigma_estimate": d.sigma_estimate,
            "center_mean": float(np.mean(d.center)), "borderline": d.borderline,
            "batches_used": d.batches_used, "batches_recommended": d.batches_recommended,
            "scatter": d.scatter, "n_grid": d.n_grid}


# ------------------------------------------------------------------
#  STAGES
# ------------------------------------------------------------------
def stage_central(d, base):
    d["central"] = {"value": run_dcf(base), "wacc": compute_wacc(base)}
    print("central:", d["central"])


def stage_cont(d, base):
    t = time.time()
    cont = convergence_with_recommendation(base, rerun=False)
    z = cont.z_star
    res = run_monte_carlo(base, MCConfig(n_simulations=z, random_seed=SEED))
    arr = np.asarray(res)
    bench = benchmark_against_folk(base, cont, folk_n=10_000, seed=SEED)
    d["cont"] = {
        "pair": pair_dict(cont),
        "production": summ_dict(summarize(res)),
        "frac_negative_pct": float(100.0 * np.mean(arr < 0)),
        "histogram": text_histogram(res, bins=20, width=42),
        "benchmark": {"z_star": bench.z_star, "folk_n": bench.folk_n,
                      "compute_ratio": bench.compute_ratio, "mean_gap_pct": bench.mean_gap_pct,
                      "z_mean": bench.z_summary.mean, "folk_mean": bench.folk_summary.mean,
                      "z_median": bench.z_summary.median, "folk_median": bench.folk_summary.median},
        "secs": time.time() - t,
    }
    print(f"cont z*={z} margin%={cont.default.decision_margin_pct:.2f} "
          f"z_pct={cont.default.z_pct} frac_neg={d['cont']['frac_negative_pct']:.1f}% "
          f"in {d['cont']['secs']:.1f}s")


def stage_shock(d, base):
    t = time.time()
    shock = convergence_with_shocks(base, rerun=False)
    z = shock.z_star
    res = run_monte_carlo_with_shocks(base, MCConfig(n_simulations=z, random_seed=SEED))
    arr = np.asarray(res)
    cfg = MCConfig(n_simulations=5000, random_seed=SEED)
    rng = np.random.default_rng(cfg.random_seed)
    rows = []
    for _ in range(cfg.n_simulations):
        oc = sample_inputs_with_shocks(base, cfg, rng, enabled=True)
        rows.append((run_dcf(oc.inputs), oc))
    fires = {ch: 0 for ch in mc_defaults.SHOCK_CHANNELS}
    stresses = []
    for _, oc in rows:
        stresses.append(oc.final_stress)
        for ev in oc.events:
            fires[ev.channel] += 1
    any_paths = sum(1 for _, oc in rows if oc.events)
    worst = sorted(rows, key=lambda r: r[0])[: max(1, len(rows) // 20)]
    wfires = {ch: 0 for ch in mc_defaults.SHOCK_CHANNELS}
    for _, oc in worst:
        for ev in oc.events:
            wfires[ev.channel] += 1
    grid = {str(p): float(100.0 * np.mean(arr < p)) for p in (-5, -2, 0, 2, 5, 8, 11, 15)}
    d["shock"] = {
        "pair": pair_dict(shock),
        "production": summ_dict(summarize(res)),
        "frac_negative_pct": float(100.0 * np.mean(arr < 0)),
        "histogram": text_histogram(res, bins=20, width=42),
        "shock_free_pct": float(100.0 * (1 - any_paths / len(rows))),
        "fires_all": fires, "fires_worst5": wfires,
        "mean_stress": float(np.mean(stresses)), "max_stress": float(np.max(stresses)),
        "total_fires": int(sum(fires.values())), "market_grid": grid,
        "secs": time.time() - t,
    }
    print(f"shock z**={z} margin%={shock.default.decision_margin_pct:.2f} "
          f"z_pct={shock.default.z_pct} frac_neg={d['shock']['frac_negative_pct']:.1f}% "
          f"shock_free={d['shock']['shock_free_pct']:.1f}% in {d['shock']['secs']:.1f}s")


def stage_seed(d, base, seed, which):
    t = time.time()
    cfg = MCConfig(n_simulations=0, random_seed=seed)
    rec = d.setdefault("seeds", {}).setdefault(str(seed), {})
    if which == "cont":
        c = convergence_with_recommendation(base, config=cfg, rerun=False)
        rec.update(cont_z=c.z_star, cont_batches=c.final_recommendation,
                   cont_margin=c.default.decision_margin_pct, cont_zpct=c.default.z_pct)
        print(f"seed {seed} cont z*={c.z_star} margin={c.default.decision_margin_pct:.1f} "
              f"in {time.time()-t:.1f}s")
    else:
        s = convergence_with_shocks(base, config=cfg, rerun=False)
        rec.update(shock_z=s.z_star, shock_batches=s.final_recommendation,
                   shock_margin=s.default.decision_margin_pct, shock_zpct=s.default.z_pct)
        print(f"seed {seed} shock z**={s.z_star} margin={s.default.decision_margin_pct:.1f} "
              f"in {time.time()-t:.1f}s")


def main():
    if len(sys.argv) < 3:
        raise SystemExit("usage: python3 case_study_runner.py <stage> <slug>")
    stage, slug = sys.argv[1], sys.argv[2]
    d = load(slug)
    if stage == "dump":
        print(json.dumps(d, indent=2))
        return
    base = get_base(slug)
    if stage == "central":
        stage_central(d, base)
    elif stage == "cont":
        stage_cont(d, base)
    elif stage == "shock":
        stage_shock(d, base)
    elif stage == "seed42":
        d.setdefault("seeds", {})["42"] = {
            "cont_z": d["cont"]["pair"]["z_star"], "cont_batches": d["cont"]["pair"]["final_recommendation"],
            "cont_margin": d["cont"]["pair"]["decision_margin_pct"], "cont_zpct": d["cont"]["pair"]["z_pct"],
            "shock_z": d["shock"]["pair"]["z_star"], "shock_batches": d["shock"]["pair"]["final_recommendation"],
            "shock_margin": d["shock"]["pair"]["decision_margin_pct"], "shock_zpct": d["shock"]["pair"]["z_pct"]}
        print("seed42 recorded from cont/shock stages")
    elif stage.startswith("seedc:"):
        stage_seed(d, base, int(stage.split(":")[1]), "cont")
    elif stage.startswith("seedk:"):
        stage_seed(d, base, int(stage.split(":")[1]), "shock")
    else:
        raise SystemExit(f"unknown stage '{stage}'")
    save(slug, d)


if __name__ == "__main__":
    main()
