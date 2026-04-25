"""
Calibration corrections derived from:
- 24-month tracking of 20 stocks (Batch 1)
- Single-month snapshot of 258 S&P 500 stocks (April 2025, Batch 2)
- 2-year historical backtest of 305 stocks (April 2025, current session)

Gap = (actual_market - our_model) / our_model
Correction = market / model  →  multiply model price by this factor.

2yr backtest update math:
  new_raw = (1 + observed_gap) * old_effective_factor
  Where old_effective = raw (HIGH or MEDIUM n≥5), 0.75*raw+0.25 (MEDIUM n<5), 0.5*raw+0.5 (LOW)

Sub-tag corrections take priority over company-type fallbacks.
Dampening rules:
  LOW confidence  → 0.5 * factor + 0.5 * 1.0  (halfway to neutral)
  MEDIUM, n < 5   → 0.75 * factor + 0.25 * 1.0
  HIGH or MEDIUM n>=5 → no dampening
"""

# Sub-tag corrections — (raw_factor, confidence, n_stocks)
SUBTAG_CORRECTIONS = {
    # ── Tags with dedicated alternative models (P/B, FFO, P/E, div-yield) ─────
    # health_insurance: structural fix added (analyst fallback prevents DCF outliers).
    # P/E 16x model works; analyst fallback handles MLR-crisis earnings collapse cases.
    'health_insurance':  (1.00, 'HIGH',  5),
    'utility_regulated': (1.00, 'HIGH',  8),   # dividend-yield model replaces DCF
    # commercial_bank: 2yr backtest shows -28% gap for pure bank stocks.
    # Updated from 1.00 → 0.72. Insurance stocks separated to pc_insurance.
    'commercial_bank':   (0.72, 'HIGH', 15),   # P/B model; per-ticker overrides in ml_engine
    # pc_insurance: new tag (2yr backtest: TRV/HIG/AFL/CB/ALL/MET averaged +28% gap)
    # P/B model undervalues; correction of 1.30 closes the gap.
    'pc_insurance':      (1.30, 'MEDIUM', 6),  # P&C/life insurers; P/B model
    'exchange':          (1.00, 'MEDIUM', 2),  # monopoly franchise multiples correct it

    # ── Well-calibrated or minor adjustments ─────────────────────────────────
    # 2yr backtest results in parentheses; updated where |gap| > 15%
    'cloud_saas':        (0.95, 'HIGH',   8),  # backtest -0.6%: essentially perfect
    'fabless_semi':      (0.65, 'HIGH',   8),  # backtest +1.7%: AI selloff partially corrected
    'defense':           (0.88, 'MEDIUM', 6),  # backtest -5.4%: minor tweak
    'cloud_software':    (0.81, 'HIGH',  15),  # backtest -7.6%: was 0.88
    'legacy_tech':       (1.00, 'MEDIUM', 5),  # low multiples already priced in
    'semi_equipment':    (1.05, 'MEDIUM', 3),  # backtest not enough data: hold
    'streaming_media':   (0.54, 'LOW',    1),  # backtest -44.5%: was 0.95; big drop (NFLX)
    'hotel_resort':      (1.15, 'MEDIUM', 2),  # insufficient backtest data: hold
    'invest_bank':       (0.75, 'MEDIUM', 3),  # backtest +4.3%: was 0.62; model now undervalues
    'music_platform':    (1.00, 'LOW',    1),  # backtest +3.6%: neutral
    'auto_legacy':       (0.67, 'LOW',    2),  # backtest +3.7%: was 0.30; debt fix improved it
    'story_auto':        (0.88, 'LOW',    1),  # TSLA: hold
    'membership_retail': (0.92, 'LOW',    1),  # COST: hold
    'ecommerce_cloud':   (0.55, 'LOW',    1),  # backtest -34.3%: was 0.66; AMZN still overvalued
    'digital_platform':  (0.56, 'LOW',    1),  # backtest -27.7%: unchanged
    'growth_loss':       (0.90, 'MEDIUM', 8),  # backtest -12.8%: added explicit entry

    # ── Systematic overvalue — updated from 2yr backtest ──────────────────────
    # energy_ep: n=13, gap=-35%. new_raw = 0.65 * 0.75 = 0.49
    'energy_ep':         (0.49, 'HIGH',  13),  # was 0.75; DCF oil assumptions too optimistic
    # consumer_staples: n=19, gap=-22.2%. new_raw = 0.778 * 0.59 = 0.46
    'consumer_staples':  (0.46, 'HIGH',  19),  # was 0.59; terminal growth + thin margins
    # pharma: n=17, gap=-17.6%. new_raw = 0.824 * 0.78 = 0.64
    'pharma':            (0.64, 'HIGH',  17),  # was 0.78; patent cliff + GLP-1 competition
    # reit: n=17, gap=-26.1%. new_raw = 0.739 * 0.72 = 0.53
    'reit':              (0.53, 'HIGH',  17),  # was 0.72; high-rate environment; FFO multiple 18x too rich
    # biotech_device: n=8, gap=-30.3%. new_raw = 0.697 * 0.62 = 0.43
    'biotech_device':    (0.43, 'HIGH',   8),  # was 0.62; EV/EBITDA multiples compressing
    # franchise_rest: n=19, gap=-26.9%. new_raw = 0.731 * 0.78 = 0.57
    'franchise_rest':    (0.57, 'HIGH',  10),  # was 0.78; MCD/SBUX/CMG under consumer pressure
    # media_cable: n=3, gap=-62.3%. Min floor hit. Effective = 0.20 (HIGH, no dampening)
    'media_cable':       (0.20, 'HIGH',   3),  # was 0.36 MEDIUM; secular decline accelerating
    # asset_mgmt: n=5 (MEDIUM no dampening), gap=-43.1%. new_raw = 0.569 * 0.58 = 0.33
    'asset_mgmt':        (0.33, 'MEDIUM', 5),  # was 0.58; AUM fee compression, lumpy carried int
    # payment_net: n=4, gap=-37.5%. new_eff = 0.625*0.7375 = 0.46
    'payment_net':       (0.46, 'MEDIUM', 3),  # was 0.65; fintech competition, market P/E lower
    # data_analytics: n=3, gap=-29.7%. new_eff = 0.703 * 0.775 = 0.55
    'data_analytics':    (0.55, 'MEDIUM', 3),  # was 0.70; SPGI/MCO still overvalued
    # retail_bigbox: n=12, gap=-16.3%. new_raw = 0.837 * 1.50 = 1.26
    'retail_bigbox':     (1.26, 'HIGH',   8),  # was 1.50; WMT re-rating partially corrected
    # packaging: n not in backtest output — hold
    'packaging':         (0.40, 'MEDIUM', 6),  # thin margins + high debt; hold
    # gaming: hold
    'gaming':            (0.88, 'MEDIUM', 3),
    # apparel_brand: n=3, gap=-12.6%. minor: hold
    'apparel_brand':     (0.85, 'MEDIUM', 3),
    # tobacco: n=2, gap=-18.8%. new_eff = 0.812*0.925 = 0.75; new_raw = 0.75 (LOW)
    'tobacco':           (0.75, 'LOW',    2),  # was 0.85

    # ── Systematic undervalue — updated from 2yr backtest ─────────────────────
    # industrial_cong: n=30, gap=+10.8%. new_raw = 1.108 * 1.07 = 1.19
    'industrial_cong':   (1.19, 'HIGH',  29),  # was 1.07; industrials outperformed
    # telecom_carrier: n=23, gap=+33.2%. COMPLETE FLIP. new_eff = 1.332*0.8125 = 1.08
    # Stocks (T, VZ, TMUS) recovered while model stayed conservative.
    'telecom_carrier':   (1.08, 'MEDIUM', 23), # was 0.75; model now undervalues telecom
    # mature_semi: n=4, gap=+43.3%. new_eff = 1.433*1.15 = 1.65
    'mature_semi':       (1.65, 'HIGH',   4),  # was 1.20 MEDIUM; QCOM/TXN/ADI cycle recovery
    # oilfield_svc: n=3, gap=+51.6%. new_eff = 1.516*1.4275 = 2.16
    'oilfield_svc':      (2.16, 'MEDIUM', 3),  # was 1.57; SLB/HAL/BKR repriced for activity cycle
    # airline: n=5 (now MEDIUM with real data), gap=+60.1%. new_raw = 1.601
    'airline':           (1.60, 'MEDIUM', 5),  # was 1.00 LOW; post-COVID demand + yield improvement
    # luxury_brand: n=2, gap=+92.3%. new_raw = 1.923 LOW
    'luxury_brand':      (1.92, 'LOW',    2),  # was 1.00; brand premium severely underweighted
    # heavy_machinery: n=4, gap=+19.2%. new_eff ≈ 1.013; flip to neutral
    'heavy_machinery':   (1.01, 'MEDIUM', 3),  # was 0.80; CAT/DE cycle outperformance
    # logistics (old generic tag — catch stocks not yet re-tagged): n=6, gap=+61.1%
    'logistics':         (1.75, 'MEDIUM', 6),  # catch-all for old predictions_db entries
    # logistics_ltl: n=3, gap inferred from above. Upgrade from 1.40.
    'logistics_ltl':     (2.09, 'MEDIUM', 3),  # was 1.40; ODFL/SAIA pricing power
    'logistics_parcel':  (0.80, 'MEDIUM', 2),  # UPS/FDX: commoditized; hold
    'security_cloud':    (1.80, 'MEDIUM', 5),  # ARR premium — hold; insufficient new data
    'industrial_dist':   (0.90, 'LOW',    2),

    # energy_major: XOM/CVX recovered vs April 2025 lows; hold pending more data
    'energy_major':      (0.69, 'MEDIUM', 3),

    # IDM_semi: INTC recovering but single-stock risk remains; max cap at 2.50
    'IDM_semi':          (2.50, 'LOW',    1),  # was 2.60; cap enforces max 2.50

    # distressed recovery
    'distressed_industrial': (1.80, 'LOW', 1),  # BA: market prices eventual recovery

    # Batch-2 new sub-sectors — updated from real backtest data where available
    'hospital_operator': (0.55, 'MEDIUM', 1),  # backtest -45%: HCA model way too high
    'crypto_proxy':      (0.42, 'LOW',    1),   # backtest -57.8%: MSTR anchor too optimistic
    'rule40_saas':       (0.89, 'MEDIUM', 2),   # backtest -10.7%: close; minor trim
}

# Company-type fallback (used when sub_tag not in SUBTAG_CORRECTIONS)
TYPE_CORRECTIONS = {
    'GROWTH_TECH':            0.71,
    'HYPERGROWTH':            0.55,
    'CYCLICAL':               0.70,
    'DISTRESSED':             0.90,
    'STABLE_VALUE':           0.85,
    'STABLE_VALUE_LOWGROWTH': 0.72,
    'STORY':                  0.88,
}

MIN_CORRECTION = 0.20
MAX_CORRECTION = 2.50


def get_correction(sub_tag: str, company_type: str) -> float:
    """
    Return calibration factor. Multiply model price by this to get calibrated price.
    """
    if sub_tag in SUBTAG_CORRECTIONS:
        factor, confidence, n = SUBTAG_CORRECTIONS[sub_tag]
        if confidence == 'LOW':
            factor = 0.5 * factor + 0.5 * 1.0
        elif confidence == 'MEDIUM' and n < 5:
            factor = 0.75 * factor + 0.25 * 1.0
    else:
        factor = TYPE_CORRECTIONS.get(company_type, 0.80)

    return max(MIN_CORRECTION, min(factor, MAX_CORRECTION))
