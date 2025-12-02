-- Migration 001: Add Scenario Management Tables
-- Created: 2025-12-02
-- Purpose: Add bear/base/bull scenario support with full assumption tracking

-- ============================================================================
-- TABLE 1: scenarios
-- Stores different assumption sets (Bear Case, Base Case, Bull Case)
-- ============================================================================
CREATE TABLE IF NOT EXISTS scenarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('bear', 'base', 'bull', 'custom')),
    description TEXT,
    is_active INTEGER DEFAULT 1,  -- 0 = archived, 1 = active
    parent_scenario_id INTEGER,  -- For cloned scenarios
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT DEFAULT 'system',
    FOREIGN KEY (parent_scenario_id) REFERENCES scenarios(id)
);

-- Create default scenarios
INSERT INTO scenarios (id, name, type, description, is_active) VALUES
(1, 'Bear Case', 'bear', 'Conservative assumptions with downside risks', 1),
(2, 'Base Case', 'base', 'Most likely scenario with balanced assumptions', 1),
(3, 'Bull Case', 'bull', 'Optimistic assumptions with strong growth', 1);

-- ============================================================================
-- TABLE 2: macro_assumptions
-- Track market-level parameters that affect all valuations
-- ============================================================================
CREATE TABLE IF NOT EXISTS macro_assumptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    date DATE NOT NULL,
    gdp_growth REAL,
    inflation_rate REAL,
    risk_free_rate_3m REAL,
    risk_free_rate_10y REAL,
    market_risk_premium REAL DEFAULT 0.065,  -- 6.5% default
    credit_spread_investment_grade REAL DEFAULT 0.015,  -- 1.5% default
    credit_spread_high_yield REAL DEFAULT 0.025,  -- 2.5% default
    FOREIGN KEY (scenario_id) REFERENCES scenarios(id) ON DELETE CASCADE
);

-- Create default macro assumptions for each scenario
-- Base Case (using current market conditions)
INSERT INTO macro_assumptions (scenario_id, date, gdp_growth, inflation_rate, risk_free_rate_10y, market_risk_premium) VALUES
(2, date('now'), 0.025, 0.025, 0.045, 0.065);  -- Base: 2.5% GDP, 2.5% inflation, 4.5% 10Y, 6.5% MRP

-- Bear Case (recession scenario)
INSERT INTO macro_assumptions (scenario_id, date, gdp_growth, inflation_rate, risk_free_rate_10y, market_risk_premium) VALUES
(1, date('now'), 0.01, 0.03, 0.055, 0.075);  -- Bear: 1% GDP, 3% inflation, 5.5% 10Y, 7.5% MRP

-- Bull Case (expansion scenario)
INSERT INTO macro_assumptions (scenario_id, date, gdp_growth, inflation_rate, risk_free_rate_10y, market_risk_premium) VALUES
(3, date('now'), 0.04, 0.02, 0.035, 0.055);  -- Bull: 4% GDP, 2% inflation, 3.5% 10Y, 5.5% MRP

-- ============================================================================
-- TABLE 3: scenario_company_assumptions
-- Company-specific assumption overrides per scenario
-- ============================================================================
CREATE TABLE IF NOT EXISTS scenario_company_assumptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    company_id INTEGER NOT NULL,

    -- Growth assumptions
    growth_rate_y1 REAL,
    growth_rate_y2 REAL,
    growth_rate_y3 REAL,
    terminal_growth REAL,

    -- Cost structure
    tax_rate REAL,

    -- Risk parameters
    beta REAL,
    size_premium REAL,
    country_risk_premium REAL,

    -- Valuation weights (sum to 1.0)
    weight_dcf REAL DEFAULT 0.50,
    weight_ev_ebitda REAL DEFAULT 0.25,
    weight_pe REAL DEFAULT 0.25,

    -- Metadata
    rationale TEXT,  -- Why these assumptions for this scenario
    source TEXT,  -- Where assumptions came from
    confidence_level TEXT CHECK(confidence_level IN ('low', 'medium', 'high')),
    last_updated_by TEXT,
    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (scenario_id) REFERENCES scenarios(id) ON DELETE CASCADE,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    UNIQUE(scenario_id, company_id)  -- One set of assumptions per scenario per company
);

-- ============================================================================
-- TABLE 4: assumption_audit_log
-- Track all changes to assumptions (regulatory compliance)
-- ============================================================================
CREATE TABLE IF NOT EXISTS assumption_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    record_id INTEGER NOT NULL,
    field_name TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    changed_by TEXT NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason TEXT
);

-- Index for fast audit queries
CREATE INDEX IF NOT EXISTS idx_audit_log_table_record ON assumption_audit_log(table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_date ON assumption_audit_log(changed_at);

-- ============================================================================
-- TABLE 5: peer_groups
-- Manage comparable companies for peer benchmarking
-- ============================================================================
CREATE TABLE IF NOT EXISTS peer_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    sector TEXT,
    companies TEXT,  -- JSON array of tickers: ["AAPL", "MSFT", "GOOGL"]
    avg_ev_ebitda REAL,
    avg_pe REAL,
    avg_peg REAL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- MODIFICATION: Add scenario_id to valuation_results
-- This links valuations to specific scenarios
-- ============================================================================
ALTER TABLE valuation_results ADD COLUMN scenario_id INTEGER DEFAULT 2;  -- Default to Base Case

-- ============================================================================
-- VIEWS: Convenient queries for common use cases
-- ============================================================================

-- View: Latest assumptions per company per scenario
CREATE VIEW IF NOT EXISTS v_latest_scenario_assumptions AS
SELECT
    s.name as scenario_name,
    s.type as scenario_type,
    c.name as company_name,
    c.ticker,
    sca.growth_rate_y1,
    sca.growth_rate_y2,
    sca.growth_rate_y3,
    sca.terminal_growth,
    sca.beta,
    sca.tax_rate,
    sca.confidence_level,
    sca.last_updated_at
FROM scenario_company_assumptions sca
JOIN scenarios s ON sca.scenario_id = s.id
JOIN companies c ON sca.company_id = c.id
WHERE s.is_active = 1;

-- View: Latest valuation per company per scenario
CREATE VIEW IF NOT EXISTS v_latest_valuations_by_scenario AS
SELECT
    s.name as scenario_name,
    s.type as scenario_type,
    c.name as company_name,
    c.ticker,
    vr.valuation_date,
    vr.final_equity_value,
    vr.final_price_per_share,
    vr.market_cap,
    vr.current_price,
    vr.upside_pct,
    vr.recommendation,
    vr.wacc
FROM valuation_results vr
JOIN scenarios s ON vr.scenario_id = s.id
JOIN companies c ON vr.company_id = c.id
WHERE vr.id IN (
    SELECT MAX(id)
    FROM valuation_results
    GROUP BY company_id, scenario_id
);

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================
SELECT 'Migration 001 completed successfully!' as status,
       'Created 5 scenario tables + 2 views' as details,
       '3 default scenarios (Bear/Base/Bull) initialized' as scenarios;
