// Global state
let currentCompanyId = null;

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    loadDashboard();
    loadCompanies();
    
    // Form submission
    document.getElementById('company-form').addEventListener('submit', saveCompany);
});

// View management
function showView(viewName) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
    
    document.getElementById(`${viewName}-view`).classList.add('active');
    event.target.classList.add('active');
    
    if (viewName === 'dashboard') {
        loadDashboard();
    } else if (viewName === 'companies') {
        loadCompanies();
    }
}

// Dashboard functions
async function loadDashboard() {
    try {
        const response = await fetch('/api/dashboard/stats');
        const stats = await response.json();
        
        document.getElementById('total-companies').textContent = stats.total_companies;
        document.getElementById('avg-upside').textContent = `${stats.avg_upside.toFixed(1)}%`;
        document.getElementById('avg-pe').textContent = `${stats.avg_pe.toFixed(1)}x`;
        document.getElementById('avg-roe').textContent = `${stats.avg_roe.toFixed(1)}%`;
        
        document.getElementById('buy-count').textContent = stats.buy_count;
        document.getElementById('hold-count').textContent = stats.hold_count;
        document.getElementById('sell-count').textContent = stats.sell_count;
        
        // Sector breakdown
        const sectorHtml = stats.sectors.map(sector => `
            <div class="sector-item">
                <strong>${sector.name}</strong>
                <span>${sector.count} companies</span>
                <span>Upside: ${sector.avg_upside.toFixed(1)}%</span>
                <span>ROE: ${sector.avg_roe.toFixed(1)}%</span>
            </div>
        `).join('');
        
        document.getElementById('sector-breakdown').innerHTML = sectorHtml;
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Companies functions
async function loadCompanies() {
    try {
        const response = await fetch('/api/companies');
        const companies = await response.json();
        
        const companiesHtml = companies.map(company => {
            const recClass = getRecommendationClass(company.recommendation);
            const upsideColor = company.upside >= 0 ? '#38ef7d' : '#dc3545';
            
            return `
                <div class="company-card">
                    <div class="company-header">
                        <div>
                            <div class="company-name">${company.name}</div>
                            <span class="company-sector">${company.sector || 'N/A'}</span>
                        </div>
                    </div>
                    
                    ${company.fair_value ? `
                        <div class="company-metrics">
                            <div class="metric">
                                <div class="metric-label">Fair Value</div>
                                <div class="metric-value">$${formatNumber(company.fair_value)}</div>
                            </div>
                            <div class="metric">
                                <div class="metric-label">Upside</div>
                                <div class="metric-value" style="color: ${upsideColor}">${company.upside?.toFixed(1)}%</div>
                            </div>
                        </div>
                        
                        <div class="recommendation-badge ${recClass}">
                            ${company.recommendation || 'N/A'}
                        </div>
                    ` : '<p style="text-align: center; color: #999; padding: 1rem;">No valuation yet</p>'}
                    
                    <div class="company-actions">
                        <button class="btn btn-primary btn-small" onclick="runValuation(${company.id})">
                            ${company.fair_value ? 'Revalue' : 'Value'}
                        </button>
                        <button class="btn btn-secondary btn-small" onclick="editCompany(${company.id})">Edit</button>
                        <button class="btn btn-danger btn-small" onclick="deleteCompany(${company.id})">Delete</button>
                    </div>
                </div>
            `;
        }).join('');
        
        document.getElementById('companies-grid').innerHTML = companiesHtml || '<p>No companies yet. Add your first company!</p>';
    } catch (error) {
        console.error('Error loading companies:', error);
    }
}

function getRecommendationClass(recommendation) {
    if (!recommendation) return '';
    const rec = recommendation.toLowerCase();
    if (rec.includes('buy')) return 'buy';
    if (rec.includes('hold')) return 'hold';
    return 'sell';
}

function formatNumber(num) {
    if (!num) return '0';
    if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
    return num.toFixed(2);
}

// Modal functions
function showAddCompanyModal() {
    currentCompanyId = null;
    document.getElementById('modal-title').textContent = 'Add Company';
    document.getElementById('company-form').reset();
    document.getElementById('company-id').value = '';
    
    // Set defaults
    document.getElementById('risk_free_rate').value = 4.5;
    document.getElementById('market_risk_premium').value = 6.5;
    document.getElementById('country_risk_premium').value = 0;
    
    document.getElementById('company-modal').classList.add('active');
}

async function editCompany(companyId) {
    try {
        const response = await fetch(`/api/company/${companyId}`);
        const company = await response.json();
        
        currentCompanyId = companyId;
        document.getElementById('modal-title').textContent = 'Edit Company';
        document.getElementById('company-id').value = companyId;
        
        // Fill form
        document.getElementById('name').value = company.name;
        document.getElementById('sector').value = company.sector;
        
        if (company.financials) {
            // Fields that are stored as decimals but displayed as percentages
            const percentageFields = [
                'capex_pct', 'profit_margin', 'growth_rate_y1', 'growth_rate_y2', 'growth_rate_y3',
                'terminal_growth', 'tax_rate', 'risk_free_rate', 'market_risk_premium',
                'country_risk_premium', 'size_premium'
            ];
            
            const fields = [
                'revenue', 'ebitda', 'depreciation', 'capex_pct', 'working_capital_change',
                'profit_margin', 'growth_rate_y1', 'growth_rate_y2', 'growth_rate_y3',
                'terminal_growth', 'tax_rate', 'shares_outstanding', 'debt', 'cash',
                'market_cap_estimate', 'beta', 'risk_free_rate', 'market_risk_premium',
                'country_risk_premium', 'size_premium', 'comparable_ev_ebitda',
                'comparable_pe', 'comparable_peg'
            ];
            
            fields.forEach(field => {
                const element = document.getElementById(field);
                if (element && company.financials[field] != null) {
                    // Convert decimals to percentages for display
                    const value = percentageFields.includes(field) 
                        ? (company.financials[field] * 100)
                        : company.financials[field];
                    element.value = value;
                }
            });
        }
        
        document.getElementById('company-modal').classList.add('active');
    } catch (error) {
        console.error('Error loading company:', error);
        alert('Error loading company data');
    }
}

function closeModal() {
    document.getElementById('company-modal').classList.remove('active');
}

function closeValuationModal() {
    document.getElementById('valuation-modal').classList.remove('active');
}

async function saveCompany(e) {
    e.preventDefault();
    
    const companyId = document.getElementById('company-id').value;
    
    // Helper to convert percentage to decimal - ALWAYS divides by 100
    // Form displays percentages (25 = 25%), backend expects decimals (0.25)
    const pct = (val, defaultVal = 0) => {
        const num = parseFloat(val) || defaultVal;
        return num / 100;
    };
    
    // Flat structure matching Pydantic model
    const data = {
        name: document.getElementById('name').value,
        sector: document.getElementById('sector').value,
        revenue: parseFloat(document.getElementById('revenue').value) || 0,
        ebitda: parseFloat(document.getElementById('ebitda').value) || 0,
        depreciation: parseFloat(document.getElementById('depreciation').value) || 0,
        capex_pct: pct(document.getElementById('capex_pct').value, 5),
        working_capital_change: parseFloat(document.getElementById('working_capital_change').value) || 0,
        profit_margin: pct(document.getElementById('profit_margin').value, 15),
        growth_rate_y1: pct(document.getElementById('growth_rate_y1').value, 20),
        growth_rate_y2: pct(document.getElementById('growth_rate_y2').value, 15),
        growth_rate_y3: pct(document.getElementById('growth_rate_y3').value, 10),
        terminal_growth: pct(document.getElementById('terminal_growth').value, 3),
        tax_rate: pct(document.getElementById('tax_rate').value, 25),
        shares_outstanding: parseFloat(document.getElementById('shares_outstanding').value) || 1000000,
        debt: parseFloat(document.getElementById('debt').value) || 0,
        cash: parseFloat(document.getElementById('cash').value) || 0,
        market_cap_estimate: parseFloat(document.getElementById('market_cap_estimate').value) || 1000000,
        beta: parseFloat(document.getElementById('beta').value) || 1.0,
        risk_free_rate: pct(document.getElementById('risk_free_rate').value, 4.5),
        market_risk_premium: pct(document.getElementById('market_risk_premium').value, 6.5),
        country_risk_premium: pct(document.getElementById('country_risk_premium').value, 0),
        size_premium: pct(document.getElementById('size_premium').value, 0),
        comparable_ev_ebitda: parseFloat(document.getElementById('comparable_ev_ebitda').value) || 10,
        comparable_pe: parseFloat(document.getElementById('comparable_pe').value) || 15,
        comparable_peg: parseFloat(document.getElementById('comparable_peg').value) || 1.5
    };
    
    try {
        const url = companyId ? `/api/company/${companyId}` : '/api/company';
        const method = companyId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            if (error.details) {
                // Pydantic validation errors
                let errorMsg = 'Validation errors:\\n\\n';
                error.details.forEach(err => {
                    const field = err.loc[err.loc.length - 1];
                    errorMsg += `• ${field}: ${err.msg}\\n`;
                });
                alert(errorMsg);
            } else {
                alert(error.error || 'Error saving company');
            }
            return;
        }
        
        const result = await response.json();
        
        closeModal();
        
        // For edits, automatically run valuation and show results
        if (companyId) {
            showLoadingState('Revaluing company with updated data...');
            try {
                const valResponse = await fetch(`/api/valuation/${companyId}`, { method: 'POST' });
                const valResult = await valResponse.json();
                hideLoadingState();
                showValuationResults(valResult, data.name);
            } catch (error) {
                hideLoadingState();
                console.error('Error running valuation:', error);
            }
        } else {
            alert('Company created successfully! Click "Revalue" to generate valuation.');
        }
        
        loadCompanies();
        loadDashboard();
    } catch (error) {
        console.error('Error saving company:', error);
        alert('Error saving company');
    }
}

async function deleteCompany(companyId) {
    if (!confirm('Are you sure you want to delete this company?')) return;
    
    try {
        const response = await fetch(`/api/company/${companyId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            loadCompanies();
            loadDashboard();
            alert('Company deleted successfully!');
        } else {
            alert('Error deleting company');
        }
    } catch (error) {
        console.error('Error deleting company:', error);
        alert('Error deleting company');
    }
}

// Valuation functions
async function runValuation(companyId) {
    try {
        // Show professional loading spinner
        const loadingHtml = `
            <div class="loading-container">
                <div class="spinner"></div>
                <h3>Running CFA-Level Valuation</h3>
                <p>Calculating DCF, WACC, Monte Carlo simulations...</p>
                <p class="loading-subtext">This may take 5-10 seconds</p>
            </div>
        `;
        document.getElementById('valuation-results').innerHTML = loadingHtml;
        document.getElementById('valuation-modal').classList.add('active');
        
        const response = await fetch(`/api/valuation/${companyId}`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Valuation failed');
        }
        
        const result = await response.json();
        
        displayValuationResults(result);
        loadCompanies();
        loadDashboard();
    } catch (error) {
        console.error('Error running valuation:', error);
        const errorHtml = `
            <div class="error-container">
                <h3>❌ Valuation Failed</h3>
                <p class="error-message">${error.message}</p>
                <button onclick="closeValuationModal()" class="btn">Close</button>
            </div>
        `;
        document.getElementById('valuation-results').innerHTML = errorHtml;
    }
}

function displayValuationResults(result) {
    document.getElementById('valuation-company-name').textContent = result.name;
    
    const recClass = getRecommendationClass(result.recommendation);
    const upsideColor = result.upside_pct >= 0 ? '#38ef7d' : '#dc3545';
    
    const html = `
        <div class="final-recommendation">
            <h2>Investment Recommendation</h2>
            <div class="recommendation-value">${result.recommendation}</div>
            <div class="upside-value" style="color: ${upsideColor}">
                ${result.upside_pct >= 0 ? '+' : ''}${result.upside_pct.toFixed(1)}% Upside/Downside
            </div>
        </div>
        
        <div class="valuation-section">
            <h3>Valuation Summary</h3>
            <div class="valuation-grid">
                <div class="valuation-item">
                    <div class="valuation-item-label">Fair Value</div>
                    <div class="valuation-item-value">$${formatNumber(result.final_equity_value)}</div>
                </div>
                <div class="valuation-item">
                    <div class="valuation-item-label">Fair Price/Share</div>
                    <div class="valuation-item-value">$${result.final_price_per_share.toFixed(2)}</div>
                </div>
                <div class="valuation-item">
                    <div class="valuation-item-label">Current Market Cap</div>
                    <div class="valuation-item-value">$${formatNumber(result.market_cap)}</div>
                </div>
                <div class="valuation-item">
                    <div class="valuation-item-label">Current Price</div>
                    <div class="valuation-item-value">$${result.current_price.toFixed(2)}</div>
                </div>
            </div>
        </div>
        
        <div class="valuation-section">
            <h3>Valuation Methods Comparison</h3>
            <canvas id="valuationChart" style="max-height: 300px;"></canvas>
        </div>
        
        <div class="valuation-section">
            <h3>Key Metrics</h3>
            <div class="valuation-grid">
                <div class="valuation-item">
                    <div class="valuation-item-label">WACC</div>
                    <div class="valuation-item-value">${result.wacc.toFixed(2)}%</div>
                </div>
                <div class="valuation-item">
                    <div class="valuation-item-label">EV/EBITDA</div>
                    <div class="valuation-item-value">${result.ev_ebitda.toFixed(1)}x</div>
                </div>
                <div class="valuation-item">
                    <div class="valuation-item-label">P/E Ratio</div>
                    <div class="valuation-item-value">${result.pe_ratio.toFixed(1)}x</div>
                </div>
                <div class="valuation-item">
                    <div class="valuation-item-label">FCF Yield</div>
                    <div class="valuation-item-value">${result.fcf_yield.toFixed(2)}%</div>
                </div>
                <div class="valuation-item">
                    <div class="valuation-item-label">ROE</div>
                    <div class="valuation-item-value">${result.roe.toFixed(1)}%</div>
                </div>
                <div class="valuation-item">
                    <div class="valuation-item-label">ROIC</div>
                    <div class="valuation-item-value">${result.roic.toFixed(1)}%</div>
                </div>
                <div class="valuation-item">
                    <div class="valuation-item-label">Debt/Equity</div>
                    <div class="valuation-item-value">${result.debt_to_equity.toFixed(2)}x</div>
                </div>
                <div class="valuation-item">
                    <div class="valuation-item-label">Z-Score</div>
                    <div class="valuation-item-value">${result.z_score.toFixed(2)}</div>
                </div>
            </div>
        </div>
        
        <div class="valuation-section">
            <h3>Monte Carlo Risk Analysis</h3>
            <canvas id="monteCarloChart" style="max-height: 250px;"></canvas>
        </div>
    `;
    
    document.getElementById('valuation-results').innerHTML = html;
    
    // Render Chart.js visualizations
    setTimeout(() => {
        renderValuationChart(result);
        renderMonteCarloChart(result);
    }, 100);
}

// Chart.js visualization functions
function renderValuationChart(result) {
    const ctx = document.getElementById('valuationChart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['DCF Method', 'EV/EBITDA', 'P/E Method', 'Current Market Cap'],
            datasets: [{
                label: 'Valuation ($M)',
                data: [
                    (result.dcf_equity_value / 1000000).toFixed(2),
                    (result.comp_ev_value / 1000000).toFixed(2),
                    (result.comp_pe_value / 1000000).toFixed(2),
                    (result.market_cap / 1000000).toFixed(2)
                ],
                backgroundColor: [
                    'rgba(56, 239, 125, 0.7)',
                    'rgba(108, 92, 231, 0.7)',
                    'rgba(255, 107, 107, 0.7)',
                    'rgba(255, 195, 0, 0.7)'
                ],
                borderColor: [
                    'rgba(56, 239, 125, 1)',
                    'rgba(108, 92, 231, 1)',
                    'rgba(255, 107, 107, 1)',
                    'rgba(255, 195, 0, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                title: {
                    display: true,
                    text: 'Valuation Methods Comparison (in millions)'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value + 'M';
                        }
                    }
                }
            }
        }
    });
}

function renderMonteCarloChart(result) {
    const ctx = document.getElementById('monteCarloChart');
    if (!ctx) return;
    
    // Create distribution approximation
    const mean = (result.mc_p10 + result.mc_p90) / 2;
    const p25 = result.mc_p10 + (mean - result.mc_p10) * 0.5;
    const p75 = result.mc_p90 - (result.mc_p90 - mean) * 0.5;
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['P10', 'P25', 'Mean', 'P75', 'P90'],
            datasets: [{
                label: 'Valuation Range',
                data: [
                    (result.mc_p10 / 1000000).toFixed(2),
                    (p25 / 1000000).toFixed(2),
                    (mean / 1000000).toFixed(2),
                    (p75 / 1000000).toFixed(2),
                    (result.mc_p90 / 1000000).toFixed(2)
                ],
                fill: true,
                backgroundColor: 'rgba(108, 92, 231, 0.2)',
                borderColor: 'rgba(108, 92, 231, 1)',
                borderWidth: 2,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                title: {
                    display: true,
                    text: 'Monte Carlo Simulation: Value Distribution (in millions)'
                }
            },
            scales: {
                y: {
                    ticks: {
                        callback: function(value) {
                            return '$' + value + 'M';
                        }
                    }
                }
            }
        }
    });
}

// Export function
async function exportCSV() {
    window.location.href = '/api/export/csv';
}

// Chart.js visualization functions
function renderValuationChart(result) {
    const ctx = document.getElementById('valuationChart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['DCF Method', 'EV/EBITDA', 'P/E Method', 'Current Market Cap'],
            datasets: [{
                label: 'Valuation ($M)',
                data: [
                    (result.dcf_equity_value / 1000000).toFixed(2),
                    (result.comp_ev_value / 1000000).toFixed(2),
                    (result.comp_pe_value / 1000000).toFixed(2),
                    (result.market_cap / 1000000).toFixed(2)
                ],
                backgroundColor: [
                    'rgba(56, 239, 125, 0.7)',
                    'rgba(108, 92, 231, 0.7)',
                    'rgba(255, 107, 107, 0.7)',
                    'rgba(255, 195, 0, 0.7)'
                ],
                borderColor: [
                    'rgba(56, 239, 125, 1)',
                    'rgba(108, 92, 231, 1)',
                    'rgba(255, 107, 107, 1)',
                    'rgba(255, 195, 0, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                title: {
                    display: true,
                    text: 'Valuation Methods Comparison (in millions)'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value + 'M';
                        }
                    }
                }
            }
        }
    });
}

function renderMonteCarloChart(result) {
    const ctx = document.getElementById('monteCarloChart');
    if (!ctx) return;
    
    // Create distribution approximation
    const mean = (result.mc_p10 + result.mc_p90) / 2;
    const p25 = result.mc_p10 + (mean - result.mc_p10) * 0.5;
    const p75 = result.mc_p90 - (result.mc_p90 - mean) * 0.5;
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['P10', 'P25', 'Mean', 'P75', 'P90'],
            datasets: [{
                label: 'Valuation Range',
                data: [
                    (result.mc_p10 / 1000000).toFixed(2),
                    (p25 / 1000000).toFixed(2),
                    (mean / 1000000).toFixed(2),
                    (p75 / 1000000).toFixed(2),
                    (result.mc_p90 / 1000000).toFixed(2)
                ],
                fill: true,
                backgroundColor: 'rgba(108, 92, 231, 0.2)',
                borderColor: 'rgba(108, 92, 231, 1)',
                borderWidth: 2,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                title: {
                    display: true,
                    text: 'Monte Carlo Simulation: Value Distribution (in millions)'
                }
            },
            scales: {
                y: {
                    ticks: {
                        callback: function(value) {
                            return '$' + value + 'M';
                        }
                    }
                }
            }
        }
    });
}
