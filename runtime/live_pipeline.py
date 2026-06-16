#!/usr/bin/env python3
"""
live_pipeline.py — run the FULL engine for an arbitrary company and assemble the
exact results.json + meta.json shapes that build_pdf_report.py and
build_excel_output.py consume.

This is the front-door equivalent of case_study_runner.py, but packaged so the
Streamlit app (or any caller) can run a complete valuation in one call:
continuous convergence (z*), production at z*, benchmark vs the folk 10,000,
shocked convergence (z**), shocked production, and shock-channel behaviour.

Presentation/orchestration layer only. It imports the frozen engine read-only
and modifies no DCF / Monte Carlo / shock / convergence logic.

For built-in case studies (Amazon, Coca-Cola) we ship hand-authored meta with
bespoke narrative. For arbitrary uploads, build_templated_meta() produces the
SAME report structure with data-driven, templated prose (no bespoke essay).
"""
from __future__ import annotations

import os as _os, sys as _sys
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "engine"))

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


# ---------------------------------------------------------------- serialisers
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


# ---------------------------------------------------------------- the full run
def run_full(base: DCFInputs, *, seed: int = SEED, do_shock: bool = True,
             progress=None) -> dict:
    """Run the complete pipeline and return a results dict (results.json shape).

    `progress(msg, frac)` is an optional callback so a UI can show stages.
    """
    def step(msg, frac):
        if progress:
            progress(msg, frac)

    d = {}

    # --- central deterministic case ---
    step("Deterministic DCF…", 0.05)
    d["central"] = {"value": run_dcf(base), "wacc": compute_wacc(base)}

    # --- continuous Monte Carlo (z*) ---
    step("Continuous convergence (z*)…", 0.15)
    t = time.time()
    cont = convergence_with_recommendation(base, config=MCConfig(n_simulations=0, random_seed=seed),
                                           rerun=False)
    z = cont.z_star
    step(f"Continuous production at z*={z:,}…", 0.40)
    res = run_monte_carlo(base, MCConfig(n_simulations=z, random_seed=seed))
    arr = np.asarray(res)
    step("Benchmarking vs the folk 10,000…", 0.55)
    bench = benchmark_against_folk(base, cont, folk_n=10_000, seed=seed)
    d["cont"] = {
        "pair": pair_dict(cont),
        "production": summ_dict(summarize(res)),
        "frac_negative_pct": float(100.0 * np.mean(arr < 0)),
        "histogram": text_histogram(res, bins=20, width=42),
        "benchmark": {"z_star": bench.z_star, "folk_n": bench.folk_n,
                      "compute_ratio": bench.compute_ratio,
                      "mean_gap_pct": bench.mean_gap_pct,
                      "z_mean": bench.z_summary.mean, "folk_mean": bench.folk_summary.mean,
                      "z_median": bench.z_summary.median,
                      "folk_median": bench.folk_summary.median},
        "secs": time.time() - t,
        "samples": arr.tolist(),
    }

    # --- shocked Monte Carlo (z**) ---
    if do_shock:
        step("Shocked convergence (z**)…", 0.65)
        t = time.time()
        shock = convergence_with_shocks(base, config=MCConfig(n_simulations=0, random_seed=seed),
                                        rerun=False)
        zz = shock.z_star
        step(f"Shocked production at z**={zz:,}…", 0.85)
        sres = run_monte_carlo_with_shocks(base, MCConfig(n_simulations=zz, random_seed=seed))
        sarr = np.asarray(sres)
        # channel behaviour (5,000-path probe, matches case_study_runner)
        cfg = MCConfig(n_simulations=5000, random_seed=seed)
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
        grid = {str(p): float(100.0 * np.mean(sarr < p)) for p in (-5, -2, 0, 2, 5, 8, 11, 15)}
        d["shock"] = {
            "pair": pair_dict(shock),
            "production": summ_dict(summarize(sres)),
            "frac_negative_pct": float(100.0 * np.mean(sarr < 0)),
            "histogram": text_histogram(sres, bins=20, width=42),
            "shock_free_pct": float(100.0 * (1 - any_paths / len(rows))),
            "fires_all": fires, "fires_worst5": wfires,
            "mean_stress": float(np.mean(stresses)), "max_stress": float(np.max(stresses)),
            "total_fires": int(sum(fires.values())), "market_grid": grid,
            "secs": time.time() - t,
            "samples": sarr.tolist(),
        }

    step("Done.", 1.0)
    return d


# ---------------------------------------------------------------- templated meta
def _pct(x, dp=1):
    return f"{x:.{dp}f}%"


def _f2(x):
    return f"${x:,.2f}"


def build_templated_meta(base: DCFInputs, results: dict, *, company: str,
                         ticker: str, market_price: float, market_date: str = "",
                         base_year=None, fixture_rel: str | None = None) -> dict:
    """Assemble a meta dict with DATA-DRIVEN templated prose for an arbitrary
    company. Same structure as the hand-authored Amazon meta, but every
    narrative string is generated from the fixture + results — no bespoke essay.
    """
    central = results["central"]
    cont = results["cont"]
    shock = results.get("shock", {})
    cprod = cont["production"]
    val = central["value"]
    wacc = central["wacc"]

    # ---- assumptions table (auto from the fixture) ----
    g = base.revenue_growth
    om = base.operating_margin
    assumptions = [
        ["Starting revenue", f"${base.starting_revenue:,.0f}", "Most recent reported annual revenue (fixture units, USD millions)."],
        ["Net debt", f"${base.net_debt:,.0f}", "Total debt less cash & equivalents at the base date."],
        ["Shares outstanding", f"{base.shares_outstanding:,.0f}", "Diluted share count used for the per-share bridge."],
        ["Forecast years", f"{base.forecast_years}", "Length of the explicit forecast window before terminal value."],
        ["Revenue growth", f"{g[0]*100:.1f}% → {g[-1]*100:.1f}%", "Year-1 growth fading to the final explicit year."],
        ["Operating margin", f"{om[0]*100:.1f}% → {om[-1]*100:.1f}%", "Operating margin path across the forecast window."],
        ["Tax rate", _pct(base.tax_rate*100), "Effective cash tax rate applied to EBIT."],
        ["Terminal growth", _pct(base.terminal_growth*100), "Perpetuity growth beyond the explicit window."],
        ["Beta", f"{base.beta:.2f}", "Equity beta driving the cost of equity in WACC."],
        ["Cost of debt", _pct(base.cost_of_debt*100), "Pre-tax cost of debt."],
        ["Debt / total capital", _pct(base.debt_to_total_capital*100), "Capital-structure weight on debt in WACC."],
    ]

    caveat = ("These assumptions are exactly what was supplied to the engine. The figures "
              "below are a statement about THESE inputs, not an independent forecast or "
              "investment advice. Change the inputs and the whole distribution moves.")

    # ---- continuous narrative numbers ----
    cp = cont["pair"]
    valuation_word = ("below" if market_price < cprod["median"] else "above")
    gap_pct = abs(market_price - cprod["median"]) / cprod["median"] * 100.0

    # ---- shock narrative ----
    shock_interp = ""
    channel_interp = ""
    if shock:
        sp = shock["pair"]
        sprod = shock["production"]
        z_gap = sp["z_star"] - cp["z_star"]
        median_drop = (cprod["median"] - sprod["median"]) / cprod["median"] * 100.0
        neg_shift = shock["frac_negative_pct"] - cont["frac_negative_pct"]
        more_or_same = ("more paths to resolve" if z_gap > 0 else
                        "no more paths to resolve" if z_gap == 0 else "fewer paths to resolve")
        shock_interp = (
            f"Re-running the simulation with the discrete shock overlay re-converged at "
            f"z** = {sp['z_star']:,} paths, requiring {more_or_same} than the continuous "
            f"engine (z* = {cp['z_star']:,}). The shocks pull the median down by "
            f"{_pct(median_drop)} (from {_f2(cprod['median'])} to {_f2(sprod['median'])}) and "
            f"move the fraction of negative outcomes by {neg_shift:+.2f} percentage points. "
            f"This gap between the continuous and shocked distributions is the engine's "
            f"measure of how much discrete tail risk these fundamentals carry."
        )
        if shock.get("fires_worst5"):
            w = shock["fires_worst5"]
            top = max(w, key=w.get)
            ordered = sorted(w.items(), key=lambda kv: kv[1], reverse=True)
            channel_interp = (
                f"Across the worst 5% of outcomes the most frequently firing shock channel was "
                f"“{top}” ({w[top]} fires), followed by "
                + ", ".join(f"{k} ({v})" for k, v in ordered[1:]) + ". "
                f"Shock-free paths accounted for {_pct(shock['shock_free_pct'])} of the run; the "
                f"remainder absorbed at least one discrete event."
            )

    market_interp = (
        f"At {_f2(market_price)}{(' (' + market_date + ')') if market_date else ''} the market price sits "
        f"{_pct(gap_pct)} {valuation_word} the engine's continuous median of {_f2(cprod['median'])}. "
        f"Where the price falls inside the simulated percentile band (shown above) is the key read: "
        f"the closer to the centre, the more the market and these fundamentals agree; out toward the "
        f"tails, the market is pricing a scenario the fundamentals only reach occasionally."
    )

    seed_interp = ("Convergence was run at a fixed seed (42). z* and z** are the engine's "
                   "self-resolved path counts for THIS company; a different company, or "
                   "different inputs, will resolve at a different number of paths.")

    final_interp = (
        f"Under the stated assumptions the deterministic central value is {_f2(val)} per share at a "
        f"WACC of {_pct(wacc*100,2)}, with a continuous Monte Carlo median of {_f2(cprod['median'])}. "
        + (f"The shocked distribution centres lower, at {_f2(shock['production']['median'])}, reflecting "
           f"the discrete tail risk in these fundamentals. " if shock else "")
        + f"Against today's price of {_f2(market_price)}, the market is trading {_pct(gap_pct)} "
        f"{valuation_word} the central distribution. Treat this as a structured statement about the "
        f"inputs, not a recommendation — the value of the exercise is seeing the full range the "
        f"fundamentals support, and how shocks reshape it."
    )

    meta = {
        "company": company,
        "ticker": ticker,
        "market_price": market_price,
        "market_date": market_date,
        "terminal_growth": base.terminal_growth,
        "base_year": base_year,
        "short_name": company.split()[0] if company else ticker,
        "assumptions": assumptions,
        "assumptions_caveat": caveat,
        "shock_interpretation": shock_interp,
        "channel_interpretation": channel_interp,
        "market_interpretation": market_interp,
        "seed_interpretation": seed_interp,
        "final_interpretation": final_interp,
    }
    if fixture_rel:
        meta["fixture"] = fixture_rel
    return meta
