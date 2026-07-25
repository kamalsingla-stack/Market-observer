#!/usr/bin/env python3
"""
Main entry point for Market Observer Agent
Run this script to get stock recommendations
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from market_observer import MarketAgent
from market_observer.utils import ReportGenerator

def main():
    parser = argparse.ArgumentParser(
        description="Market Observer - AI Stock Trading Agent"
    )
    parser.add_argument(
        '--symbol',
        help='Analyze specific stock symbol (e.g., NVDA)',
        type=str
    )
    parser.add_argument(
        '--portfolio',
        action='store_true',
        help='Analyze entire AI stock portfolio'
    )
    parser.add_argument(
        '--sector',
        action='store_true',
        help='Show AI sector trend analysis'
    )
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = MarketAgent()
    
    if args.symbol:
        # Single stock analysis
        print(f"\n📊 Analyzing {args.symbol}...")
        recommendation = agent.get_recommendation(args.symbol)
        print(ReportGenerator.format_recommendation(recommendation))
        
        # Print technical analysis
        if recommendation.get('analysis'):
            analysis = recommendation['analysis']
            print("Technical Indicators:")
            print(f"  Current Price: ${analysis.get('current_price', 'N/A'):.2f}")
            print(f"  Trend: {analysis.get('trend', 'N/A')}")
            print(f"  RSI: {analysis.get('rsi', 'N/A'):.2f}")
            print(f"  SMA 20: ${analysis.get('sma_20', 'N/A'):.2f}")
            print(f"  SMA 50: ${analysis.get('sma_50', 'N/A'):.2f}")
            print(f"  SMA 200: ${analysis.get('sma_200', 'N/A'):.2f}")
            print(f"  Volatility: {analysis.get('volatility', 'N/A'):.2%}")
    
    elif args.sector:
        # Sector trend analysis
        print("\n📈 Analyzing AI Sector Trends...\n")
        sector_analysis = agent.get_sector_trend()
        print(ReportGenerator.format_sector_analysis(sector_analysis))
    
    else:
        # Full portfolio analysis (default)
        print("\n📊 Analyzing AI Stock Portfolio...\n")
        portfolio = agent.analyze_portfolio()
        print(ReportGenerator.format_portfolio_analysis(portfolio))
        
        # Also show sector trend
        print("\n" + ReportGenerator.format_sector_analysis(agent.get_sector_trend()))


if __name__ == '__main__':
    main()
