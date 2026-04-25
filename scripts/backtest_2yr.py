"""
2-Year Backtest: Model Price vs Historical Actuals
Uses current model predictions from predictions_db.json
Pulls 24 months of historical prices and computes gap at each month.
Output: JSON report + console summary by sub-sector.

Key question: is our model systematically over or under market?
Trend analysis: is the gap CONVERGING (model was right) or DIVERGING (model was wrong)?
"""

import json
import time
from collections import defaultdict
from datetime import date
from dateutil.relativedelta import relativedelta
from pathlib import Path

import yfinance as yf

DB_PATH = Path(__file__).parent / 'predictions_db.json'
REPORT_PATH = Path(__file__).parent / 'backtest_2yr_report.json'

MONTHS = 24


def get_monthly_prices(ticker: str, months: int = 24) -> dict:
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='3y')
        if hist.empty:
            return {}
        hist.index = hist.index.tz_localize(None) if hist.index.tzinfo else hist.index

        prices = {}
        today = date.today()
        for i in range(months, 0, -1):
            month_start = today - relativedelta(months=i)
            label = month_start.strftime('%Y-%m')
            from datetime import datetime
            window_start = datetime(month_start.year, month_start.month, 1)
            window_end = window_start + relativedelta(days=10)
            try:
                window = hist.loc[window_start:window_end]
                if not window.empty:
                    prices[label] = round(float(window['Close'].iloc[0]), 2)
            except Exception:
                pass
        return prices
    except Exception:
        return {}


def run_backtest(limit: int = None):
    db = json.loads(DB_PATH.read_text())
    tickers = list(db.keys())
    if limit:
        tickers = tickers[:limit]

    total = len(tickers)
    print(f'\n2-Year Backtest: {total} stocks × {MONTHS} months\n')
    print(f'{"Ticker":<7} {"Model$":>8} {"Cur$":>7} {"CurGap":>8} | {"2yr trend"}')
    print('-' * 75)

    results = []
    by_tag = defaultdict(list)

    for i, ticker in enumerate(tickers, 1):
        rec = db[ticker]
        model_price = rec.get('model_price', 0)
        if not model_price:
            continue

        monthly = get_monthly_prices(ticker, MONTHS)
        if not monthly:
            continue

        months_sorted = sorted(monthly.keys())
        gaps = {}
        for label, price in monthly.items():
            if model_price > 0:
                gap = round((price - model_price) / model_price * 100, 1)
                gaps[label] = {'price': price, 'gap': gap}

        if not gaps:
            continue

        # Current gap (most recent month in history)
        current_label = months_sorted[-1]
        current_price = monthly[current_label]
        current_gap = gaps[current_label]['gap']

        # 2-year-ago gap (oldest month)
        oldest_label = months_sorted[0]
        oldest_price = monthly[oldest_label]
        oldest_gap = gaps[oldest_label]['gap']

        # Trend: did the gap CONVERGE (absolute gap decreasing) or DIVERGE?
        trend = 'CONVERGING' if abs(current_gap) < abs(oldest_gap) else 'DIVERGING'

        tag = rec.get('sub_tag', 'unknown')
        ctype = rec.get('company_type', '')

        row = {
            'ticker': ticker,
            'model_price': model_price,
            'company_type': ctype,
            'sub_tag': tag,
            'current_price': current_price,
            'current_gap': current_gap,
            'oldest_price': oldest_price,
            'oldest_gap': oldest_gap,
            'trend': trend,
            'monthly_gaps': gaps,
        }
        results.append(row)
        by_tag[tag].append(current_gap)

        direction = 'OVER' if current_gap < 0 else 'UNDER'
        trend_arrow = '↘' if trend == 'CONVERGING' else '↗'
        print(f'{ticker:<7} ${model_price:>7.0f} ${current_price:>6.0f} {current_gap:>+7.1f}%  '
              f'| {trend_arrow} {trend} from {oldest_gap:+.0f}% → {current_gap:+.0f}% ({direction})')

        time.sleep(0.3)  # gentle on yfinance

    # Summary by sub-sector
    import statistics
    print('\n\n=== 2-YEAR BACKTEST SUMMARY BY SUB-SECTOR ===\n')
    print(f'{"Sub-sector":<22} {"n":>4} {"Med gap":>9} {"MAE":>8} {"Consistent?"}')
    print('-' * 65)

    sector_rows = []
    for tag, gaps_list in sorted(by_tag.items()):
        if not gaps_list:
            continue
        med = statistics.median(gaps_list)
        mae = statistics.mean(abs(g) for g in gaps_list)
        within20 = sum(1 for g in gaps_list if abs(g) <= 20) / len(gaps_list)
        consistent = 'SYSTEMATIC OVERVAL' if med < -25 else 'SYSTEMATIC UNDERVAL' if med > 25 else 'MIXED'
        sector_rows.append((tag, len(gaps_list), med, mae, within20, consistent))

    sector_rows.sort(key=lambda x: x[2])  # sort by median gap
    for tag, n, med, mae, w20, consistent in sector_rows:
        mark = '⚠️' if abs(med) > 25 else '✅'
        print(f'{tag:<22} {n:>4}   {med:>+7.1f}%  {mae:>6.1f}%   {consistent} {mark}')

    # Overall stats
    all_gaps = [r['current_gap'] for r in results]
    print(f'\n=== OVERALL STATS ({len(results)} stocks) ===')
    print(f'Within ±20%: {sum(1 for g in all_gaps if abs(g)<=20)} = {sum(1 for g in all_gaps if abs(g)<=20)/len(all_gaps)*100:.0f}%')
    print(f'Within ±30%: {sum(1 for g in all_gaps if abs(g)<=30)} = {sum(1 for g in all_gaps if abs(g)<=30)/len(all_gaps)*100:.0f}%')
    print(f'MAE: {statistics.mean(abs(g) for g in all_gaps):.1f}%')
    print(f'Median gap: {statistics.median(all_gaps):+.1f}%')

    # Convergence analysis
    converging = [r for r in results if r['trend'] == 'CONVERGING']
    diverging  = [r for r in results if r['trend'] == 'DIVERGING']
    print(f'\nConverging (market → model): {len(converging)}/{len(results)} = {len(converging)/len(results)*100:.0f}%')
    print(f'Diverging  (market ← model): {len(diverging)}/{len(results)} = {len(diverging)/len(results)*100:.0f}%')

    # Save full report
    REPORT_PATH.write_text(json.dumps(results, indent=2))
    print(f'\nFull report saved to {REPORT_PATH.name}')
    return results


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--limit', type=int, default=None, help='Limit to N stocks (for testing)')
    args = p.parse_args()
    run_backtest(limit=args.limit)
