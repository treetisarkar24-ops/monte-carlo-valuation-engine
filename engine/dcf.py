"""
Monte Carlo Valuation Engine — Deterministic DCF Skeleton
==========================================================

This module is the spine of the engine. It takes a set of point-estimate
inputs about a company and returns a single equity value per share.

The Monte Carlo machinery built in later steps wraps this function and
perturbs the forward-looking inputs across thousands of runs to produce
a distribution of equity values per share instead of one number.

Built in teach-mode: each block is filled in deliberately, with the
reasoning documented inline so a reader can reconstruct the why, not
just the what.
"""

from dataclasses import dataclass, field
from typing import List


# ============================================================
#  INPUTS — the four buckets
# ============================================================
#  Historical financials, market data, forward-looking
#  assumptions, and structural choices, all collected into one
#  container. The Monte Carlo loop will later vary the
#  forward-looking ones.
# ============================================================


@dataclass
class DCFInputs:
    """Container for everything the engine needs to produce one valuation.

    Organised in four conceptual buckets, in the order an analyst would
    typically gather them:

      1. Starting point (year 0 / t — today): facts read off the most
         recent annual report.
      2. Forecast horizon: how many years we forecast explicitly before
         collapsing the rest into terminal value.
      3. Forward-looking trajectories: the dials Monte Carlo will later
         perturb. One value per forecast year (Option A — lists).
      4. Cost-of-capital ingredients: combine into WACC inside block 5.

    All rates and percentages are stored as decimals (0.12 = 12%) so
    arithmetic stays clean. All currency values are in the same units
    (e.g. millions of USD) — the engine doesn't care which currency,
    only that everything matches.
    """

    # --- 1. Starting point (today, year 0 / t) ---

    starting_revenue: float
    # Current annual revenue. The launching pad — every future year's
    # revenue is built by compounding growth rates onto this number.

    net_debt: float
    # Total debt minus cash and equivalents. Subtracted from enterprise
    # value at the end to get equity value. Can be negative (cash-rich
    # companies have negative net debt).

    shares_outstanding: float
    # Number of shares outstanding. Equity value is divided by this to
    # get the per-share valuation the engine returns.

    # --- 2. Forecast horizon ---

    forecast_years: int
    # How many years we predict explicitly before switching to terminal
    # value. Default 7; stretch to 10 for stable companies; contract to
    # 5 for unstable ones. Choice is made upstream, not in the engine.

    # --- 3. Forward-looking trajectories (one entry per forecast year) ---

    revenue_growth: List[float]
    # Year-by-year revenue growth rates, as decimals. Length must equal
    # forecast_years. Example for 5 years: [0.12, 0.10, 0.08, 0.06, 0.04]
    # means revenue grows 12% in year 1, 10% in year 2, and so on.

    operating_margin: List[float]
    # Year-by-year operating margins (EBIT / revenue), as decimals.
    # EBIT = earnings before interest and tax = revenue minus operating
    # costs but BEFORE the cost of financing and tax bills. This is the
    # core profitability of the business.

    capex_pct_revenue: List[float]
    # Capital expenditure as a fraction of revenue, year by year. Capex
    # is money spent on long-lived assets (factories, equipment, IT) —
    # cash that leaves the business now to support future operations.
    # NOTE: scaling capex off revenue assumes the business is in
    # steady-state replacement mode, where each year's investment
    # roughly maintains the existing revenue base. This breaks for
    # companies in heavy growth-investment phases (capex runs ahead of
    # revenue), companies winding down a build-out (capex collapses
    # once the asset is finished), and asset-light businesses where
    # capex is negligible regardless of revenue. Arguably more fragile
    # than the D&A assumption because capex is the active investment
    # decision, while D&A is its accounting echo.

    da_pct_revenue: List[float]
    # Depreciation and amortisation as a fraction of revenue, year by
    # year. D&A is a non-cash expense that reduces accounting profit
    # but doesn't actually leave the business — we add it back when
    # computing free cash flow.
    # NOTE: scaling D&A off revenue assumes the asset base and revenue
    # grow roughly in proportion. This breaks for capital-heavy
    # companies (utilities, miners, telecoms) where assets dwarf
    # revenue, and for early-stage companies where the asset base is
    # being built ahead of the revenue that justifies it. Use with
    # caution outside the steady-state, asset-light case.

    nwc_pct_revenue: List[float]
    # Change in net working capital as a fraction of revenue, year by
    # year. Working capital is the cash tied up in day-to-day operations
    # (receivables + inventory − payables). As revenue grows, more cash
    # gets tied up — this subtraction reflects that drag.
    # NOTE: this is the most defensible of the three "% of revenue"
    # assumptions because NWC components genuinely scale with sales
    # activity. The breaks are narrower: subscription businesses with
    # deferred revenue (cash arrives before the work is delivered),
    # companies mid-change in payment or inventory policy, and
    # strongly seasonal businesses where annual averaging hides the
    # within-year build and drain.

    tax_rate: float
    # Effective corporate tax rate, as a decimal. Held flat across the
    # forecast period unless there's a reason to vary it (e.g. a
    # scheduled rate change). Applied to EBIT to get NOPAT.

    # --- 4. Terminal (post-forecast) ---

    terminal_growth: float
    # Long-run growth rate of free cash flow after the forecast period,
    # as a decimal. Typically pegged to long-run GDP growth or
    # inflation-plus-a-bit (so usually 2–3%). Must be less than WACC,
    # otherwise the terminal value formula returns infinity or nonsense.

    # --- 5. Cost of capital ingredients ---

    risk_free_rate: float
    # Yield on a long-dated government bond (typically 10-year), as a
    # decimal. The "what you'd earn with no equity risk" baseline.

    equity_risk_premium: float
    # The extra annual return investors demand for holding stocks
    # instead of risk-free bonds, as a decimal. Historically ~5–7%.

    beta: float
    # The stock's sensitivity to broad market moves. Market = 1.0.
    # A beta of 1.3 means the stock tends to move 1.3x the market;
    # 0.7 means it tends to move 0.7x. Pulled from a data provider
    # or computed from price history.
    # NOTE: beta can be negative (the stock moves opposite to the
    # market — e.g. gold-related assets, inverse ETFs, tail-risk
    # hedges) or near zero. The field is `float` deliberately to
    # allow the full real-number range; typical equities sit between
    # 0.3 and 2.5, but negative betas are mathematically valid and
    # economically meaningful — hedging assets command a lower cost
    # of equity in CAPM, which actually raises their DCF value
    # because they reduce portfolio risk.

    cost_of_debt: float
    # The pre-tax interest rate the company pays on its debt, as a
    # decimal. The engine applies the tax shield inside WACC
    # (because interest is tax-deductible).

    debt_to_total_capital: float
    # Debt as a fraction of total capital (debt + equity), as a
    # decimal. The weighting used in WACC: weights cost of debt and
    # cost of equity by how much of each the company is funded with.


# ============================================================
#  BLOCK 1 — Revenue projection
# ============================================================
#  Project annual revenue across the explicit forecast period
#  from a starting revenue and a growth-rate trajectory.
# ============================================================


def project_revenue(inputs: DCFInputs) -> List[float]:
    """Project annual revenue across the explicit forecast period.

    The recipe: take the starting revenue (year 0, today) and grow it
    forward year by year by compounding each year's growth rate onto
    the previous year's revenue.

        revenue[t] = revenue[t-1] × (1 + growth[t])

    Returns a list of length `inputs.forecast_years`. revenues[0] is
    the revenue in forecast year 1, revenues[-1] is the revenue in the
    final forecast year. Year 0 (the starting revenue itself) is NOT
    included in the returned list — downstream blocks can read it from
    `inputs.starting_revenue` if they need it.
    """
    revenues: List[float] = []          # the output list we're building
    current = inputs.starting_revenue   # running value, starts at year 0

    # Walk the growth trajectory one year at a time, compounding as
    # we go. Each iteration produces one forecast year's revenue.
    for growth_rate in inputs.revenue_growth:
        current = current * (1 + growth_rate)
        revenues.append(current)

    return revenues


# ============================================================
#  BLOCK 2 — Margins → NOPAT
# ============================================================
#  Apply operating margin to revenue to get EBIT, then tax to
#  get NOPAT (net operating profit after tax).
# ============================================================


def project_ebit(revenues: List[float], inputs: DCFInputs) -> List[float]:
    """Project EBIT (operating profit) for each forecast year.

    Applies each year's operating margin to that year's revenue:

        EBIT[t] = revenue[t] × operating_margin[t]

    EBIT (earnings before interest and tax) is the operating profit
    the business produces before paying its financing costs and tax
    bill. Note: EBIT is computed AFTER D&A — operating costs in this
    margin already include depreciation and amortisation. That's why
    we'll need to add D&A back in block 3 when we move to cash flow.

    The operating margin is stored as a trajectory (one value per
    forecast year) because real businesses see margins drift over
    time — expanding as scale absorbs fixed costs, compressing under
    competitive pressure, cyclical swings, and so on.

    Returns a list of length len(revenues), one EBIT value per year.
    """
    # zip pairs each revenue with its corresponding margin, element
    # by element, so margin[i] applies to revenue[i].
    return [
        revenue * margin
        for revenue, margin in zip(revenues, inputs.operating_margin)
    ]


def project_nopat(ebits: List[float], inputs: DCFInputs) -> List[float]:
    """Project NOPAT (net operating profit after tax) for each year.

    Applies the corporate tax rate to each year's EBIT:

        NOPAT[t] = EBIT[t] × (1 − tax_rate)

    NOPAT is what's left of operating profit after the tax bill,
    but BEFORE financing costs (interest expense). This is the
    correct base for free cash flow to the firm — capital structure
    (how the business is funded) is handled separately, inside WACC,
    not here. That separation is what makes a DCF an "operating
    value" first and an "equity value" second.

    Tax rate is held flat across the forecast period (single float
    in inputs, not a list). Vary it later only if there's a specific
    reason — e.g. a scheduled corporate-tax-code change.

    Returns a list of length len(ebits), one NOPAT value per year.
    """
    # Apply (1 - tax_rate) to each EBIT value. Mathematically
    # equivalent to subtracting the tax bill (EBIT × tax_rate) from
    # EBIT, just expressed multiplicatively.
    return [ebit * (1 - inputs.tax_rate) for ebit in ebits]


# ============================================================
#  BLOCK 3 — Free cash flow
# ============================================================
#  Add back D&A (non-cash), subtract capex, subtract change in
#  working capital. Result: free cash flow to the firm (FCFF).
# ============================================================


def project_da(revenues: List[float], inputs: DCFInputs) -> List[float]:
    """Project depreciation and amortisation for each forecast year.

    D&A is computed as a fraction of revenue using the trajectory
    in inputs.da_pct_revenue. See the inline NOTE on da_pct_revenue
    in DCFInputs for the modelling caveat: this assumes asset base
    and revenue grow roughly in proportion, which breaks for
    capital-heavy and early-stage companies.
    """
    return [
        revenue * pct
        for revenue, pct in zip(revenues, inputs.da_pct_revenue)
    ]


def project_capex(revenues: List[float], inputs: DCFInputs) -> List[float]:
    """Project capital expenditure for each forecast year.

    Capex is computed as a fraction of revenue using the trajectory
    in inputs.capex_pct_revenue. Capex is real cash leaving the
    business to fund long-lived assets — factories, equipment, IT
    infrastructure. See the inline NOTE on capex_pct_revenue for
    the modelling caveat (steady-state replacement assumption,
    fragile during build-out and wind-down phases).
    """
    return [
        revenue * pct
        for revenue, pct in zip(revenues, inputs.capex_pct_revenue)
    ]


def project_dnwc(revenues: List[float], inputs: DCFInputs) -> List[float]:
    """Project change in net working capital for each forecast year.

    ΔNWC is computed as a fraction of revenue using the trajectory
    in inputs.nwc_pct_revenue. The DELTA matters (not the absolute
    NWC level) because what affects free cash flow is whether cash
    is being newly tied up (positive ΔNWC, drag on cash flow) or
    newly released (negative ΔNWC, boost). See the inline NOTE on
    nwc_pct_revenue for the modelling caveat.
    """
    return [
        revenue * pct
        for revenue, pct in zip(revenues, inputs.nwc_pct_revenue)
    ]


def project_fcf(
    nopat: List[float],
    revenues: List[float],
    inputs: DCFInputs,
) -> List[float]:
    """Project free cash flow to the firm (FCFF) for each forecast year.

    Recipe:

        FCFF[t] = NOPAT[t] + D&A[t] − Capex[t] − ΔNWC[t]

    FCFF is the cash the business actually generates and has available
    to distribute to ALL its funders — debt holders and equity holders
    combined. "To the firm" means before we split debt and equity;
    that split happens later in block 6 when we subtract net debt to
    get equity value.

    The three adjustments each have a reason. D&A is added back
    because it was subtracted to get EBIT but isn't real cash leaving
    the business (it's an accounting allocation of past asset
    purchases). Capex is subtracted because it IS real cash leaving
    the business now, and NOPAT doesn't account for it. ΔNWC is
    subtracted because cash tied up in receivables and inventory
    isn't available to distribute, even though it's still the
    business's money in an accounting sense.

    Composes the three helpers above for inspectability — each can
    be called separately to display intermediate values.

    Returns a list of length len(nopat), one FCFF value per year.
    """
    da = project_da(revenues, inputs)
    capex = project_capex(revenues, inputs)
    dnwc = project_dnwc(revenues, inputs)

    # Walk all four lists in lockstep, applying the FCFF formula to
    # each year's bundle of (nopat, da, capex, dnwc) values.
    return [
        n + d - c - w
        for n, d, c, w in zip(nopat, da, capex, dnwc)
    ]


# ============================================================
#  BLOCK 4 — WACC (weighted average cost of capital)
# ============================================================
#  Combine cost of equity (CAPM), cost of debt (post-tax shield),
#  and capital structure into a single discount rate. Used by
#  block 5 (terminal value) and block 6 (discounting).
# ============================================================


def compute_wacc(inputs: DCFInputs) -> float:
    """Compute the weighted average cost of capital (WACC).

    WACC is the blended rate the company has to pay across all its
    sources of capital. It's the discount rate the engine uses to
    convert future cash to present value, because it represents the
    OPPORTUNITY COST — what investors could earn elsewhere at similar
    risk. Used in two places downstream: block 5 (terminal value)
    plugs it into the Gordon growth perpetuity, and block 6
    (discounting) uses it to pull every future cash flow back to
    year 0.

    Formula:

        WACC = (E/V) × Cost_of_Equity + (D/V) × Cost_of_Debt × (1 − tax_rate)

    Where E/V is equity's share of total capital, D/V is debt's share,
    Cost_of_Equity comes from CAPM (below), and (1 − tax_rate) is the
    tax shield on debt (interest is deductible in most jurisdictions,
    so the firm's effective cost of debt is lower than the headline
    rate). E/V + D/V = 1 by construction — proportions of the same
    whole. The engine stores only D/V (`debt_to_total_capital`) in
    inputs; equity weight is derived as `1 − D/V`, which keeps the
    two from drifting out of sync.

    Cost of equity uses the Capital Asset Pricing Model (CAPM):

        Cost_of_Equity = risk_free_rate + beta × equity_risk_premium

    CAPM's logic: investors deserve at least the risk-free rate (what
    they could earn with zero risk), plus a premium scaled by how much
    market risk this particular stock carries. Beta is the scaling
    factor; for the market itself beta = 1, defensive stocks have
    beta < 1, aggressive stocks have beta > 1, and hedging assets can
    have beta near zero or negative.

    Market vs book values: WACC theory wants MARKET values for E and D,
    not book values, because that reflects what investors currently
    demand returns on. For equity this is direct (share price × shares
    outstanding). For debt, most corporate debt doesn't trade actively,
    so analysts substitute book value as a proxy — close enough for
    healthy firms, can break down for distressed companies whose bonds
    trade well below par. The engine takes whatever D/V the analyst
    provides at face value.

    Capital structure: held constant across the forecast. Real firms
    can re-lever or de-lever over time; the engine takes the CURRENT
    mix as the assumed mix throughout. If a company's structure is
    likely to shift materially, that should be reflected by updating
    the input, not by varying the structure inside this function.

    First block that takes only `inputs` — no prior block's output
    feeds in. WACC depends purely on market data and capital
    structure, not on the operating projection. Returns a single
    float; the orchestrator passes that one number into both
    terminal_value (block 5) and the discounter (block 6).
    """
    # ---- Cost of equity via CAPM ----
    # rf is the no-risk baseline (what an investor could earn in a
    # 10-year government bond). beta × ERP is the EXTRA return demanded
    # for taking on this particular stock's market risk. Together:
    # "I want the safe rate, plus a premium scaled to how much I'm
    # bouncing around with the market."
    cost_of_equity = (
        inputs.risk_free_rate
        + inputs.beta * inputs.equity_risk_premium
    )

    # ---- After-tax cost of debt (the tax shield) ----
    # Interest payments are tax-deductible: every $1 of interest paid
    # reduces taxable income by $1, saving (tax_rate × $1) on the tax
    # bill. So the EFFECTIVE cost of debt is the headline rate scaled
    # down by (1 − tax_rate). At cost_of_debt = 6% and tax_rate = 25%,
    # the effective post-tax cost is 6% × 0.75 = 4.5%.
    after_tax_cost_of_debt = inputs.cost_of_debt * (1 - inputs.tax_rate)

    # ---- Capital-structure weights ----
    # debt_to_total_capital IS D/V. Equity weight is what's left.
    # Sum to 1 by construction.
    weight_debt = inputs.debt_to_total_capital
    weight_equity = 1 - weight_debt

    # ---- Blended rate ----
    # Weighted average: each component multiplied by its share of the
    # capital base, then summed. The bigger the debt slice, the more
    # WACC tilts toward the (cheaper) after-tax debt cost — which is
    # why levered firms tend to have lower WACCs, up to the point
    # where bankruptcy risk starts pushing every cost component up.
    wacc = (
        weight_equity * cost_of_equity
        + weight_debt * after_tax_cost_of_debt
    )

    return wacc


# ============================================================
#  BLOCK 5 — Terminal value
# ============================================================
#  Collapse all cash flows beyond the explicit forecast into a
#  single number using Gordon growth: TV = FCF_{N+1} / (WACC - g).
# ============================================================


def terminal_value(
    fcfs: List[float],
    wacc: float,
    inputs: DCFInputs,
) -> float:
    """Compute terminal value (TV) — a single number positioned at year N.

    The explicit forecast stops at year N (the last entry in `fcfs`). The
    business doesn't disappear in year N+1, though — it keeps generating
    cash, in principle forever. Terminal value collapses all that
    post-forecast cash into one lump-sum number sitting at year N.

    We use the Gordon growth model (Myron Gordon, 1959): assume that from
    year N+1 onward, free cash flow grows forever at a constant rate g
    (the long-run, steady-state growth rate). The present value AT YEAR
    N of an infinitely growing cash stream is:

        TV_N = FCF_{N+1} / (WACC - g)

    Where FCF_{N+1} is the first post-forecast year's cash flow, usually
    estimated as FCF_N × (1 + g) — i.e. one more year of growth at the
    terminal rate. This assumes the business has reached steady state by
    year N.

    The clean formula comes from summing the geometric series of a
    perpetuity (an infinite stream of payments) that grows at g and is
    discounted at WACC. The load-bearing fact: as long as WACC > g, the
    discounting outruns the growth and the infinite sum converges to a
    finite number. If g >= WACC the sum explodes — economically that
    would mean a business growing faster than its cost of capital
    forever, which can't be true of any real firm (it would eventually
    own the entire economy). Input validation enforcing g < WACC is
    deferred to step 7 of the build sequence; here we just document
    the requirement.

    Why g is typically 2-3%: it's pegged to long-run GDP growth or
    inflation-plus-a-touch. No company can grow faster than the broader
    economy forever — pick g above that and you're implicitly claiming
    the company eventually IS the economy.

    Why TV is large: in most DCFs, terminal value is 60-80% of total
    enterprise value. That's mathematically expected — a perpetuity
    captures ALL cash beyond N, which is a lot of years. It also means
    TV inputs (especially g) deserve heavy scrutiny — exactly the kind
    of thing the Monte Carlo overlay will later perturb.

    A design note on the WACC parameter: TV needs WACC, which is
    computed in block 4 (the prior block). We take it as a parameter
    rather than recomputing it here — single source of truth. The
    orchestrator calls compute_wacc(inputs) once and passes that float
    into both this function and the discounter (block 6).

    Returns a single float (not a list) — TV is one lump number at
    year N, unlike the per-year trajectories every prior block returns.
    Discounting TV back to year 0 happens in block 6 alongside the
    explicit FCFs.
    """
    # Last forecast year's FCF — the launching pad for the perpetuity.
    fcf_N = fcfs[-1]

    # The terminal growth rate g, pulled from inputs. Decimal form
    # (e.g. 0.025 means 2.5% per year forever).
    g = inputs.terminal_growth

    # FCF in the FIRST post-forecast year (year N+1). Standard
    # convention: grow the last forecast FCF one more year at g.
    # Assumes the business has reached steady state by year N.
    fcf_next = fcf_N * (1 + g)

    # Gordon growth perpetuity. The denominator (wacc - g) is the
    # "spread" — how much faster the discount rate runs than the
    # growth rate. Smaller spread → larger TV (more sensitive to
    # both inputs as the spread narrows toward zero).
    tv = fcf_next / (wacc - g)

    return tv


# ============================================================
#  BLOCK 6 — Discounting
# ============================================================
#  Pull each forecast FCF and the terminal value back to present
#  value (PV) using WACC. Sum the PVs to get enterprise value.
# ============================================================


def discount_fcfs(fcfs: List[float], wacc: float) -> List[float]:
    """Pull each forecast year's free cash flow back to year 0.

    Each FCF arrives at the end of year t (end-of-year convention).
    Its present value is the future amount divided by (1 + WACC)^t —
    the discount factor, which represents how much $1 today would
    have grown to in t years at rate WACC. Dividing un-grows future
    cash back to today's equivalent.

        PV[t] = FCF[t] / (1 + WACC)^t

    Returns a list of length len(fcfs), one PV per forecast year.
    The list is positional: pv_fcfs[0] is the PV of year-1 FCF,
    pv_fcfs[-1] is the PV of year-N FCF. Exposed as a separate
    helper so diagnostic reports can show how discounting attenuates
    each year's contribution without digging inside discount().
    """
    # enumerate(..., start=1) gives us (t, fcf) pairs where t is the
    # year number (1, 2, ..., N). Year-1 cash is discounted once;
    # year-N cash is discounted N times — that's the geometric decay
    # the discount factor encodes.
    return [
        fcf / (1 + wacc) ** t
        for t, fcf in enumerate(fcfs, start=1)
    ]


def discount_tv(tv: float, n: int, wacc: float) -> float:
    """Pull the terminal value back to year 0.

    Terminal value is positioned at year n (the last explicit forecast
    year) by block 5. So it gets the same discount treatment as the
    year-n FCF — divide by (1 + WACC)^n.

        PV_TV = TV / (1 + WACC)^n

    Returns a single float. Exposed as a separate helper because PV_TV
    is one of the most-watched diagnostic numbers in a DCF — it's
    typically 60–80% of enterprise value and tells you how much of the
    answer is driven by the perpetuity assumption (the post-forecast
    tail) versus the explicit forecast period.
    """
    return tv / (1 + wacc) ** n


def discount(
    fcfs: List[float],
    tv: float,
    wacc: float,
) -> float:
    """Compose the two discounting helpers into enterprise value.

    Enterprise value (EV) is the total present value of all the firm's
    future cash, before splitting between debt holders and equity
    holders:

        EV = sum(PV_FCFs) + PV_TV

    EV represents what the operating business is worth today, funded
    by ALL its capital providers combined. Block 7 (the equity bridge)
    takes this number, subtracts net debt to back out the equity
    holders' slice, and divides by shares outstanding to produce the
    per-share intrinsic value the engine ultimately returns.

    Convention: end-of-year discounting — each year's cash is treated
    as arriving at the end of that year. Mid-year convention would
    assume cash arrives smoothly across the year and would shift PVs
    up slightly (less discounting per period). End-of-year is the
    standard textbook choice and what most published DCFs use, so the
    engine matches that for parity.

    Returns a single float — the enterprise value, in the same
    currency units as the input cash flows (typically $M).
    """
    # Discount the FCF trajectory (year 1 through year N).
    pv_fcfs = discount_fcfs(fcfs, wacc)

    # Discount the terminal value (positioned at year N). len(fcfs)
    # is N — same year as the last explicit forecast, so TV gets
    # the same denominator as the year-N FCF.
    pv_tv = discount_tv(tv, len(fcfs), wacc)

    # Sum to enterprise value: sum() over the list of PV_FCFs, plus
    # the single PV_TV float.
    return sum(pv_fcfs) + pv_tv


# ============================================================
#  BLOCK 7 — Equity bridge
# ============================================================
#  Subtract net debt from enterprise value to isolate the equity
#  holders' slice. Divide by shares outstanding for per-share
#  intrinsic value — the engine's final answer.
# ============================================================


def equity_value(ev: float, inputs: DCFInputs) -> float:
    """Bridge from enterprise value to total equity value.

    EV is the value of the operating business to ALL capital providers
    combined — debt holders and equity holders. To isolate the equity
    holders' slice, subtract net debt:

        Equity Value = EV − Net Debt

    Net debt = total debt − cash and equivalents (stored directly in
    inputs.net_debt by the analyst — the engine doesn't compute it
    from raw balance-sheet numbers). The netting matters: cash on the
    balance sheet is an asset shareholders effectively already own
    (it could be paid as a dividend or used to retire debt), so we
    subtract only the debt that the cash doesn't already offset.
    Otherwise we'd double-penalise equity by ignoring the cash
    literally sitting there ready to pay debt down.

    Net debt can be negative (cash > debt) for cash-rich firms like
    Apple or Berkshire Hathaway. In that case Equity Value > EV — the
    cash hoard accrues entirely to shareholders on top of the
    operating business. The arithmetic handles this naturally:
    EV − (−x) = EV + x.

    Returns a single float, in the same currency units as EV. Useful
    as a diagnostic on its own: equity_value / EV tells you what
    share of enterprise value belongs to equity, which is a leverage
    signal (lower ratio → more levered firm).
    """
    return ev - inputs.net_debt


def equity_value_per_share(
    equity_val: float,
    inputs: DCFInputs,
) -> float:
    """Bridge from total equity value to per-share intrinsic value.

    The engine's final answer. Divide total equity value by the share
    count to produce intrinsic value per share — what one share is
    worth, according to this model, based on the cash the business
    will produce, discounted at the rate investors demand.

        Equity Value Per Share = Equity Value / Shares Outstanding

    This is NOT the same as market price. Market price is the
    consensus the market is currently quoting on the exchange. The
    actionable signal is the COMPARISON: intrinsic value > market
    price suggests potentially undervalued; intrinsic value < market
    price suggests potentially overvalued.

    A `current_market_price` field is deliberately NOT in DCFInputs.
    Market price is the benchmark we compare the engine's output
    against, not an input the engine consumes. It will be added at
    the comparison/output step.

    When the Monte Carlo machinery (step 3 of the build sequence)
    wraps this engine, the output becomes a DISTRIBUTION of per-share
    values rather than a single number — and that distribution gets
    compared against market price. A far stronger statement than one
    number versus one number, because it lets the analyst say things
    like "the market price sits at the 12th percentile of our
    intrinsic-value distribution" rather than just "our number is
    higher than theirs."

    Returns a single float — the engine's deterministic per-share
    intrinsic value, in the same currency units as the inputs.
    """
    return equity_val / inputs.shares_outstanding


# ============================================================
#  ORCHESTRATOR — run the whole engine
# ============================================================


def run_dcf(inputs: DCFInputs) -> float:
    """Run the deterministic DCF from inputs to per-share intrinsic value.

    Wires the seven engine blocks together in strict dependency order
    and returns the engine's final answer — equity value per share.

    The composition order matches the block numbering inside this
    module:

        block 1: starting_revenue ─→ revenues
        block 2: revenues + margins ─→ EBIT ─→ NOPAT
        block 3: NOPAT + (D&A − Capex − ΔNWC) ─→ FCFs
        block 4: cost-of-capital ingredients ─→ WACC
        block 5: FCFs + WACC ─→ TV (year N)
        block 6: FCFs + TV + WACC ─→ enterprise value
        block 7: EV − net debt ─→ equity value ─→ per share

    Each block reads only from prior blocks. No shared mutable state,
    no hidden coupling — every dependency travels as an explicit
    function argument. This is the spine the Monte Carlo machinery
    will later wrap: perturb the forward-looking inputs, call
    run_dcf, collect the float, repeat n times, build the
    distribution.

    Returns a single float — per-share intrinsic value in the same
    currency units as the inputs. For diagnostic visibility into
    intermediate trajectories (WACC, TV, EV, etc.), call the
    individual blocks directly rather than going through the
    orchestrator.
    """
    # Block 1 — revenue trajectory
    revenues = project_revenue(inputs)

    # Block 2 — operating profit (split for inspectability)
    ebits = project_ebit(revenues, inputs)
    nopats = project_nopat(ebits, inputs)

    # Block 3 — free cash flow to the firm
    fcfs = project_fcf(nopats, revenues, inputs)

    # Block 4 — discount rate (computed once, reused twice below)
    wacc = compute_wacc(inputs)

    # Block 5 — terminal value, positioned at year N
    tv = terminal_value(fcfs, wacc, inputs)

    # Block 6 — pull everything to present value, sum to EV
    ev = discount(fcfs, tv, wacc)

    # Block 7 — bridge EV to equity, then to per-share
    eq_val = equity_value(ev, inputs)
    per_share = equity_value_per_share(eq_val, inputs)

    return per_share
