"""
Real-time Stock Price Service
Fetches current market prices for portfolio companies
"""

import yfinance as yf
from datetime import datetime
from typing import Dict, List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from config import Config

class RealtimePriceService:
    def __init__(self):
        self.conn = None

    def get_connection(self):
        """Get database connection"""
        if not self.conn or self.conn.closed:
            self.conn = psycopg2.connect(
                Config.get_db_connection_string(),
                cursor_factory=RealDictCursor
            )
        return self.conn

    def get_current_price(self, ticker: str) -> Optional[float]:
        """
        Fetch current stock price from Yahoo Finance

        Args:
            ticker: Stock ticker symbol

        Returns:
            Current price or None if error
        """
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period='1d', interval='1m')

            if data.empty:
                # Fallback to info if history fails
                info = stock.info
                return info.get('currentPrice') or info.get('regularMarketPrice')

            # Get most recent price
            current_price = data['Close'].iloc[-1]
            return float(current_price)

        except Exception as e:
            print(f"Error fetching price for {ticker}: {e}")
            return None

    def update_all_portfolio_prices(self) -> List[Dict]:
        """
        Update prices for all companies in portfolio

        Returns:
            List of updated company prices
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Get all companies with tickers
            cursor.execute("""
                SELECT id, name, ticker, market_cap_estimate, shares_outstanding
                FROM companies
                WHERE ticker IS NOT NULL AND ticker != ''
                ORDER BY name
            """)

            companies = cursor.fetchall()
            updated_prices = []

            for company in companies:
                ticker = company['ticker']
                current_price = self.get_current_price(ticker)

                if current_price:
                    # Update market cap estimate based on current price
                    if company['shares_outstanding']:
                        new_market_cap = current_price * company['shares_outstanding']

                        cursor.execute("""
                            UPDATE companies
                            SET market_cap_estimate = %s,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE id = %s
                        """, (new_market_cap, company['id']))

                    updated_prices.append({
                        'company_id': company['id'],
                        'ticker': ticker,
                        'name': company['name'],
                        'current_price': current_price,
                        'market_cap': new_market_cap if company['shares_outstanding'] else company['market_cap_estimate'],
                        'updated_at': datetime.now().isoformat()
                    })

            conn.commit()
            return updated_prices

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

    def get_portfolio_prices(self) -> List[Dict]:
        """
        Get current prices for all portfolio companies without updating DB

        Returns:
            List of company prices
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id, name, ticker, market_cap_estimate, shares_outstanding
                FROM companies
                WHERE ticker IS NOT NULL AND ticker != ''
                ORDER BY name
            """)

            companies = cursor.fetchall()
            prices = []

            for company in companies:
                ticker = company['ticker']
                current_price = self.get_current_price(ticker)

                if current_price:
                    market_cap = (current_price * company['shares_outstanding']) if company['shares_outstanding'] else company['market_cap_estimate']

                    prices.append({
                        'company_id': company['id'],
                        'ticker': ticker,
                        'name': company['name'],
                        'current_price': current_price,
                        'market_cap': market_cap,
                        'timestamp': datetime.now().isoformat()
                    })

            return prices

        finally:
            cursor.close()

    def __del__(self):
        """Clean up database connection"""
        if self.conn and not self.conn.closed:
            self.conn.close()

# Singleton instance
_price_service = None

def get_price_service():
    """Get singleton price service instance"""
    global _price_service
    if _price_service is None:
        _price_service = RealtimePriceService()
    return _price_service
