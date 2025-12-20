// Phase 1: Per-Company Scenarios & Real-Time Prices
let macroEnvironments = [];
let activeMacroId = null;
let priceUpdateInterval = null;
let companiesData = {};

document.addEventListener('DOMContentLoaded', () => {
    loadMacroEnvironments();
    startRealtimePriceUpdates();
});

async function loadMacroEnvironments() {
    try {
        const response = await fetch('/api/macro-environments');
        if (!response.ok) return;
        const data = await response.json();
        macroEnvironments = data.macro_environments || [];
        const activeEnv = macroEnvironments.find(env => env.is_active);
        if (activeEnv) {
            activeMacroId = activeEnv.id;
            updateMacroStatus(activeEnv.name);
        }
        renderMacroCards();
    } catch (error) {
        console.error('Error loading macro:', error);
    }
}

function renderMacroCards() {
    const container = document.getElementById('macro-environments');
    if (!container) return;
    container.innerHTML = macroEnvironments.map(env => {
        const macroType = env.name.toLowerCase().includes('bear') ? 'bear' : env.name.toLowerCase().includes('bull') ? 'bull' : 'base';
        const icon = macroType === 'bear' ? '🐻' : macroType === 'bull' ? '🐂' : '📊';
        const desc = macroType === 'bear' ? 'Lower growth, higher risk' : macroType === 'bull' ? 'Strong growth, lower risk' : 'Balanced assumptions';
        return `<div class="macro-card ${macroType}"><div class="macro-card-header"><div class="macro-card-title">${icon} ${env.name}</div></div><div class="macro-card-description">${desc}<div style="margin-top:0.5rem;font-size:0.85rem;color:#667eea;font-weight:600;">Apply to individual stocks below</div></div><div class="macro-assumptions"><div class="macro-assumption-item"><span class="macro-assumption-label">Risk-Free Rate</span><span class="macro-assumption-value">${(env.risk_free_rate*100).toFixed(2)}%</span></div><div class="macro-assumption-item"><span class="macro-assumption-label">Market Premium</span><span class="macro-assumption-value">${(env.market_risk_premium*100).toFixed(2)}%</span></div></div></div>`;
    }).join('');
}

function updateMacroStatus(envName) {
    const statusContainer = document.getElementById('current-macro-status');
    if (!statusContainer) return;
    const macroType = envName.toLowerCase().includes('bear') ? 'bear' : envName.toLowerCase().includes('bull') ? 'bull' : 'base';
    statusContainer.innerHTML = `<span class="macro-status-badge ${macroType}">Reference: ${envName}</span>`;
}

function startRealtimePriceUpdates() {
    updatePortfolioPrices();
    priceUpdateInterval = setInterval(() => updatePortfolioPrices(), 60000);
    console.log('Real-time price updates started');
}

async function updatePortfolioPrices() {
    try {
        const response = await fetch('/api/prices/realtime');
        if (!response.ok) return;
        const data = await response.json();
        if (data.success && data.prices) {
            data.prices.forEach(p => {
                const card = document.querySelector(`[data-company-id="${p.company_id}"]`);
                if (!card) return;
                const priceEl = card.querySelector('.company-current-price');
                if (priceEl) {
                    priceEl.textContent = `$${p.current_price.toFixed(2)}`;
                    priceEl.classList.add('price-updated');
                    setTimeout(() => priceEl.classList.remove('price-updated'), 500);
                }
            });
        }
    } catch (error) {
        console.error('Error updating prices:', error);
    }
}

async function applyScenarioToCompany(companyId, scenarioType) {
    try {
        showNotification(`Applying ${scenarioType}...`, 'info');
        const response = await fetch(`/api/company/${companyId}/scenario/apply`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({scenario_type: scenarioType})
        });
        if (!response.ok) throw new Error('Failed');
        updateCompanyScenarioDisplay(companyId, scenarioType);
        if (typeof loadCompanies === 'function') loadCompanies();
        showNotification(`${scenarioType.toUpperCase()} applied!`, 'success');
    } catch (error) {
        showNotification('Failed to apply scenario', 'error');
    }
}

function updateCompanyScenarioDisplay(companyId, scenarioType) {
    const card = document.querySelector(`[data-company-id="${companyId}"]`);
    if (!card) return;
    card.querySelectorAll('.scenario-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.scenario === scenarioType) btn.classList.add('active');
    });
    let badge = card.querySelector('.company-scenario-badge');
    if (!badge) {
        badge = document.createElement('div');
        badge.className = 'company-scenario-badge';
        const header = card.querySelector('.company-header');
        if (header) header.appendChild(badge);
    }
    const icon = scenarioType === 'bear' ? '🐻' : scenarioType === 'bull' ? '🐂' : '📊';
    badge.className = `company-scenario-badge scenario-${scenarioType}`;
    badge.textContent = icon + ' ' + scenarioType.toUpperCase();
}

function showNotification(message, type = 'info') {
    const n = document.createElement('div');
    n.style.cssText = `position:fixed;top:80px;right:20px;padding:1rem 1.5rem;background:${type==='success'?'#38ef7d':type==='error'?'#fa709a':'#667eea'};color:white;border-radius:8px;box-shadow:0 4px 20px rgba(0,0,0,0.2);z-index:9999;font-weight:600;`;
    n.textContent = message;
    document.body.appendChild(n);
    setTimeout(() => n.remove(), 3000);
}

const style = document.createElement('style');
style.textContent = `.price-updated{animation:priceFlash 0.5s ease}@keyframes priceFlash{0%,100%{background:transparent}50%{background:#38ef7d;color:white;padding:2px 6px;border-radius:4px}}.company-scenario-badge{display:inline-block;padding:0.25rem 0.75rem;border-radius:20px;font-size:0.8rem;font-weight:700;margin-left:0.5rem}.company-scenario-badge.scenario-bear{background:#fee140;color:#c82333}.company-scenario-badge.scenario-base{background:#38ef7d;color:#11998e}.company-scenario-badge.scenario-bull{background:#667eea;color:white}.scenario-selector{display:flex;gap:0.5rem;margin-top:0.75rem;padding-top:0.75rem;border-top:1px solid #e9ecef}.scenario-btn{flex:1;padding:0.5rem;border:2px solid #e9ecef;background:white;border-radius:6px;font-size:0.8rem;font-weight:600;cursor:pointer;transition:all 0.2s}.scenario-btn:hover{transform:translateY(-2px);box-shadow:0 2px 8px rgba(0,0,0,0.1)}.scenario-btn.bear{border-color:#fee140;color:#c82333}.scenario-btn.bear:hover,.scenario-btn.bear.active{background:#fee140;color:#c82333}.scenario-btn.base{border-color:#38ef7d;color:#11998e}.scenario-btn.base:hover,.scenario-btn.base.active{background:#38ef7d;color:white}.scenario-btn.bull{border-color:#667eea;color:#667eea}.scenario-btn.bull:hover,.scenario-btn.bull.active{background:#667eea;color:white}.scenario-btn.active{font-weight:700;box-shadow:0 4px 12px rgba(0,0,0,0.15)}`;
document.head.appendChild(style);

window.applyScenarioToCompany = applyScenarioToCompany;
window.updatePortfolioPrices = updatePortfolioPrices;
