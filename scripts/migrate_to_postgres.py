#!/usr/bin/env python3
"""
PostgreSQL Migration Script
Migrates valuation app from SQLite to PostgreSQL with authentication & security
"""

import sqlite3
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
from datetime import datetime

def log(message):
    """Simple logging"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

def migrate_sqlite_to_postgres():
    """Main migration function"""

    log("🚀 Starting Phase 0: Foundation Migration")
    log("=" * 60)

    # Step 1: Connect to SQLite
    log("Step 1: Reading data from SQLite...")
    try:
        sqlite_conn = sqlite3.connect('valuations.db')
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()
        log("✅ Connected to SQLite database")
    except Exception as e:
        log(f"❌ Error connecting to SQLite: {e}")
        return False

    # Step 2: Connect to PostgreSQL
    log("\nStep 2: Connecting to PostgreSQL...")
    try:
        pg_conn = psycopg2.connect(
            dbname='valuations_institutional',
            user='subhankarshukla',  # macOS username
            host='localhost'
        )
        pg_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        pg_cursor = pg_conn.cursor()
        log("✅ Connected to PostgreSQL database")
    except Exception as e:
        log(f"❌ Error connecting to PostgreSQL: {e}")
        log("   Make sure you ran: createdb valuations_institutional")
        return False

    # Step 3: Create tables in PostgreSQL
    log("\nStep 3: Creating PostgreSQL schema...")

    # Companies table
    pg_cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            ticker TEXT,
            sector TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    log("✅ Created companies table")

    # Company financials table
    pg_cursor.execute("""
        CREATE TABLE IF NOT EXISTS company_financials (
            id SERIAL PRIMARY KEY,
            company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
            revenue REAL,
            ebitda REAL,
            depreciation REAL,
            capex_pct REAL,
            working_capital_change REAL,
            profit_margin REAL,
            growth_rate_y1 REAL,
            growth_rate_y2 REAL,
            growth_rate_y3 REAL,
            terminal_growth REAL,
            tax_rate REAL,
            shares_outstanding REAL,
            debt REAL,
            cash REAL,
            market_cap_estimate REAL,
            beta REAL,
            risk_free_rate REAL,
            market_risk_premium REAL,
            country_risk_premium REAL,
            size_premium REAL,
            comparable_ev_ebitda REAL,
            comparable_pe REAL,
            comparable_peg REAL
        )
    """)
    log("✅ Created company_financials table")

    # Valuation results table
    pg_cursor.execute("""
        CREATE TABLE IF NOT EXISTS valuation_results (
            id SERIAL PRIMARY KEY,
            company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
            valuation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            dcf_equity_value REAL,
            dcf_price_per_share REAL,
            comp_ev_value REAL,
            comp_pe_value REAL,
            final_equity_value REAL,
            final_price_per_share REAL,
            market_cap REAL,
            current_price REAL,
            upside_pct REAL,
            recommendation TEXT,
            wacc REAL,
            ev_ebitda REAL,
            pe_ratio REAL,
            fcf_yield REAL,
            roe REAL,
            roic REAL,
            debt_to_equity REAL,
            z_score REAL,
            mc_p10 REAL,
            mc_p90 REAL,
            scenario_id INTEGER DEFAULT 2
        )
    """)
    log("✅ Created valuation_results table")

    # Step 4: Migrate data
    log("\nStep 4: Migrating data from SQLite to PostgreSQL...")

    # Migrate companies
    sqlite_cursor.execute("SELECT * FROM companies")
    companies = sqlite_cursor.fetchall()
    companies = [dict(c) for c in companies]
    for company in companies:
        pg_cursor.execute("""
            INSERT INTO companies (id, name, ticker, sector, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            company['id'], company['name'], company.get('ticker'),
            company.get('sector'), company.get('created_at'),
            company.get('updated_at')
        ))
    log(f"✅ Migrated {len(companies)} companies")

    # Migrate company_financials
    sqlite_cursor.execute("SELECT * FROM company_financials")
    financials = sqlite_cursor.fetchall()
    financials = [dict(f) for f in financials]
    for fin in financials:
        pg_cursor.execute("""
            INSERT INTO company_financials (
                company_id, revenue, ebitda, depreciation, capex_pct,
                working_capital_change, profit_margin, growth_rate_y1,
                growth_rate_y2, growth_rate_y3, terminal_growth, tax_rate,
                shares_outstanding, debt, cash, market_cap_estimate, beta,
                risk_free_rate, market_risk_premium, country_risk_premium,
                size_premium, comparable_ev_ebitda, comparable_pe, comparable_peg
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            fin['company_id'], fin.get('revenue'), fin.get('ebitda'),
            fin.get('depreciation'), fin.get('capex_pct'),
            fin.get('working_capital_change'), fin.get('profit_margin'),
            fin.get('growth_rate_y1'), fin.get('growth_rate_y2'),
            fin.get('growth_rate_y3'), fin.get('terminal_growth'),
            fin.get('tax_rate'), fin.get('shares_outstanding'),
            fin.get('debt'), fin.get('cash'), fin.get('market_cap_estimate'),
            fin.get('beta'), fin.get('risk_free_rate'),
            fin.get('market_risk_premium'), fin.get('country_risk_premium'),
            fin.get('size_premium'), fin.get('comparable_ev_ebitda'),
            fin.get('comparable_pe'), fin.get('comparable_peg')
        ))
    log(f"✅ Migrated {len(financials)} financial records")

    # Migrate valuation_results
    sqlite_cursor.execute("SELECT * FROM valuation_results")
    valuations = sqlite_cursor.fetchall()
    valuations = [dict(v) for v in valuations]
    for val in valuations:
        pg_cursor.execute("""
            INSERT INTO valuation_results (
                company_id, valuation_date, dcf_equity_value, dcf_price_per_share,
                comp_ev_value, comp_pe_value, final_equity_value,
                final_price_per_share, market_cap, current_price, upside_pct,
                recommendation, wacc, ev_ebitda, pe_ratio, fcf_yield, roe,
                roic, debt_to_equity, z_score, mc_p10, mc_p90, scenario_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            val['company_id'], val.get('valuation_date'),
            val.get('dcf_equity_value'), val.get('dcf_price_per_share'),
            val.get('comp_ev_value'), val.get('comp_pe_value'),
            val.get('final_equity_value'), val.get('final_price_per_share'),
            val.get('market_cap'), val.get('current_price'),
            val.get('upside_pct'), val.get('recommendation'),
            val.get('wacc'), val.get('ev_ebitda'), val.get('pe_ratio'),
            val.get('fcf_yield'), val.get('roe'), val.get('roic'),
            val.get('debt_to_equity'), val.get('z_score'),
            val.get('mc_p10'), val.get('mc_p90'), 2  # Default to Base Case
        ))
    log(f"✅ Migrated {len(valuations)} valuation records")

    # Step 5: Create users table for authentication
    log("\nStep 5: Creating authentication tables...")
    pg_cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'analyst' CHECK(role IN ('analyst', 'senior_analyst', 'admin')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    """)
    log("✅ Created users table")

    # Create default admin user (password: 'admin' - CHANGE THIS!)
    from werkzeug.security import generate_password_hash
    pg_cursor.execute("""
        INSERT INTO users (username, email, password_hash, role)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (username) DO NOTHING
    """, ('admin', 'admin@localhost', generate_password_hash('admin'), 'admin'))
    log("✅ Created default admin user (username: admin, password: admin)")
    log("   ⚠️  CHANGE THIS PASSWORD IMMEDIATELY!")

    # Step 6: Add optimistic locking columns
    log("\nStep 6: Adding optimistic locking...")
    pg_cursor.execute("ALTER TABLE companies ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1")
    pg_cursor.execute("ALTER TABLE company_financials ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1")
    log("✅ Added version columns for optimistic locking")

    # Step 7: Create indexes
    log("\nStep 7: Creating indexes for performance...")
    pg_cursor.execute("CREATE INDEX IF NOT EXISTS idx_companies_ticker ON companies(ticker)")
    pg_cursor.execute("CREATE INDEX IF NOT EXISTS idx_financials_company ON company_financials(company_id)")
    pg_cursor.execute("CREATE INDEX IF NOT EXISTS idx_valuations_company ON valuation_results(company_id)")
    pg_cursor.execute("CREATE INDEX IF NOT EXISTS idx_valuations_scenario ON valuation_results(scenario_id)")
    pg_cursor.execute("CREATE INDEX IF NOT EXISTS idx_valuations_date ON valuation_results(valuation_date)")
    log("✅ Created performance indexes")

    # Close connections
    sqlite_conn.close()
    pg_conn.close()

    log("\n" + "=" * 60)
    log("🎉 Migration completed successfully!")
    log("=" * 60)
    log("\n📊 Summary:")
    log(f"   • {len(companies)} companies migrated")
    log(f"   • {len(financials)} financial records migrated")
    log(f"   • {len(valuations)} valuations migrated")
    log(f"   • Authentication system created")
    log(f"   • Optimistic locking enabled")
    log(f"\n🔐 Default Login:")
    log(f"   Username: admin")
    log(f"   Password: admin")
    log(f"   ⚠️  Change this password immediately!")
    log(f"\n📝 Next steps:")
    log(f"   1. Update app.py to use PostgreSQL")
    log(f"   2. Add Flask-Login authentication")
    log(f"   3. Test the application")
    log(f"\nDatabase: postgresql://localhost/valuations_institutional")

    return True

if __name__ == '__main__':
    try:
        success = migrate_sqlite_to_postgres()
        sys.exit(0 if success else 1)
    except Exception as e:
        log(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
