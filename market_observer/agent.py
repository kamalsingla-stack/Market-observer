"""
Main Market Observer Agent - Buy/Sell recommendation engine
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import pandas as pd

from .data_fetcher import DataFetcher
from .analyzer import TechnicalAnalyzer
from .config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketAgent:
    """
    Intelligent agent that analyzes AI stocks and provides buy/sell recommendations
    """
    
    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.analyzer = TechnicalAnalyzer()
        self.config = config
        self.analysis_cache = {}
        self.recommendations = {}
    
    def get_recommendation(self, symbol: str) -> Dict:
        """
        Get buy/sell recommendation for a stock
        
        Args:
            symbol: Stock ticker symbol
        
        Returns:
            Dictionary with recommendation, confidence, and reasoning
        """
        try:
            # Fetch data
            df = self.data_fetcher.fetch_stock_data(symbol)
            if df.empty:
                return self._create_recommendation(symbol, "ERROR", 0, "Unable to fetch data")
            
            # Analyze
            analysis = self.analyzer.analyze_stock(df)
            if not analysis:
                return self._create_recommendation(symbol, "ERROR", 0, "Analysis failed")
            
            # Generate signal
            signal, confidence, reasoning = self._generate_signal(analysis)
            
            return self._create_recommendation(symbol, signal, confidence, reasoning, analysis)
        
        except Exception as e:
            logger.error(f"Error getting recommendation for {symbol}: {e}")
            return self._create_recommendation(symbol, "ERROR", 0, str(e))
    
    def _generate_signal(self, analysis: Dict) -> Tuple[str, float, str]:
        """
        Generate trading signal based on technical analysis
        
        Returns:
            (signal, confidence, reasoning)
        """
        thresholds = self.config.get_signal_thresholds()
        
        scores = {
            'rsi': self._score_rsi(analysis['rsi']),
            'macd': self._score_macd(analysis['macd'], analysis['macd_signal']),
            'trend': self._score_trend(analysis['trend']),
            'momentum': self._score_momentum(analysis['momentum']),
            'bollinger': self._score_bollinger(analysis['current_price'], analysis['bb_upper'], analysis['bb_lower'])
        }
        
        # Calculate overall confidence
        buy_score = (
            scores['rsi'][0] * 0.25 +
            scores['macd'][0] * 0.25 +
            scores['trend'][0] * 0.25 +
            scores['momentum'][0] * 0.15 +
            scores['bollinger'][0] * 0.10
        )
        
        sell_score = (
            scores['rsi'][1] * 0.25 +
            scores['macd'][1] * 0.25 +
            scores['trend'][1] * 0.25 +
            scores['momentum'][1] * 0.15 +
            scores['bollinger'][1] * 0.10
        )
        
        # Determine signal
        buy_threshold = thresholds.get('buy_threshold', 0.65)
        sell_threshold = thresholds.get('sell_threshold', 0.65)
        
        if buy_score > buy_threshold and buy_score > sell_score:
            signal = 'BUY'
            confidence = min(buy_score, 1.0)
            reasoning = self._build_reasoning(scores, 'BUY')
        elif sell_score > sell_threshold and sell_score > buy_score:
            signal = 'SELL'
            confidence = min(sell_score, 1.0)
            reasoning = self._build_reasoning(scores, 'SELL')
        else:
            signal = 'HOLD'
            confidence = max(buy_score, sell_score)
            reasoning = "Mixed signals. Hold position or wait for clearer trend."
        
        return signal, confidence, reasoning
    
    def _score_rsi(self, rsi: float) -> Tuple[float, float]:
        """
        Score RSI for buy/sell signals
        
        Returns:
            (buy_score, sell_score)
        """
        if rsi < 30:
            return (0.8, 0.1)  # Strong buy signal
        elif rsi < 40:
            return (0.6, 0.2)
        elif rsi > 70:
            return (0.1, 0.8)  # Strong sell signal
        elif rsi > 60:
            return (0.2, 0.6)
        else:
            return (0.3, 0.3)  # Neutral
    
    def _score_macd(self, macd: float, signal: float) -> Tuple[float, float]:
        """
        Score MACD for buy/sell signals
        
        Returns:
            (buy_score, sell_score)
        """
        if macd > signal:
            strength = min(abs(macd - signal) / abs(signal) if signal != 0 else 0, 1.0)
            return (0.5 + strength * 0.4, 0.1)  # Buy signal
        else:
            strength = min(abs(macd - signal) / abs(signal) if signal != 0 else 0, 1.0)
            return (0.1, 0.5 + strength * 0.4)  # Sell signal
    
    def _score_trend(self, trend: str) -> Tuple[float, float]:
        """Score trend direction"""
        if trend == 'uptrend':
            return (0.7, 0.2)
        elif trend == 'downtrend':
            return (0.2, 0.7)
        else:  # sideways
            return (0.3, 0.3)
    
    def _score_momentum(self, momentum: float) -> Tuple[float, float]:
        """Score price momentum"""
        if momentum > 2:
            return (0.7, 0.2)
        elif momentum < -2:
            return (0.2, 0.7)
        else:
            return (0.3, 0.3)
    
    def _score_bollinger(self, price: float, upper: float, lower: float) -> Tuple[float, float]:
        """Score Bollinger Bands position"""
        middle = (upper + lower) / 2
        
        if price < lower:
            return (0.8, 0.2)  # Oversold - buy signal
        elif price > upper:
            return (0.2, 0.8)  # Overbought - sell signal
        elif price < middle:
            return (0.5, 0.3)
        else:
            return (0.3, 0.5)
    
    def _build_reasoning(self, scores: Dict, signal: str) -> str:
        """Build human-readable reasoning for the signal"""
        reasons = []
        
        if signal == 'BUY':
            if scores['rsi'][0] > scores['rsi'][1]:
                reasons.append("RSI shows oversold conditions")
            if scores['trend'][0] > scores['trend'][1]:
                reasons.append("Strong uptrend identified")
            if scores['momentum'][0] > scores['momentum'][1]:
                reasons.append("Positive momentum observed")
            if scores['bollinger'][0] > scores['bollinger'][1]:
                reasons.append("Price near support levels")
        
        elif signal == 'SELL':
            if scores['rsi'][1] > scores['rsi'][0]:
                reasons.append("RSI shows overbought conditions")
            if scores['trend'][1] > scores['trend'][0]:
                reasons.append("Strong downtrend identified")
            if scores['momentum'][1] > scores['momentum'][0]:
                reasons.append("Negative momentum observed")
            if scores['bollinger'][1] > scores['bollinger'][0]:
                reasons.append("Price near resistance levels")
        
        return " | ".join(reasons) if reasons else "Technical analysis suggests this signal"
    
    def _create_recommendation(self, symbol: str, signal: str, confidence: float, reasoning: str, analysis: Dict = None) -> Dict:
        """Create recommendation dictionary"""
        return {
            'symbol': symbol,
            'signal': signal,
            'confidence': round(confidence, 3),
            'reasoning': reasoning,
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis,
            'emoji': self._get_emoji(signal)
        }
    
    def _get_emoji(self, signal: str) -> str:
        """Get emoji for signal"""
        return {'BUY': '🟢', 'SELL': '🔴', 'HOLD': '🟡', 'ERROR': '❌'}.get(signal, '❓')
    
    def analyze_portfolio(self, symbols: List[str] = None) -> Dict:
        """
        Analyze multiple stocks
        
        Args:
            symbols: List of stock symbols (uses config if not provided)
        
        Returns:
            Dictionary with recommendations for all stocks
        """
        if symbols is None:
            symbols = self.config.get_stocks()
        
        portfolio_analysis = {
            'timestamp': datetime.now().isoformat(),
            'stocks': {}
        }
        
        buy_count = 0
        sell_count = 0
        hold_count = 0
        
        for symbol in symbols:
            recommendation = self.get_recommendation(symbol)
            portfolio_analysis['stocks'][symbol] = recommendation
            
            if recommendation['signal'] == 'BUY':
                buy_count += 1
            elif recommendation['signal'] == 'SELL':
                sell_count += 1
            elif recommendation['signal'] == 'HOLD':
                hold_count += 1
        
        portfolio_analysis['summary'] = {
            'buy_signals': buy_count,
            'sell_signals': sell_count,
            'hold_signals': hold_count,
            'total_stocks': len(symbols)
        }
        
        return portfolio_analysis
    
    def get_sector_trend(self) -> Dict:
        """
        Get overall AI sector trend
        
        Returns:
            Dictionary with sector analysis
        """
        symbols = self.config.get_stocks()
        portfolio = self.analyze_portfolio(symbols)
        summary = portfolio['summary']
        
        buy_percentage = (summary['buy_signals'] / summary['total_stocks']) * 100
        sell_percentage = (summary['sell_signals'] / summary['total_stocks']) * 100
        
        if buy_percentage > 50:
            trend = 'BULLISH'
        elif sell_percentage > 50:
            trend = 'BEARISH'
        else:
            trend = 'NEUTRAL'
        
        return {
            'trend': trend,
            'buy_signals': summary['buy_signals'],
            'sell_signals': summary['sell_signals'],
            'hold_signals': summary['hold_signals'],
            'buy_percentage': round(buy_percentage, 2),
            'sell_percentage': round(sell_percentage, 2)
        }
