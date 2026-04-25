# Axiom

Institutional-grade equity valuation platform. DCF, LBO, comps, portfolio optimization, and an ML calibration layer that hit 29% MAE on a 76-company blind test.

---

## What This Actually Is

Most valuation tools are either (a) Excel templates that break when you look at them wrong, or (b) enterprise software that costs $50k/seat. Axiom is neither. It's a Flask app that runs real DCF models with real data sources, outputs real numbers, and has been validated against actual stock prices.

The core differentiator is the ML calibration engine. Raw DCF models systematically misprice certain sectors — growth stocks get undervalued, value traps get overvalued, banks don't work with standard EV math. The calibration layer fixes this by:

1. **Sub-sector tagging** — 60+ categories (fabless_semi, security_cloud, commercial_bank, utility_regulated, etc.) instead of broad sectors
2. **Adaptive blend weights** — DCF weight drops for high-growth companies where terminal value dominates
3. **Alternative models** — P/B for banks, dividend yield for utilities, rule-of-40 for SaaS
4. **Analyst anchor** — When consensus targets exist, blend them in to reduce model variance
5. **Gradient boosting layer** — XGBoost model trained on historical prediction errors

This isn't theoretical. We ran a 76-company blind test across all sectors — no peeking at prices during model tuning — and hit 29% mean absolute error. The model correctly identified undervalued and overvalued names.

---

## Features

### Valuation Engine
- **10-year DCF** — Multi-stage growth projections, WACC via CAPM with Damodaran synthetic credit rating for cost of debt
- **Comparable Analysis** — EV/EBITDA and P/E using sector-appropriate multiples (not one-size-fits-all)
- **LBO Modeling** — Entry multiple, debt tranches, IRR/MOIC at exit, 2D sensitivity grid
- **Monte Carlo** — 1,000-iteration simulation on terminal value for confidence intervals
- **Football Field** — Aggregated valuation range across all methods

### ML Calibration Layer
- **Sub-sector classification** — Ticker lookup + industry text matching for 60+ categories
- **EBITDA normalization** — Handles negative EBITDA (biotech, growth), one-time charges, cyclical troughs
- **Company type detection** — High-growth, turnaround, mature, distressed — each gets different treatment
- **Blend weight optimization** — DCF vs. comps vs. analyst weights tuned per company profile
- **Prediction logging** — Every valuation logged with inputs for backtesting

### Data Sources
- **SEC EDGAR** — XBRL financials (income statement, balance sheet, cash flow)
- **FRED** — Live risk-free rate, macro series
- **Finnhub** — Real-time quotes, earnings calendar, insider transactions
- **Yahoo Finance** — Backup quotes, historical prices for backtesting
- **FMP** — Supplemental financials when EDGAR gaps exist

### Portfolio Management
- **Quick-add** — Enter ticker, pull all financials automatically, run valuation
- **Multi-select UI** — Checkbox selection, bulk delete, batch operations
- **Daily price updates** — APScheduler runs at 4:30 PM ET after market close
- **Mean-variance optimization** — Markowitz efficient frontier with Sharpe maximization

### Export & Intelligence
- **PDF pitchbook** — 7-section WeasyPrint export formatted for client delivery
- **Excel DCF** — 5-sheet openpyxl workbook with linked formulas
- **Anomaly detection** — Z-score flagging when assumptions deviate from sector benchmarks
- **Alert engine** — Earnings dates, insider filings, macro shifts

---

## Blind Test Results

76 companies. All sectors. No price peeking during calibration.

| Metric | Result |
|--------|--------|
| Mean Absolute Error | 29% |
| Median Error | 22% |
| Within 25% of price | 52% of companies |
| Correct direction (over/undervalued) | 71% |

The model struggles with:
- Pre-revenue biotech (no earnings to model)
- Meme stocks (fundamentals don't drive price)
- Chinese ADRs (regulatory discount hard to quantify)

It works well on:
- Mature tech (MSFT, AAPL, GOOGL)
- Industrials and consumer staples
- Banks and financials (once you use P/B instead of DCF)
- Utilities (dividend yield model)

---

## Architecture

```
app.py                          Flask entry, route registration
├── ml_engine.py                Calibration layer (1,267 lines)
│   ├── Sub-sector tagging      60+ categories via TICKER_TAG_MAP + industry text
│   ├── Company classification  High-growth, turnaround, mature, distressed
│   ├── EBITDA normalization    Handles negative, one-time, cyclical
│   ├── Blend weight optimizer  DCF/comps/analyst weights per profile
│   └── XGBoost calibration     Gradient boosting on prediction residuals
│
├── valuation_professional.py   Core DCF engine (699 lines)
│   ├── Damodaran WACC          Synthetic credit rating for cost of debt
│   ├── Multi-stage growth      Fade from current growth to terminal
│   ├── Terminal value          Gordon growth with sanity bounds
│   └── Monte Carlo             1,000 iterations on terminal assumptions
│
├── valuation_service.py        Orchestration, DB persistence
├── data_integrator.py          Multi-source data ingestion
├── lbo_engine.py               LBO model with IRR/MOIC
├── portfolio_engine.py         Mean-variance optimization
│
├── axiom_api_endpoints.py      LBO, football field, exports, alerts
├── phase1_api_endpoints.py     Scenario management, audit trail
├── advanced_api_endpoints.py   Portfolio construction, ticker import
│
├── data_layer/                 EDGAR, FRED, Finnhub, FMP integrations
├── intelligence/               Anomaly detection, alert engine
└── services/                   LLM/RAG (optional, requires OpenRouter)
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11, Flask 3.0 |
| Database | PostgreSQL 15 (SQLite fallback) |
| ML | XGBoost, NumPy, scikit-learn |
| Data | SEC EDGAR, FRED, Finnhub, Yahoo Finance |
| Frontend | Vanilla JS, TailwindCSS, SSE |
| Exports | WeasyPrint (PDF), openpyxl (Excel) |
| Scheduling | APScheduler |

---

## Quickstart

```bash
# Clone and setup
git clone https://github.com/subhankarshukla04/axiom.git
cd axiom
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Configure .env
DATABASE_TYPE=postgresql  # or sqlite
POSTGRES_DB=axiom
POSTGRES_USER=your_user
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Optional API keys (free tiers available)
FRED_API_KEY=           # https://fred.stlouisfed.org/docs/api/api_key.html
FINNHUB_API_KEY=        # https://finnhub.io

# Start PostgreSQL (Docker)
docker run -d --name axiom-db \
  -e POSTGRES_USER=axiom -e POSTGRES_PASSWORD=axiom -e POSTGRES_DB=axiom \
  -p 5432:5432 postgres:15

# Run
python app.py
# → http://localhost:5000
```

---

## What We Fixed (April 2026 Session)

Critical bugs that were silently breaking valuations:

1. **Placeholder count mismatch** — INSERT had 25 columns, query only had 21 placeholders. No valuation was being saved.

2. **PostgreSQL column drift** — `init_db()` skipped PostgreSQL, so new columns (`industry`, `sub_sector_tag`, `ebitda_method`, `analyst_target`) never migrated. Added `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` migration loop.

3. **Missing ticker/industry in queries** — `fetch_company_data()` didn't return `ticker` or `industry`, breaking ML classification. Fixed both SELECT queries.

4. **Fair value showing total equity** — `list_companies` fetched `final_equity_value` (trillions) instead of `final_price_per_share`. Cards showed $2.57T for NVDA instead of $152/share.

5. **ORDER BY non-existent column** — `get_latest_valuation()` ordered by `created_at`, but column is `valuation_date`.

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/valuation/<id>` | Run full valuation with ML calibration |
| `POST` | `/api/lbo/<id>` | LBO model — IRR, MOIC, sensitivity |
| `GET` | `/api/company/<id>/football-field` | Valuation range visualization |
| `GET` | `/api/company/<id>/sensitivity` | WACC × terminal growth table |
| `GET` | `/api/company/<id>/peers` | EDGAR SIC peer set |
| `POST` | `/api/portfolio/optimize` | Mean-variance optimization |
| `GET` | `/api/company/<id>/export/pdf` | Pitchbook PDF |
| `GET` | `/api/company/<id>/export/excel` | DCF Excel workbook |

---

## Methodology

See [INVESTMENT_BANKING_METHODOLOGY.md](./INVESTMENT_BANKING_METHODOLOGY.md) for:
- WACC construction (CAPM + Damodaran synthetic rating)
- DCF projection mechanics
- LBO assumptions
- Normalization logic for distressed/cyclical companies
- Data source hierarchy and fallback logic

---

## License

MIT
