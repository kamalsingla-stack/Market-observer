"""
Technical analysis engine for stock evaluation
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    """Technical analysis indicators and strategies"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
    
    def calculate_moving_averages(self, df: pd.DataFrame, windows: list = [20, 50, 200]) -> Dict[str, pd.Series]:
        """
        Calculate simple moving averages
        
        Args:
            df: DataFrame with 'Close' prices
            windows: List of moving average periods
        
        Returns:
            Dictionary with MA series
        """
        mas = {}
        for window in windows:
            mas[f'MA{window}'] = df['Close'].rolling(window=window).mean()
        return mas
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI)
        
        Args:
            df: DataFrame with 'Close' prices
            period: RSI period (default: 14)
        
        Returns:
            RSI series
        """
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Returns:
            macd, signal line, histogram
        """
        ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()
        
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        
        return macd, signal_line, histogram
    
    def calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Bollinger Bands
        
        Returns:
            middle (SMA), upper band, lower band
        """
        middle = df['Close'].rolling(window=period).mean()
        std = df['Close'].rolling(window=period).std()
        
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return middle, upper, lower
    
    def calculate_momentum(self, df: pd.DataFrame, period: int = 5) -> pd.Series:
        """
        Calculate price momentum
        
        Returns:
            Momentum series
        """
        return df['Close'].pct_change(periods=period) * 100
    
    def detect_trend(self, df: pd.DataFrame) -> str:
        """
        Detect current trend (uptrend, downtrend, or sideways)
        
        Returns:
            'uptrend', 'downtrend', or 'sideways'
        """
        ma20 = df['Close'].rolling(window=20).mean()
        ma50 = df['Close'].rolling(window=50).mean()
        
        current_price = df['Close'].iloc[-1]
        ma20_val = ma20.iloc[-1]
        ma50_val = ma50.iloc[-1]
        
        if current_price > ma20_val > ma50_val:
            return 'uptrend'
        elif current_price < ma20_val < ma50_val:
            return 'downtrend'
        else:
            return 'sideways'
    
    def calculate_volatility(self, df: pd.DataFrame, window: int = 20) -> float:
        """Calculate annualized volatility"""
        returns = df['Close'].pct_change()
        return returns.std() * np.sqrt(252)
    
    def analyze_stock(self, df: pd.DataFrame) -> Dict:
        """
        Comprehensive technical analysis
        
        Args:
            df: DataFrame with 'Close' prices
        
        Returns:
            Dictionary with all technical indicators
        """
        if df.empty or len(df) < 50:
            logger.warning("Insufficient data for analysis")
            return {}
        
        try:
            # Calculate indicators
            mas = self.calculate_moving_averages(df)
            rsi = self.calculate_rsi(df)
            macd, signal, histogram = self.calculate_macd(df)
            middle, upper, lower = self.calculate_bollinger_bands(df)
            momentum = self.calculate_momentum(df)
            trend = self.detect_trend(df)
            volatility = self.calculate_volatility(df)
            
            current_price = df['Close'].iloc[-1]
            
            analysis = {
                'current_price': current_price,
                'trend': trend,
                'volatility': volatility,
                'rsi': rsi.iloc[-1],
                'macd': macd.iloc[-1],
                'macd_signal': signal.iloc[-1],
                'macd_histogram': histogram.iloc[-1],
                'bb_upper': upper.iloc[-1],
                'bb_lower': lower.iloc[-1],
                'momentum': momentum.iloc[-1],
                'sma_20': mas['MA20'].iloc[-1],
                'sma_50': mas['MA50'].iloc[-1],
                'sma_200': mas['MA200'].iloc[-1]
            }
            
            return analysis
        
        except Exception as e:
            logger.error(f"Error during analysis: {e}")
            return {}
