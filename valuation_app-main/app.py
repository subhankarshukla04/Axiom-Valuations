from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
import json
from datetime import datetime
import io
import csv
import logging
from pydantic import ValidationError
from models import CompanyCreate, CompanyUpdate
from valuation_service import ValuationService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Initialize valuation service
valuation_service = ValuationService()

# Database initialization
def init_db():
    conn = sqlite3.connect('valuations.db')
    c = conn.cursor()
    
    # Companies table
    c.execute('''CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        sector TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Company financials table
    c.execute('''CREATE TABLE IF NOT EXISTS company_financials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
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
        comparable_peg REAL,
        FOREIGN KEY (company_id) REFERENCES companies (id)
    )''')
    
    # Valuation results table
    c.execute('''CREATE TABLE IF NOT EXISTS valuation_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
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
        FOREIGN KEY (company_id) REFERENCES companies (id)
    )''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/companies', methods=['GET'])
def get_companies():
    conn = sqlite3.connect('valuations.db')
    c = conn.cursor()
    c.execute('''SELECT c.id, c.name, c.sector, c.created_at,
                 vr.final_equity_value, vr.recommendation, vr.upside_pct,
                 vr.pe_ratio, vr.roe, vr.z_score, vr.market_cap, 
                 vr.current_price, vr.wacc, vr.ev_ebitda, vr.roic,
                 vr.fcf_yield, vr.debt_to_equity
                 FROM companies c
                 LEFT JOIN valuation_results vr ON c.id = vr.company_id
                 AND vr.id = (SELECT MAX(id) FROM valuation_results WHERE company_id = c.id)
                 ORDER BY c.created_at DESC''')
    
    companies = []
    for row in c.fetchall():
        companies.append({
            'id': row[0],
            'name': row[1],
            'sector': row[2],
            'created_at': row[3],
            'fair_value': row[4],
            'recommendation': row[5],
            'upside': row[6],
            'pe_ratio': row[7],
            'roe': row[8],
            'z_score': row[9],
            'market_cap': row[10],
            'current_price': row[11],
            'wacc': row[12],
            'ev_ebitda': row[13],
            'roic': row[14],
            'fcf_yield': row[15],
            'debt_to_equity': row[16]
        })
    
    conn.close()
    return jsonify(companies)

@app.route('/api/company/<int:company_id>', methods=['GET'])
def get_company(company_id):
    conn = sqlite3.connect('valuations.db')
    c = conn.cursor()
    
    # Get company info
    c.execute('SELECT * FROM companies WHERE id = ?', (company_id,))
    company_row = c.fetchone()
    
    if not company_row:
        conn.close()
        return jsonify({'error': 'Company not found'}), 404
    
    # Get financials
    c.execute('SELECT * FROM company_financials WHERE company_id = ?', (company_id,))
    financials_row = c.fetchone()
    
    # Get latest valuation
    c.execute('SELECT * FROM valuation_results WHERE company_id = ? ORDER BY valuation_date DESC LIMIT 1', (company_id,))
    valuation_row = c.fetchone()
    
    conn.close()
    
    company_data = {
        'id': company_row[0],
        'name': company_row[1],
        'sector': company_row[2],
        'financials': dict(zip([
            'id', 'company_id', 'revenue', 'ebitda', 'depreciation', 'capex_pct',
            'working_capital_change', 'profit_margin', 'growth_rate_y1', 'growth_rate_y2',
            'growth_rate_y3', 'terminal_growth', 'tax_rate', 'shares_outstanding',
            'debt', 'cash', 'market_cap_estimate', 'beta', 'risk_free_rate',
            'market_risk_premium', 'country_risk_premium', 'size_premium',
            'comparable_ev_ebitda', 'comparable_pe', 'comparable_peg'
        ], financials_row)) if financials_row else None,
        'valuation': dict(zip([
            'id', 'company_id', 'valuation_date', 'dcf_equity_value', 'dcf_price_per_share',
            'comp_ev_value', 'comp_pe_value', 'final_equity_value', 'final_price_per_share',
            'market_cap', 'current_price', 'upside_pct', 'recommendation', 'wacc',
            'ev_ebitda', 'pe_ratio', 'fcf_yield', 'roe', 'roic', 'debt_to_equity',
            'z_score', 'mc_p10', 'mc_p90'
        ], valuation_row)) if valuation_row else None
    }
    
    return jsonify(company_data)

@app.route('/api/company', methods=['POST'])
def create_company():
    try:
        data = request.json
        
        # Validate input with Pydantic
        company_data = CompanyCreate(**data)
        logger.info(f"Creating company: {company_data.name}")
        
        conn = sqlite3.connect('valuations.db')
        c = conn.cursor()
        
        # Insert company
        c.execute('INSERT INTO companies (name, sector) VALUES (?, ?)',
                  (company_data.name, company_data.sector))
        company_id = c.lastrowid
        
        # Insert financials
        c.execute('''INSERT INTO company_financials (
            company_id, revenue, ebitda, depreciation, capex_pct, working_capital_change,
            profit_margin, growth_rate_y1, growth_rate_y2, growth_rate_y3, terminal_growth,
            tax_rate, shares_outstanding, debt, cash, market_cap_estimate, beta,
            risk_free_rate, market_risk_premium, country_risk_premium, size_premium,
            comparable_ev_ebitda, comparable_pe, comparable_peg
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (company_id, company_data.revenue, company_data.ebitda,
         company_data.depreciation, company_data.capex_pct,
         company_data.working_capital_change, company_data.profit_margin,
         company_data.growth_rate_y1, company_data.growth_rate_y2,
         company_data.growth_rate_y3, company_data.terminal_growth,
         company_data.tax_rate, company_data.shares_outstanding,
         company_data.debt, company_data.cash, company_data.market_cap_estimate,
         company_data.beta, company_data.risk_free_rate,
         company_data.market_risk_premium, company_data.country_risk_premium,
         company_data.size_premium, company_data.comparable_ev_ebitda,
         company_data.comparable_pe, company_data.comparable_peg))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Company created successfully with ID: {company_id}")
        return jsonify({'id': company_id, 'message': 'Company created successfully'}), 201
        
    except ValidationError as e:
        logger.warning(f"Validation error creating company: {str(e)}")
        # Convert Pydantic errors to JSON-serializable format
        errors = []
        for err in e.errors():
            errors.append({
                'field': err['loc'][-1] if err['loc'] else 'unknown',
                'message': err['msg'],
                'type': err['type']
            })
        return jsonify({
            'error': 'Validation failed',
            'details': errors
        }), 400
    except Exception as e:
        logger.error(f"Error creating company: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/company/<int:company_id>', methods=['PUT'])
def update_company(company_id):
    try:
        data = request.json
        
        # Validate input with Pydantic
        company_data = CompanyUpdate(**data)
        logger.info(f"Updating company ID {company_id}: {company_data.name}")
        
        conn = sqlite3.connect('valuations.db')
        c = conn.cursor()
        
        # Update company
        c.execute('UPDATE companies SET name = ?, sector = ?, updated_at = ? WHERE id = ?',
                  (company_data.name, company_data.sector, datetime.now().isoformat(), company_id))
        
        # Update financials
        c.execute('''UPDATE company_financials SET
            revenue = ?, ebitda = ?, depreciation = ?, capex_pct = ?,
            working_capital_change = ?, profit_margin = ?, growth_rate_y1 = ?,
            growth_rate_y2 = ?, growth_rate_y3 = ?, terminal_growth = ?,
            tax_rate = ?, shares_outstanding = ?, debt = ?, cash = ?,
            market_cap_estimate = ?, beta = ?, risk_free_rate = ?,
            market_risk_premium = ?, country_risk_premium = ?, size_premium = ?,
            comparable_ev_ebitda = ?, comparable_pe = ?, comparable_peg = ?
            WHERE company_id = ?''',
        (company_data.revenue, company_data.ebitda,
         company_data.depreciation, company_data.capex_pct,
         company_data.working_capital_change, company_data.profit_margin,
         company_data.growth_rate_y1, company_data.growth_rate_y2,
         company_data.growth_rate_y3, company_data.terminal_growth,
         company_data.tax_rate, company_data.shares_outstanding,
         company_data.debt, company_data.cash, company_data.market_cap_estimate,
         company_data.beta, company_data.risk_free_rate,
         company_data.market_risk_premium, company_data.country_risk_premium,
         company_data.size_premium, company_data.comparable_ev_ebitda,
         company_data.comparable_pe, company_data.comparable_peg, company_id))
        
        conn.commit()
        conn.close()
        
        # 🚨 CRITICAL: Auto-revaluation after financial data update
        logger.info(f"Triggering automatic revaluation for company ID {company_id}")
        success, results, error_msg = valuation_service.valuate_company(company_id)
        
        if success:
            logger.info(f"Auto-revaluation successful for company ID {company_id}")
            return jsonify({
                'message': 'Company updated and revalued successfully',
                'valuation': results
            })
        else:
            logger.warning(f"Auto-revaluation failed for company ID {company_id}: {error_msg}")
            return jsonify({
                'message': 'Company updated but revaluation failed',
                'error': error_msg
            }), 207  # 207 Multi-Status: partial success
            
    except ValidationError as e:
        logger.warning(f"Validation error updating company {company_id}: {str(e)}")
        # Convert Pydantic errors to JSON-serializable format
        errors = []
        for err in e.errors():
            errors.append({
                'field': err['loc'][-1] if err['loc'] else 'unknown',
                'message': err['msg'],
                'type': err['type']
            })
        return jsonify({
            'error': 'Validation failed',
            'details': errors
        }), 400
    except Exception as e:
        logger.error(f"Error updating company {company_id}: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/company/<int:company_id>', methods=['DELETE'])
def delete_company(company_id):
    conn = sqlite3.connect('valuations.db')
    c = conn.cursor()
    
    c.execute('DELETE FROM valuation_results WHERE company_id = ?', (company_id,))
    c.execute('DELETE FROM company_financials WHERE company_id = ?', (company_id,))
    c.execute('DELETE FROM companies WHERE id = ?', (company_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Company deleted successfully'})

@app.route('/api/valuation/<int:company_id>', methods=['POST'])
def run_valuation(company_id):
    try:
        logger.info(f"Manual valuation requested for company ID {company_id}")
        
        # Use centralized service
        success, results, error_msg = valuation_service.valuate_company(company_id)
        
        if success:
            logger.info(f"Valuation completed successfully for company ID {company_id}")
            return jsonify(results)
        else:
            logger.error(f"Valuation failed for company ID {company_id}: {error_msg}")
            return jsonify({'error': error_msg}), 404 if 'not found' in error_msg else 500
            
    except Exception as e:
        logger.error(f"Unexpected error during valuation for company ID {company_id}: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    conn = sqlite3.connect('valuations.db')
    c = conn.cursor()
    
    c.execute('''SELECT c.name, c.sector, vr.*
                 FROM companies c
                 JOIN valuation_results vr ON c.id = vr.company_id
                 WHERE vr.id IN (
                     SELECT MAX(id) FROM valuation_results GROUP BY company_id
                 )''')
    
    rows = c.fetchall()
    conn.close()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'Company', 'Sector', 'DCF Value', 'DCF Price/Share', 'Fair Value',
        'Fair Price/Share', 'Market Cap', 'Current Price', 'Upside %',
        'Recommendation', 'WACC %', 'EV/EBITDA', 'P/E', 'FCF Yield %',
        'ROE %', 'ROIC %', 'Debt/Equity', 'Z-Score'
    ])
    
    # Data
    for row in rows:
        writer.writerow([
            row[0], row[1], row[3], row[4], row[7], row[8], row[9], row[10],
            row[11], row[12], row[13], row[14], row[15], row[16], row[17],
            row[18], row[19], row[20]
        ])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'valuations_{datetime.now().strftime("%Y%m%d")}.csv'
    )

@app.route('/api/dashboard/stats', methods=['GET'])
def dashboard_stats():
    conn = sqlite3.connect('valuations.db')
    c = conn.cursor()
    
    # Get portfolio statistics
    c.execute('''SELECT 
        COUNT(DISTINCT c.id) as total_companies,
        AVG(vr.upside_pct) as avg_upside,
        SUM(CASE WHEN vr.recommendation IN ('BUY', 'STRONG BUY') THEN 1 ELSE 0 END) as buy_count,
        SUM(CASE WHEN vr.recommendation = 'HOLD' THEN 1 ELSE 0 END) as hold_count,
        SUM(CASE WHEN vr.recommendation IN ('SELL', 'UNDERWEIGHT') THEN 1 ELSE 0 END) as sell_count,
        AVG(vr.pe_ratio) as avg_pe,
        AVG(vr.roe) as avg_roe,
        SUM(vr.final_equity_value) as total_fair_value,
        SUM(vr.market_cap) as total_market_cap,
        AVG(vr.wacc) as avg_wacc
        FROM companies c
        JOIN valuation_results vr ON c.id = vr.company_id
        WHERE vr.id IN (
            SELECT MAX(id) FROM valuation_results GROUP BY company_id
        )''')
    
    stats = c.fetchone()
    
    # Get sector breakdown with P/E
    c.execute('''SELECT c.sector, COUNT(*), AVG(vr.upside_pct), AVG(vr.roe), AVG(vr.pe_ratio)
                 FROM companies c
                 JOIN valuation_results vr ON c.id = vr.company_id
                 WHERE vr.id IN (
                     SELECT MAX(id) FROM valuation_results GROUP BY company_id
                 )
                 GROUP BY c.sector''')
    
    sectors = c.fetchall()
    conn.close()
    
    return jsonify({
        'total_companies': stats[0] or 0,
        'avg_upside': round(stats[1] or 0, 2),
        'buy_count': stats[2] or 0,
        'hold_count': stats[3] or 0,
        'sell_count': stats[4] or 0,
        'avg_pe': round(stats[5] or 0, 1),
        'avg_roe': round(stats[6] or 0, 1),
        'total_fair_value': stats[7] or 0,
        'total_market_cap': stats[8] or 0,
        'avg_wacc': round(stats[9] or 0, 2),
        'sectors': [{'name': s[0], 'count': s[1], 'avg_upside': round(s[2] or 0, 2), 'avg_roe': round(s[3] or 0, 1), 'avg_pe': round(s[4] or 0, 1)} for s in sectors]
    })

if __name__ == '__main__':
    # Use port 5001 to avoid conflict with macOS AirPlay Receiver on port 5000
    app.run(debug=True, port=5001)
