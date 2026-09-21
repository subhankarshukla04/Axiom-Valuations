"""
Import companies from CSV files into the SQLite database
"""
import csv
import sqlite3
from datetime import datetime

def import_from_csv(csv_filename, db_filename='valuations.db'):
    """Import companies from CSV file into SQLite database"""
    
    conn = sqlite3.connect(db_filename)
    c = conn.cursor()
    
    try:
        with open(csv_filename, 'r') as file:
            reader = csv.DictReader(file)
            companies = list(reader)
        
        print(f"\n📊 Importing {len(companies)} companies from {csv_filename}")
        print("=" * 60)
        
        imported_count = 0
        
        for company in companies:
            name = company['name']
            sector = company.get('sector', 'Unknown')
            
            # Insert company
            c.execute('INSERT INTO companies (name, sector) VALUES (?, ?)', (name, sector))
            company_id = c.lastrowid
            
            # Helper to convert percentages to decimals
            def pct_to_decimal(value, default=0):
                """Convert percentage (22) to decimal (0.22)"""
                val = float(company.get(value, default))
                return val / 100 if val > 0 else 0
            
            # Insert financials (converting percentage fields to decimals)
            c.execute('''INSERT INTO company_financials (
                company_id, revenue, ebitda, depreciation, capex_pct, working_capital_change,
                profit_margin, growth_rate_y1, growth_rate_y2, growth_rate_y3, terminal_growth,
                tax_rate, shares_outstanding, debt, cash, market_cap_estimate, beta,
                risk_free_rate, market_risk_premium, country_risk_premium, size_premium,
                comparable_ev_ebitda, comparable_pe, comparable_peg
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (company_id, 
             float(company.get('revenue', 0)),
             float(company.get('ebitda', 0)),
             float(company.get('depreciation', 0)),
             pct_to_decimal('capex_pct', 5),
             float(company.get('working_capital_change', 0)),
             pct_to_decimal('profit_margin', 15),
             pct_to_decimal('growth_rate_y1', 10),
             pct_to_decimal('growth_rate_y2', 8),
             pct_to_decimal('growth_rate_y3', 5),
             pct_to_decimal('terminal_growth', 3),
             pct_to_decimal('tax_rate', 25),
             float(company.get('shares_outstanding', 1000000)),
             float(company.get('debt', 0)),
             float(company.get('cash', 0)),
             float(company.get('market_cap_estimate', 1000000)),
             float(company.get('beta', 1.0)),
             pct_to_decimal('risk_free_rate', 4.5),
             pct_to_decimal('market_risk_premium', 6.5),
             pct_to_decimal('country_risk_premium', 0),
             pct_to_decimal('size_premium', 0),
             float(company.get('comparable_ev_ebitda', 10)),
             float(company.get('comparable_pe', 15)),
             float(company.get('comparable_peg', 1.5))))
            
            print(f"✓ Imported: {name} ({sector})")
            imported_count += 1
        
        conn.commit()
        print("=" * 60)
        print(f"✅ Successfully imported {imported_count} companies!")
        
    except FileNotFoundError:
        print(f"❌ Error: File '{csv_filename}' not found.")
    except Exception as e:
        print(f"❌ Error importing data: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

def clear_database(db_filename='valuations.db'):
    """Clear all data from the database"""
    conn = sqlite3.connect(db_filename)
    c = conn.cursor()
    
    c.execute('DELETE FROM valuation_results')
    c.execute('DELETE FROM company_financials')
    c.execute('DELETE FROM companies')
    
    conn.commit()
    conn.close()
    print("🗑️  Database cleared successfully!")

if __name__ == '__main__':
    import sys
    
    print("\n" + "=" * 60)
    print("📁 CSV to SQLite Import Tool")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        # Try default files
        import os
        if os.path.exists('companies_enhanced.csv'):
            csv_file = 'companies_enhanced.csv'
        elif os.path.exists('companies.csv'):
            csv_file = 'companies.csv'
        else:
            print("\n❌ No CSV file found!")
            print("Usage: python3 import_csv.py <csv_filename>")
            print("\nOr place 'companies_enhanced.csv' or 'companies.csv' in the current directory")
            sys.exit(1)
    
    print(f"\n🎯 Target file: {csv_file}")
    
    # Ask if user wants to clear existing data
    response = input("\n⚠️  Clear existing database? (y/N): ").strip().lower()
    if response == 'y':
        clear_database()
    
    # Import the data
    import_from_csv(csv_file)
    
    print("\n✨ Import complete! Start the Flask app to view your companies.")
    print("   Run: python3 app.py\n")
