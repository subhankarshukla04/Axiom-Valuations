#!/usr/bin/env python3
"""
SIMPLE SCRIPT TO ADD COMPANIES TO YOUR VALUATION APP
Just run: python3 add_company.py
"""

import requests
import sys

def add_company(ticker):
    """Add a company and get instant valuation"""

    print(f"\n{'='*70}")
    print(f"  Adding {ticker} to your portfolio...")
    print(f"{'='*70}")

    try:
        # Call your app's API
        response = requests.post(
            'http://127.0.0.1:5001/api/ticker/import-and-value',
            json={'ticker': ticker},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()

            if data.get('success'):
                # Success! Show results
                print(f"\n✅ SUCCESS! Added to portfolio\n")
                print(f"{'─'*70}")
                print(f"  Company:        {data['company_name']}")
                print(f"  Ticker:         {ticker}")
                print(f"  Sector:         {data['valuation']['sector']}")
                print(f"{'─'*70}")

                val = data['valuation']
                print(f"\n💰 VALUATION SUMMARY:")
                print(f"{'─'*70}")
                print(f"  Current Price:  ${data['current_price']:>12,.2f}")
                print(f"  Fair Value:     ${val['final_price_per_share']:>12,.2f}")
                print(f"  Upside/Down:    {val['upside_pct']:>12.1f}%")
                print(f"{'─'*70}")

                # Recommendation with color
                rec = val['recommendation']
                if 'BUY' in rec:
                    symbol = '🟢'
                elif 'HOLD' in rec:
                    symbol = '🟡'
                else:
                    symbol = '🔴'

                print(f"\n{symbol} RECOMMENDATION: {rec}")
                print(f"\n✓ {ticker} is now being tracked in your portfolio!")
                print(f"{'='*70}\n")
                return True
            else:
                print(f"\n❌ Error: {data.get('error')}\n")
                return False
        else:
            print(f"\n❌ HTTP Error {response.status_code}")
            print("   Make sure your app is running at http://127.0.0.1:5001\n")
            return False

    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to app!")
        print("   Please start the app first: python3 app.py\n")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        return False


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  STOCK VALUATION TRACKER - ADD COMPANY BY TICKER")
    print("="*70)

    # Check if ticker provided as argument
    if len(sys.argv) > 1:
        ticker = sys.argv[1].upper()
        add_company(ticker)
    else:
        # Interactive mode
        print("\nPopular tickers: AAPL, GOOGL, AMZN, MSFT, TSLA, NVDA, META, NFLX")
        print("Or any US stock ticker symbol")

        ticker = input("\nEnter ticker to add: ").strip().upper()

        if ticker:
            add_company(ticker)
        else:
            print("\n❌ No ticker entered\n")

    print("View all companies: http://127.0.0.1:5001")
    print("="*70 + "\n")
