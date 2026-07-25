#!/usr/bin/env python3
"""
Backtesting engine for Market Observer Agent
Test strategies against historical data
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from market_observer import MarketAgent, DataFetcher

class Backtester:
    """Backtest trading strategies"""
    
    def __init__(self):
        self.agent = MarketAgent()
        self.data_fetcher = DataFetcher()
    
    def backtest_stock(self, symbol: str, initial_capital: float = 10000) -> Dict:
        """
        Backtest strategy on single stock
        
        Args:
            symbol: Stock symbol
            initial_capital: Starting capital
        
        Returns:
            Backtest results
        """
        print(f"\nBacktesting {symbol}...")
        
        # Fetch historical data
        df = self.data_fetcher.fetch_stock_data(symbol, period="2y")
        
        if df.empty:
            print(f"No data available for {symbol}")
            return {}
        
        # Initialize portfolio
        cash = initial_capital
        shares = 0
        trades = []
        portfolio_values = []
        
        # Simulate daily signals
        for i in range(50, len(df)):  # Start after 50 days for indicators
            daily_df = df.iloc[:i+1]
            analysis = self.agent.analyzer.analyze_stock(daily_df)
            
            if not analysis:
                continue
            
            signal, confidence, _ = self.agent._generate_signal(analysis)
            current_price = analysis['current_price']
            
            # Execute trades
            if signal == 'BUY' and cash > current_price:
                # Buy
                new_shares = int(cash / current_price)
                if new_shares > 0:
                    shares += new_shares
                    cash -= new_shares * current_price
                    trades.append({
                        'date': df.index[i],
                        'action': 'BUY',
                        'price': current_price,
                        'shares': new_shares
                    })
            
            elif signal == 'SELL' and shares > 0:
                # Sell all
                cash += shares * current_price
                trades.append({
                    'date': df.index[i],
                    'action': 'SELL',
                    'price': current_price,
                    'shares': shares
                })
                shares = 0
            
            # Calculate portfolio value
            portfolio_value = cash + (shares * current_price)
            portfolio_values.append(portfolio_value)
        
        # Calculate results
        final_portfolio_value = cash + (shares * current_price)
        total_return = ((final_portfolio_value - initial_capital) / initial_capital) * 100
        
        # Buy and hold comparison
        buy_hold_shares = initial_capital / df['Close'].iloc[0]
        buy_hold_value = buy_hold_shares * df['Close'].iloc[-1]
        buy_hold_return = ((buy_hold_value - initial_capital) / initial_capital) * 100
        
        results = {
            'symbol': symbol,
            'initial_capital': initial_capital,
            'final_portfolio_value': final_portfolio_value,
            'total_return_pct': total_return,
            'buy_hold_return_pct': buy_hold_return,
            'outperformance': total_return - buy_hold_return,
            'trades': len(trades),
            'win_trades': sum(1 for t in trades if t['action'] == 'SELL'),
            'max_portfolio_value': max(portfolio_values) if portfolio_values else initial_capital
        }
        
        return results
    
    def print_backtest_results(self, results: Dict):
        """Print formatted backtest results"""
        print(f"\n{'='*60}")
        print(f"BACKTEST RESULTS - {results['symbol']}")
        print(f"{'='*60}")
        print(f"Initial Capital: ${results['initial_capital']:,.2f}")
        print(f"Final Value: ${results['final_portfolio_value']:,.2f}")
        print(f"Total Return: {results['total_return_pct']:.2f}%")
        print(f"Buy & Hold Return: {results['buy_hold_return_pct']:.2f}%")
        print(f"Outperformance: {results['outperformance']:.2f}%")
        print(f"Total Trades: {results['trades']}")
        print(f"Max Portfolio Value: ${results['max_portfolio_value']:,.2f}")
        print(f"{'='*60}\n")


def main():
    backtester = Backtester()
    
    # Backtest key AI stocks
    symbols = ['NVDA', 'TSLA', 'META', 'GOOGL', 'MSFT']
    
    all_results = []
    for symbol in symbols:
        try:
            results = backtester.backtest_stock(symbol)
            if results:
                backtester.print_backtest_results(results)
                all_results.append(results)
        except Exception as e:
            print(f"Error backtesting {symbol}: {e}")
    
    # Print summary
    if all_results:
        print(f"\n{'='*60}")
        print("BACKTEST SUMMARY")
        print(f"{'='*60}")
        avg_return = sum(r['total_return_pct'] for r in all_results) / len(all_results)
        avg_outperformance = sum(r['outperformance'] for r in all_results) / len(all_results)
        print(f"Average Return: {avg_return:.2f}%")
        print(f"Average Outperformance vs B&H: {avg_outperformance:.2f}%")
        print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
