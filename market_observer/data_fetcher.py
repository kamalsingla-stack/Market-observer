"""
Stock data fetcher using yfinance
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, Optional, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataFetcher:
    """Fetch stock data from Yahoo Finance"""
    
    def __init__(self, history_days: int = 365):
        self.history_days = history_days
        self.cache = {}
    
    def fetch_stock_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """
        Fetch historical stock data
        
        Args:
            symbol: Stock ticker symbol
            period: Time period (default: 1 year)
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            logger.info(f"Fetching data for {symbol}")
            
            # Check cache first
            if symbol in self.cache:
                cached_date, cached_data = self.cache[symbol]
                if datetime.now() - cached_date < timedelta(hours=1):
                    logger.info(f"Using cached data for {symbol}")
                    return cached_data
            
            # Fetch from Yahoo Finance
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            
            # Cache the data
            self.cache[symbol] = (datetime.now(), df)
            
            logger.info(f"Successfully fetched {len(df)} records for {symbol}")
            return df
        
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def fetch_multiple_stocks(self, symbols: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple stocks
        
        Args:
            symbols: List of stock symbols
        
        Returns:
            Dictionary with symbol as key and DataFrame as value
        """
        data = {}
        for symbol in symbols:
            data[symbol] = self.fetch_stock_data(symbol)
        return data
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current stock price"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")
            if not data.empty:
                return data['Close'].iloc[-1]
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
        return None
    
    def get_stock_info(self, symbol: str) -> Dict:
        """Get stock information"""
        try:
            ticker = yf.Ticker(symbol)
            return ticker.info
        except Exception as e:
            logger.error(f"Error getting stock info for {symbol}: {e}")
            return {}
    
    def calculate_returns(self, df: pd.DataFrame, period: int = 1) -> pd.Series:
        """Calculate returns for given period"""
        return df['Close'].pct_change(periods=period)
    
    def calculate_volatility(self, df: pd.DataFrame, window: int = 20) -> float:
        """Calculate volatility (annualized)"""
        returns = self.calculate_returns(df)
        return returns.std() * (252 ** 0.5)  # Annualized
