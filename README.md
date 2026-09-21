# Axiom

An equity research tool built around one principle: every assumption should
be legible before the headline is trusted.

Combines multiples-based valuation, DCF, and analyst consensus with a small
machine-learning correction layer trained on prior prediction errors. Every
numeric assumption is either a peer-comp computation or an entry in the
`HARDCODED_VALUES.md` inventory with a stated phase-out plan. The intended
user is an analyst who wants to read each assumption before relying on the
output.

> **What this is, and what it isn't.**
> Axiom is a research aid, not a quantitative alpha system and not a
> regulated valuation product. The headline value combines (a) hand-curated
> sub-sector multiples and blend weights stored in `valuation/config/*.json`,
> (b) a DCF engine using Damodaran-style synthetic credit spreads, and
> (c) a small GBM correction (`ml/calibrator.py`) trained on ~1,650 prior
> predictions. Most of the output's variance comes from the hand-curated
> tables, not the ML layer. Outputs should be read as one input among
> several, not as a forecast or a recommendation.
>
> See `HARDCODED_VALUES.md` for the full inventory of hand-set constants
> and the phased plan to replace them with live peer-comp estimates.

## What it does

1. **Add a ticker.** Enter any US-listed equity. The app pulls financials from Yahoo Finance.
2. **Run valuation.** One click runs a 10-year DCF alongside a comparable-company analysis.
3. **See the result.** Per-share value with a **bear / base / bull range** (Phase 4 driver-based perturbation: WACC ±100bp, terminal growth ±100bp, Y1 growth ±25%), upside/downside to current price, and a directional read.

No account or paid data feed required.

## Codebase layout (Phase 1)

- `valuation/` — heuristic / multiples-based layer. Sub-sector tagging,
  comparable multiples, blend weights, analyst anchoring, sector-specific
  valuation models (banks → P/B, REITs → P/FFO, utilities → DDM, SaaS → R40).
  **Every numeric assumption here is hand-picked**; see `HARDCODED_VALUES.md`.
- `ml/` — actually-learned-from-data layer. The GBM correction model
  (`calibrator.py`), the walk-forward trainer (`walk_forward.py`), the
  prediction logger (`log.py`), the historical regression backtest
  (`backtest.py`), and the live monitor.
- `valuation_engine.py` — single import surface re-exporting both layers.
- `HARDCODED_VALUES.md` — the inventory.

---

## How the Valuation Works

### The DCF Model

The core is a 10-year discounted cash flow. Here's what it actually calculates:

**Free Cash Flow Projection**
```
FCF = EBITDA × (1 - Tax Rate) - CapEx - Change in Working Capital
```

The model projects FCF for 10 years using a multi-stage growth approach:
- Years 1-3: Current growth rate (from recent financials)
- Years 4-7: Growth fades toward industry average
- Years 8-10: Growth converges to terminal rate (2-3%)

**WACC Calculation**

Weighted Average Cost of Capital uses CAPM for equity:
```
Cost of Equity = Risk-Free Rate + Beta × Market Risk Premium
```

For cost of debt, we use Damodaran's synthetic credit rating approach instead of a hardcoded spread. The model calculates interest coverage ratio (EBIT / Interest Expense) and maps it to a credit spread:

| Coverage Ratio | Implied Rating | Spread |
|----------------|----------------|--------|
| > 8.5 | AAA | 0.60% |
| > 6.5 | AA | 0.90% |
| > 5.5 | A+ | 1.10% |
| > 4.25 | A | 1.40% |
| > 3.0 | A- | 1.60% |
| > 2.5 | BBB | 2.00% |
| > 2.0 | BB+ | 2.40% |
| > 1.5 | BB | 2.75% |
| > 1.25 | B+ | 3.25% |
| > 0.8 | B | 4.00% |
| < 0.8 | CCC/D | 7-15% |

This means a company with strong interest coverage gets a lower cost of debt automatically, without a hand-set spread assumption.

**Terminal Value**

Gordon Growth Model with a sanity cap:
```
Terminal Value = FCF_Year10 × (1 + g) / (WACC - g)
```

Terminal growth is capped at the lower of 3% or (WACC - 1%). This prevents the model from producing infinite values when growth approaches WACC.

**Enterprise Value to Equity**
```
Equity Value = Enterprise Value - Net Debt + Cash
Price per Share = Equity Value / Shares Outstanding
```

### Comparable Company Analysis

The model also calculates implied value from trading multiples:

- **EV/EBITDA**: Enterprise value implied by peer EBITDA multiples
- **P/E Ratio**: Market cap implied by peer P/E multiples

These provide sanity checks on the DCF output.

---

## The ML Calibration Layer

Raw DCF models systematically misprice certain types of companies. A model that works for Microsoft will fail for Tesla. The calibration layer fixes this.

### Sub-Sector Tagging

Instead of broad sectors like "Technology" or "Financials," we classify companies into 60+ sub-categories:

| Category | Examples | Why It Matters |
|----------|----------|----------------|
| `fabless_semi` | NVDA, AMD, AVGO | High margins, growth premiums |
| `IDM_semi` | INTC, STM | Lower multiples, capex-heavy |
| `security_cloud` | CRWD, ZS, PANW | ARR-driven, ignore current EBITDA |
| `commercial_bank` | JPM, BAC, WFC | Use P/B, not DCF |
| `utility_regulated` | NEE, DUK, SO | Dividend yield model |
| `story_auto` | TSLA, RIVN | Growth narrative, not fundamentals |

Each sub-sector gets tuned EBITDA multiples and blend weights.

### Company Classification

Beyond sector, the model classifies each company's financial profile:

- **High-growth**: Revenue growing >20%, may have negative EBITDA. Weight toward revenue multiples.
- **Mature**: Stable margins, predictable FCF. Standard DCF works.
- **Turnaround**: Margins expanding from low base. Project recovery.
- **Distressed**: Negative EBITDA, high leverage. Value optionality.

### EBITDA Normalization

Real-world EBITDA is messy:
- Biotech companies have negative EBITDA by design
- Cyclical companies have EBITDA that swings wildly with the cycle
- One-time charges distort trailing figures

The model normalizes EBITDA by:
1. Adjusting for R&D capitalization in high-growth tech
2. Using mid-cycle margins for cyclicals
3. Excluding one-time restructuring charges

### Blend Weight Optimization

The final fair value is a weighted blend of:
- DCF value
- EV/EBITDA implied value
- P/E implied value
- Analyst consensus (when available)

Weights vary by company type:
- Mature companies: 50% DCF, 25% comps, 25% analyst
- High-growth: 20% DCF, 40% comps, 40% analyst (terminal value dominates DCF, so reduce weight)
- Banks: 100% P/B model (DCF doesn't work for financial institutions)

### The Calibration Model

On top of all the above, an XGBoost model trained on historical prediction errors applies a final adjustment. Features include:
- Sub-sector tag
- Growth rate
- Margin profile
- Size (market cap)
- Momentum (price vs. 200-day MA)

This catches systematic biases the rule-based adjustments miss.

---

## Audit trail and discipline

Built so an analyst can answer "where did this number come from" for any input, and a reviewer can see what has been changed and by whom.

**Assumption-change log.** Every input edit logs field, old value, new value, user, timestamp, change reason, and a materiality flag that auto-triggers on any numeric move greater than 10%. Filterable by date, by user, by material-only. Supports rollback. The workpaper trail lives inside the model, not next to it. (`audit_service.py`)

**Constants inventory.** Every hand-set constant is documented in `HARDCODED_VALUES.md` with file path, line number, what it gates, and which phase replaces it through peer-implied calibration, backtest deltas, or panel regression. About 600 constants today; most are scheduled for retirement.

**Explicit exclusions.** ROE, ROIC, D/E, and Altman Z are not surfaced in the UI even when the data layer computes them. The yfinance inputs are not reliable enough to publish these without misleading the reader. The system refuses to display before it guesses.

**Non-blending rule.** Comparable multiples sit next to the DCF as context, never folded into the headline. There is no silent re-weighting between methods. The headline value means what it says.

---

## Blind Test Results

The model was validated on 76 companies across all sectors. The test was blind: prices were hidden during model tuning.

| Metric | Result |
|--------|--------|
| Mean Absolute Error | 29% |
| Median Error | 22% |
| Within 25% of price | 52% of companies |
| Correct direction | 71% |

**Where it works well:**
- Mature tech (MSFT, AAPL, GOOGL) — stable margins, predictable FCF
- Consumer staples — mean reversion works
- Industrials — cyclical normalization helps
- Banks — P/B model is appropriate

**Where it struggles:**
- Pre-revenue biotech — no earnings to model
- Meme stocks — fundamentals don't drive price
- Chinese ADRs — regulatory discount is hard to quantify

---

## Quickstart

```bash
git clone https://github.com/subhankarshukla04/axiom.git
cd axiom
pip install -r requirements.txt

# Configure database (PostgreSQL or SQLite)
cp .env.example .env
# Edit .env with your database credentials

python app.py
# Open http://localhost:5000
```

**Adding a company:**
1. Click the search icon in the toolbar
2. Enter a ticker (e.g., AAPL)
3. Click "Add & Value"
4. View results in the valuation modal

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Flask, Python 3.11 |
| Database | PostgreSQL (SQLite fallback) |
| Data | Yahoo Finance |
| ML | XGBoost, NumPy |
| Frontend | Vanilla JS, CSS |

---

## Files

```
app.py                    Flask app, API routes
valuation_engine.py       Calibration and alternative-model orchestration
valuation_professional.py DCF detail (WACC, scenarios, ML hookup)
valuation_service.py      Orchestration, DB persistence
audit_service.py          Assumption-change audit trail
ib_valuation_framework.py Archetype classification and IB-style adjustments
data_integrator.py        Yahoo Finance data fetch
realtime_price_service.py Daily price updates
config.py                 Environment config
models.py                 Pydantic schemas
valuation/                Tagging, peer comps, scenarios, alt models, config tables
ml/                       Calibration, walk-forward trainer, backtest, monitor
static/                   CSS, JavaScript
templates/                HTML
```

---

## License

MIT
