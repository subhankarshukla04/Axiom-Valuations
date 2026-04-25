#!/usr/bin/env python3
"""
Phase 1 Database Migration Script
Adds scenario management, macro assumptions, and audit trail tables
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import sys
from datetime import datetime

def get_connection():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='valuations_institutional',
            user='subhankarshukla'
        )
        return conn
    except Exception as e:
        print(f"❌ Error connecting to PostgreSQL: {e}")
        sys.exit(1)

def create_scenarios_table(cursor):
    """Create scenarios table"""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scenarios (
            id SERIAL PRIMARY KEY,
            company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            is_default BOOLEAN DEFAULT FALSE,
            created_by INTEGER REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            version INTEGER DEFAULT 1
        )
    ''')

    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_scenarios_company ON scenarios(company_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_scenarios_default ON scenarios(company_id, is_default)')

    print("✅ Created scenarios table")

def create_scenario_assumptions_table(cursor):
    """Create scenario_assumptions table"""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scenario_assumptions (
            id SERIAL PRIMARY KEY,
            scenario_id INTEGER REFERENCES scenarios(id) ON DELETE CASCADE,

            -- Growth rates
            growth_rate_y1 REAL,
            growth_rate_y2 REAL,
            growth_rate_y3 REAL,
            terminal_growth REAL,

            -- Margins & efficiency
            profit_margin REAL,
            ebitda_margin REAL,
            capex_pct REAL,

            -- Risk parameters
            beta REAL,
            risk_free_rate REAL,
            market_risk_premium REAL,
            size_premium REAL,
            country_risk_premium REAL,

            -- Capital structure
            target_debt_ratio REAL,
            credit_spread REAL,
            tax_rate REAL,

            -- Comparable multiples
            comparable_ev_ebitda REAL,
            comparable_pe REAL,
            comparable_peg REAL,

            -- Metadata
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            version INTEGER DEFAULT 1
        )
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_scenario_assumptions_scenario ON scenario_assumptions(scenario_id)')

    print("✅ Created scenario_assumptions table")

def create_macro_assumptions_table(cursor):
    """Create macro_assumptions table"""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS macro_assumptions (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL,
            description TEXT,

            -- Macro variables
            risk_free_rate REAL NOT NULL,
            market_risk_premium REAL NOT NULL,
            gdp_growth REAL NOT NULL,
            inflation_rate REAL NOT NULL,

            -- Credit spreads by rating
            credit_spread_aaa REAL,
            credit_spread_aa REAL,
            credit_spread_a REAL,
            credit_spread_bbb REAL,
            credit_spread_bb REAL,
            credit_spread_b REAL,

            -- Default tax rates
            corporate_tax_rate REAL,

            -- Market sentiment
            equity_risk_appetite REAL,

            -- Metadata
            is_active BOOLEAN DEFAULT FALSE,
            created_by INTEGER REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            version INTEGER DEFAULT 1
        )
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_macro_assumptions_active ON macro_assumptions(is_active)')

    print("✅ Created macro_assumptions table")

def create_sector_multiples_table(cursor):
    """Create sector_multiples table"""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sector_multiples (
            id SERIAL PRIMARY KEY,
            macro_assumption_id INTEGER REFERENCES macro_assumptions(id) ON DELETE CASCADE,
            sector VARCHAR(100) NOT NULL,

            -- Multiples
            ev_ebitda_avg REAL,
            ev_ebitda_median REAL,
            pe_avg REAL,
            pe_median REAL,
            peg_avg REAL,

            -- Metadata
            data_source VARCHAR(200),
            as_of_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sector_multiples_macro ON sector_multiples(macro_assumption_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sector_multiples_sector ON sector_multiples(sector)')

    print("✅ Created sector_multiples table")

def create_audit_log_table(cursor):
    """Create assumption_audit_log table"""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assumption_audit_log (
            id SERIAL PRIMARY KEY,

            -- What changed
            entity_type VARCHAR(50) NOT NULL,
            entity_id INTEGER NOT NULL,
            field_name VARCHAR(100) NOT NULL,
            old_value TEXT,
            new_value TEXT,

            -- Who changed it
            changed_by INTEGER REFERENCES users(id),
            user_role VARCHAR(50),

            -- When changed
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            -- Why changed (optional)
            change_reason TEXT,
            change_type VARCHAR(50),

            -- Context
            ip_address VARCHAR(45),
            user_agent TEXT,

            -- Impact assessment
            is_material BOOLEAN DEFAULT FALSE,

            CONSTRAINT chk_entity_type CHECK (entity_type IN ('company_financials', 'scenario_assumptions', 'macro_assumptions', 'sector_multiples'))
        )
    ''')

    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_entity ON assumption_audit_log(entity_type, entity_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_user ON assumption_audit_log(changed_by)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_date ON assumption_audit_log(changed_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_material ON assumption_audit_log(is_material)')

    print("✅ Created assumption_audit_log table")

def update_valuation_results_table(cursor):
    """Add scenario_id column to valuation_results"""
    # Check if column already exists
    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name='valuation_results' AND column_name='scenario_id'
    """)

    if cursor.fetchone() is None:
        cursor.execute('''
            ALTER TABLE valuation_results
            ADD COLUMN scenario_id INTEGER REFERENCES scenarios(id) ON DELETE SET NULL
        ''')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_valuations_scenario ON valuation_results(scenario_id)')

        print("✅ Updated valuation_results table with scenario_id")
    else:
        print("ℹ️  valuation_results already has scenario_id column")

def insert_default_macro_environments(cursor):
    """Insert default Bear/Base/Bull macro environments"""

    # Check if macro environments already exist
    cursor.execute("SELECT COUNT(*) as count FROM macro_assumptions")
    result = cursor.fetchone()
    count = result['count'] if result else 0

    if count > 0:
        print("ℹ️  Macro environments already exist, skipping defaults")
        return

    # Get admin user ID
    cursor.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1")
    admin_user = cursor.fetchone()
    admin_id = admin_user['id'] if admin_user else None

    macro_environments = [
        {
            'name': 'Base Case',
            'description': 'Current market conditions with moderate growth assumptions',
            'risk_free_rate': 0.045,
            'market_risk_premium': 0.065,
            'gdp_growth': 0.025,
            'inflation_rate': 0.030,
            'credit_spread_aaa': 0.005,
            'credit_spread_aa': 0.0075,
            'credit_spread_a': 0.0125,
            'credit_spread_bbb': 0.020,
            'credit_spread_bb': 0.035,
            'credit_spread_b': 0.050,
            'corporate_tax_rate': 0.21,
            'equity_risk_appetite': 1.0,
            'is_active': True
        },
        {
            'name': 'Bear Market',
            'description': 'Recession scenario with high rates, low growth, and wide credit spreads',
            'risk_free_rate': 0.060,
            'market_risk_premium': 0.080,
            'gdp_growth': 0.005,
            'inflation_rate': 0.025,
            'credit_spread_aaa': 0.010,
            'credit_spread_aa': 0.015,
            'credit_spread_a': 0.025,
            'credit_spread_bbb': 0.040,
            'credit_spread_bb': 0.065,
            'credit_spread_b': 0.100,
            'corporate_tax_rate': 0.21,
            'equity_risk_appetite': 1.3,
            'is_active': False
        },
        {
            'name': 'Bull Market',
            'description': 'Economic expansion with low rates, high growth, and tight credit spreads',
            'risk_free_rate': 0.030,
            'market_risk_premium': 0.055,
            'gdp_growth': 0.040,
            'inflation_rate': 0.035,
            'credit_spread_aaa': 0.003,
            'credit_spread_aa': 0.005,
            'credit_spread_a': 0.008,
            'credit_spread_bbb': 0.012,
            'credit_spread_bb': 0.020,
            'credit_spread_b': 0.030,
            'corporate_tax_rate': 0.21,
            'equity_risk_appetite': 0.8,
            'is_active': False
        }
    ]

    for env in macro_environments:
        cursor.execute('''
            INSERT INTO macro_assumptions (
                name, description, risk_free_rate, market_risk_premium,
                gdp_growth, inflation_rate, credit_spread_aaa, credit_spread_aa,
                credit_spread_a, credit_spread_bbb, credit_spread_bb, credit_spread_b,
                corporate_tax_rate, equity_risk_appetite, is_active, created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            env['name'], env['description'], env['risk_free_rate'], env['market_risk_premium'],
            env['gdp_growth'], env['inflation_rate'], env['credit_spread_aaa'], env['credit_spread_aa'],
            env['credit_spread_a'], env['credit_spread_bbb'], env['credit_spread_bb'], env['credit_spread_b'],
            env['corporate_tax_rate'], env['equity_risk_appetite'], env['is_active'], admin_id
        ))

    print("✅ Inserted default macro environments (Bear/Base/Bull)")

def insert_default_sector_multiples(cursor):
    """Insert default sector multiples for Base Case"""

    # Get Base Case macro ID
    cursor.execute("SELECT id FROM macro_assumptions WHERE name = 'Base Case'")
    result = cursor.fetchone()
    if not result:
        print("⚠️  Base Case macro environment not found, skipping sector multiples")
        return

    base_case_id = result['id']

    # Check if sector multiples already exist
    cursor.execute("SELECT COUNT(*) as count FROM sector_multiples WHERE macro_assumption_id = %s", (base_case_id,))
    result = cursor.fetchone()
    count = result['count'] if result else 0

    if count > 0:
        print("ℹ️  Sector multiples already exist, skipping defaults")
        return

    sectors = [
        {'sector': 'Technology', 'ev_ebitda_avg': 15.0, 'ev_ebitda_median': 14.5, 'pe_avg': 25.0, 'pe_median': 24.0, 'peg_avg': 1.8},
        {'sector': 'Healthcare', 'ev_ebitda_avg': 14.0, 'ev_ebitda_median': 13.5, 'pe_avg': 22.0, 'pe_median': 21.0, 'peg_avg': 1.9},
        {'sector': 'Financial Services', 'ev_ebitda_avg': 10.0, 'ev_ebitda_median': 9.5, 'pe_avg': 15.0, 'pe_median': 14.5, 'peg_avg': 1.5},
        {'sector': 'Consumer Cyclical', 'ev_ebitda_avg': 10.0, 'ev_ebitda_median': 9.8, 'pe_avg': 18.0, 'pe_median': 17.5, 'peg_avg': 1.6},
        {'sector': 'Consumer Defensive', 'ev_ebitda_avg': 11.0, 'ev_ebitda_median': 10.8, 'pe_avg': 20.0, 'pe_median': 19.5, 'peg_avg': 1.7},
        {'sector': 'Industrials', 'ev_ebitda_avg': 10.0, 'ev_ebitda_median': 9.7, 'pe_avg': 18.0, 'pe_median': 17.2, 'peg_avg': 1.6},
        {'sector': 'Energy', 'ev_ebitda_avg': 8.0, 'ev_ebitda_median': 7.5, 'pe_avg': 12.0, 'pe_median': 11.5, 'peg_avg': 1.2},
        {'sector': 'Utilities', 'ev_ebitda_avg': 9.0, 'ev_ebitda_median': 8.8, 'pe_avg': 16.0, 'pe_median': 15.5, 'peg_avg': 1.4},
        {'sector': 'Real Estate', 'ev_ebitda_avg': 12.0, 'ev_ebitda_median': 11.5, 'pe_avg': 25.0, 'pe_median': 24.0, 'peg_avg': 2.0},
        {'sector': 'Communication Services', 'ev_ebitda_avg': 12.0, 'ev_ebitda_median': 11.8, 'pe_avg': 20.0, 'pe_median': 19.5, 'peg_avg': 1.7}
    ]

    today = datetime.now().date()

    for sector_data in sectors:
        cursor.execute('''
            INSERT INTO sector_multiples (
                macro_assumption_id, sector, ev_ebitda_avg, ev_ebitda_median,
                pe_avg, pe_median, peg_avg, data_source, as_of_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            base_case_id, sector_data['sector'], sector_data['ev_ebitda_avg'], sector_data['ev_ebitda_median'],
            sector_data['pe_avg'], sector_data['pe_median'], sector_data['peg_avg'],
            'Market Research', today
        ))

    print("✅ Inserted default sector multiples for Base Case")

def generate_default_scenarios_for_companies(cursor):
    """Generate default Base scenario for each existing company"""

    # Get all companies
    cursor.execute("SELECT id FROM companies")
    companies = cursor.fetchall()

    if not companies:
        print("ℹ️  No companies found, skipping scenario generation")
        return

    # Get admin user ID
    cursor.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1")
    admin_user = cursor.fetchone()
    admin_id = admin_user['id'] if admin_user else None

    scenario_count = 0

    for company in companies:
        company_id = company['id']

        # Check if Base scenario already exists
        cursor.execute("""
            SELECT id FROM scenarios
            WHERE company_id = %s AND name = 'Base Case'
        """, (company_id,))

        if cursor.fetchone():
            continue  # Skip if already exists

        # Create Base scenario
        cursor.execute('''
            INSERT INTO scenarios (company_id, name, description, is_default, created_by)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            company_id,
            'Base Case',
            'Current assumptions from company financials',
            True,
            admin_id
        ))

        scenario_id = cursor.fetchone()['id']

        # Copy assumptions from company_financials
        cursor.execute('''
            INSERT INTO scenario_assumptions (
                scenario_id, growth_rate_y1, growth_rate_y2, growth_rate_y3, terminal_growth,
                profit_margin, capex_pct, beta, risk_free_rate, market_risk_premium,
                size_premium, country_risk_premium, tax_rate,
                comparable_ev_ebitda, comparable_pe, comparable_peg
            )
            SELECT
                %s, growth_rate_y1, growth_rate_y2, growth_rate_y3, terminal_growth,
                profit_margin, capex_pct, beta, risk_free_rate, market_risk_premium,
                size_premium, country_risk_premium, tax_rate,
                comparable_ev_ebitda, comparable_pe, comparable_peg
            FROM company_financials
            WHERE company_id = %s
        ''', (scenario_id, company_id))

        scenario_count += 1

    print(f"✅ Generated {scenario_count} default Base scenarios for companies")

def main():
    """Run Phase 1 migration"""
    print("=" * 80)
    print("🚀 PHASE 1 DATABASE MIGRATION - SCENARIO MANAGEMENT")
    print("=" * 80)
    print()

    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Step 1: Create tables
        print("Step 1: Creating scenario management tables...")
        create_scenarios_table(cursor)
        create_scenario_assumptions_table(cursor)
        print()

        # Step 2: Create macro assumptions tables
        print("Step 2: Creating macro assumptions tables...")
        create_macro_assumptions_table(cursor)
        create_sector_multiples_table(cursor)
        print()

        # Step 3: Create audit log table
        print("Step 3: Creating audit trail table...")
        create_audit_log_table(cursor)
        print()

        # Step 4: Update valuation_results
        print("Step 4: Updating valuation_results table...")
        update_valuation_results_table(cursor)
        print()

        # Step 5: Insert default data
        print("Step 5: Inserting default macro environments...")
        insert_default_macro_environments(cursor)
        print()

        # Step 6: Insert sector multiples
        print("Step 6: Inserting default sector multiples...")
        insert_default_sector_multiples(cursor)
        print()

        # Step 7: Generate default scenarios
        print("Step 7: Generating default scenarios for companies...")
        generate_default_scenarios_for_companies(cursor)
        print()

        # Commit changes
        conn.commit()

        # Get counts
        cursor.execute("SELECT COUNT(*) as count FROM scenarios")
        scenario_count = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM macro_assumptions")
        macro_count = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM sector_multiples")
        sector_count = cursor.fetchone()['count']

        print("=" * 80)
        print("🎉 PHASE 1 MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print()
        print("📊 Summary:")
        print(f"   • {scenario_count} scenarios created")
        print(f"   • {macro_count} macro environments created")
        print(f"   • {sector_count} sector multiples added")
        print(f"   • Audit trail system enabled")
        print()
        print("✅ Next Steps:")
        print("   1. Restart the Flask application")
        print("   2. Navigate to http://localhost:5001")
        print("   3. Go to any company and click 'Scenarios' tab")
        print("   4. Use 'Macro Settings' to switch environments")
        print("   5. View 'Audit Trail' to see all changes")
        print()
        print("📖 Documentation:")
        print("   • Read PHASE1_ROADMAP.md for full feature overview")
        print("   • Check SCENARIO_GUIDE.md for user guide (coming soon)")
        print()

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    main()
