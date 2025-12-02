// ============================================
// QUICK ADD BY TICKER - NEW FEATURE
// ============================================

function handleTickerInput(event) {
    if (event.key === 'Enter') {
        quickAddCompany();
    }
}

function quickAddTicker(ticker) {
    document.getElementById('quick-ticker-input').value = ticker.toUpperCase();
    quickAddCompany();
}

async function quickAddCompany() {
    const input = document.getElementById('quick-ticker-input');
    const ticker = input.value.trim().toUpperCase();

    if (!ticker) {
        alert('Please enter a ticker symbol');
        return;
    }

    // Show loading state
    document.getElementById('add-btn-text').style.display = 'none';
    document.getElementById('add-btn-loading').style.display = 'inline';
    document.getElementById('ticker-result').style.display = 'none';
    document.querySelector('.btn-add-ticker').disabled = true;

    try {
        const response = await fetch('/api/ticker/import-and-value', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ ticker: ticker })
        });

        const data = await response.json();

        if (data.success) {
            // Show success result
            showTickerResult(data, 'success');

            // Clear input
            input.value = '';

            // Refresh dashboard and companies
            setTimeout(() => {
                if (typeof loadDashboard === 'function') loadDashboard();
                if (typeof loadCompanies === 'function') loadCompanies();
            }, 1500);
        } else {
            showTickerResult({ error: data.error || 'Unknown error' }, 'error');
        }
    } catch (error) {
        console.error('Error adding company:', error);
        showTickerResult({ error: 'Failed to connect to server' }, 'error');
    } finally {
        // Hide loading state
        document.getElementById('add-btn-text').style.display = 'inline';
        document.getElementById('add-btn-loading').style.display = 'none';
        document.querySelector('.btn-add-ticker').disabled = false;
    }
}

function showTickerResult(data, type) {
    const resultDiv = document.getElementById('ticker-result');

    if (type === 'success') {
        const val = data.valuation;
        const upside = val.upside_pct;
        const recClass = upside > 0 ? 'success' : 'danger';
        const recSymbol = upside > 10 ? '🟢' : (upside < -10 ? '🔴' : '🟡');

        resultDiv.innerHTML = `
            <div class="result-success">
                <div class="result-header">
                    <strong>✅ Added: ${data.company_name}</strong>
                    <span class="ticker-badge">${data.ticker}</span>
                </div>
                <div class="result-metrics">
                    <div class="metric">
                        <span class="metric-label">Current Price:</span>
                        <span class="metric-value">$${data.current_price.toFixed(2)}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Fair Value:</span>
                        <span class="metric-value">$${val.final_price_per_share.toFixed(2)}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Upside:</span>
                        <span class="metric-value metric-${recClass}">${upside > 0 ? '+' : ''}${upside.toFixed(1)}%</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Recommendation:</span>
                        <span class="metric-value">${recSymbol} ${val.recommendation}</span>
                    </div>
                </div>
                <div class="result-footer">
                    Now tracking ${data.ticker} in your portfolio!
                </div>
            </div>
        `;
    } else {
        resultDiv.innerHTML = `
            <div class="result-danger">
                <strong>❌ Error</strong>
                <p>${data.error}</p>
            </div>
        `;
    }

    resultDiv.style.display = 'block';

    // Auto-hide after 5 seconds
    setTimeout(() => {
        resultDiv.style.display = 'none';
    }, 5000);
}

// ============================================
// REAL-TIME PRICE UPDATES
// ============================================

let priceUpdateInterval = null;

// Initialize auto-updates
function initializeRealTimeUpdates() {
    // Update prices every 60 seconds
    priceUpdateInterval = setInterval(updateRealTimePrices, 60000);

    // Also update after 3 seconds initially
    setTimeout(updateRealTimePrices, 3000);

    console.log('✓ Real-time price updates enabled (every 60 seconds)');
}

async function updateRealTimePrices() {
    try {
        console.log('🔄 Updating real-time prices...');

        const response = await fetch('/api/companies');
        const companies = await response.json();

        // Update global companies if it exists
        if (typeof allCompanies !== 'undefined') {
            allCompanies = companies;
        }

        // Refresh views if functions exist
        if (typeof loadDashboard === 'function') loadDashboard();
        if (typeof renderCompanies === 'function') renderCompanies();

        // Show subtle indicator
        showPriceUpdateIndicator();

        console.log('✅ Prices updated');
    } catch (error) {
        console.error('Error updating prices:', error);
    }
}

function showPriceUpdateIndicator() {
    // Check if indicator already exists
    if (document.querySelector('.price-update-indicator')) return;

    const indicator = document.createElement('div');
    indicator.className = 'price-update-indicator';
    indicator.innerHTML = '🔄 Updated';
    indicator.style.cssText = `
        position: fixed;
        top: 70px;
        right: 20px;
        background: #4CAF50;
        color: white;
        padding: 6px 12px;
        border-radius: 4px;
        font-size: 12px;
        z-index: 9999;
        opacity: 0;
        transition: opacity 0.3s;
    `;

    document.body.appendChild(indicator);

    // Fade in
    setTimeout(() => indicator.style.opacity = '1', 10);

    // Fade out and remove
    setTimeout(() => {
        indicator.style.opacity = '0';
        setTimeout(() => indicator.remove(), 300);
    }, 1500);
}

// Auto-start when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeRealTimeUpdates);
} else {
    initializeRealTimeUpdates();
}
