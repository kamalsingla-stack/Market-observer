"""
Utility functions for Market Observer
"""

import json
from datetime import datetime
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generate formatted reports"""
    
    @staticmethod
    def format_recommendation(recommendation: Dict) -> str:
        """Format recommendation as readable text"""
        output = f"\n{recommendation['emoji']} {recommendation['symbol']} - {recommendation['signal']}\n"
        output += f"Confidence: {recommendation['confidence']:.1%}\n"
        output += f"Reasoning: {recommendation['reasoning']}\n"
        output += f"Time: {recommendation['timestamp']}\n"
        return output
    
    @staticmethod
    def format_portfolio_analysis(portfolio: Dict) -> str:
        """Format portfolio analysis as readable text"""
        output = "\n" + "="*60 + "\n"
        output += "PORTFOLIO ANALYSIS\n"
        output += "="*60 + "\n"
        output += f"Timestamp: {portfolio['timestamp']}\n\n"
        
        summary = portfolio['summary']
        output += f"Summary:\n"
        output += f"  🟢 BUY Signals: {summary['buy_signals']}\n"
        output += f"  🔴 SELL Signals: {summary['sell_signals']}\n"
        output += f"  🟡 HOLD Signals: {summary['hold_signals']}\n"
        output += f"  Total Stocks: {summary['total_stocks']}\n\n"
        
        output += "Individual Stock Analysis:\n"
        for symbol, rec in portfolio['stocks'].items():
            output += f"{rec['emoji']} {symbol}: {rec['signal']} ({rec['confidence']:.1%})\n"
            output += f"   → {rec['reasoning']}\n"
        
        output += "\n" + "="*60 + "\n"
        return output
    
    @staticmethod
    def format_sector_analysis(sector_analysis: Dict) -> str:
        """Format sector trend analysis"""
        output = "\n" + "="*60 + "\n"
        output += "AI SECTOR ANALYSIS\n"
        output += "="*60 + "\n"
        
        trend_emoji = {
            'BULLISH': '📈',
            'BEARISH': '📉',
            'NEUTRAL': '➡️'
        }
        
        output += f"Sector Trend: {trend_emoji.get(sector_analysis['trend'])} {sector_analysis['trend']}\n"
        output += f"  🟢 Buy Signals: {sector_analysis['buy_signals']} ({sector_analysis['buy_percentage']:.1f}%)\n"
        output += f"  🔴 Sell Signals: {sector_analysis['sell_signals']} ({sector_analysis['sell_percentage']:.1f}%)\n"
        output += f"  🟡 Hold Signals: {sector_analysis['hold_signals']}\n\n"
        
        output += "Interpretation:\n"
        if sector_analysis['trend'] == 'BULLISH':
            output += "The AI stock sector is showing strong bullish momentum.\n"
            output += "Consider increasing exposure to AI stocks in your portfolio.\n"
        elif sector_analysis['trend'] == 'BEARISH':
            output += "The AI stock sector is showing strong bearish pressure.\n"
            output += "Consider taking profits or reducing AI stock exposure.\n"
        else:
            output += "The AI stock sector is consolidating.\n"
            output += "Monitor for breakout signals before making major moves.\n"
        
        output += "\n" + "="*60 + "\n"
        return output


class PortfolioTracker:
    """Track portfolio positions and performance"""
    
    def __init__(self):
        self.positions = {}
    
    def add_position(self, symbol: str, quantity: int, entry_price: float):
        """Add a position to portfolio"""
        self.positions[symbol] = {
            'quantity': quantity,
            'entry_price': entry_price,
            'entry_date': datetime.now().isoformat(),
            'current_price': entry_price,
            'gain_loss': 0,
            'gain_loss_pct': 0
        }
        logger.info(f"Added position: {quantity} x {symbol} @ ${entry_price}")
    
    def update_price(self, symbol: str, current_price: float):
        """Update current price for a position"""
        if symbol in self.positions:
            pos = self.positions[symbol]
            pos['current_price'] = current_price
            pos['gain_loss'] = (current_price - pos['entry_price']) * pos['quantity']
            pos['gain_loss_pct'] = ((current_price - pos['entry_price']) / pos['entry_price']) * 100
    
    def get_portfolio_value(self) -> float:
        """Get total portfolio value"""
        total = 0
        for pos in self.positions.values():
            total += pos['current_price'] * pos['quantity']
        return total
    
    def get_total_gain_loss(self) -> Tuple[float, float]:
        """Get total gain/loss (absolute and percentage)"""
        total_gain_loss = 0
        total_invested = 0
        
        for pos in self.positions.values():
            total_gain_loss += pos['gain_loss']
            total_invested += pos['entry_price'] * pos['quantity']
        
        pct = (total_gain_loss / total_invested * 100) if total_invested > 0 else 0
        return total_gain_loss, pct
    
    def get_portfolio_report(self) -> str:
        """Get formatted portfolio report"""
        output = "\n" + "="*60 + "\n"
        output += "PORTFOLIO REPORT\n"
        output += "="*60 + "\n"
        
        for symbol, pos in self.positions.items():
            output += f"\n{symbol}\n"
            output += f"  Quantity: {pos['quantity']}\n"
            output += f"  Entry Price: ${pos['entry_price']:.2f}\n"
            output += f"  Current Price: ${pos['current_price']:.2f}\n"
            output += f"  Gain/Loss: ${pos['gain_loss']:.2f} ({pos['gain_loss_pct']:.2f}%)\n"
        
        total_gain_loss, pct = self.get_total_gain_loss()
        output += f"\nTotal Gain/Loss: ${total_gain_loss:.2f} ({pct:.2f}%)\n"
        output += f"Portfolio Value: ${self.get_portfolio_value():.2f}\n"
        output += "\n" + "="*60 + "\n"
        
        return output


def save_analysis_to_file(filename: str, data: Dict):
    """Save analysis to JSON file"""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f"Analysis saved to {filename}")
    except Exception as e:
        logger.error(f"Error saving analysis: {e}")


def load_analysis_from_file(filename: str) -> Dict:
    """Load analysis from JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading analysis: {e}")
        return {}
