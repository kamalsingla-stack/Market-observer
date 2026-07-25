# Market Observer - AI Stock Trading Agent

An intelligent agent that tracks AI-related stocks and provides buy/sell recommendations based on technical analysis and market trends.

## Features

- **Real-time Stock Tracking**: Monitor AI stocks including NVIDIA, Tesla, META, GOOGL, and more
- **Technical Analysis**: Uses moving averages, RSI, and momentum indicators
- **Buy/Sell Signals**: Generates actionable trading recommendations
- **Market Trends**: Analyzes sector-wide trends and volatility
- **Portfolio Tracking**: Keep track of your AI stock portfolio
- **Alerts**: Get notified on significant price movements and trading signals

## AI Stocks Tracked

- **NVIDIA (NVDA)** - AI chip leader
- **Tesla (TSLA)** - AI & autonomous driving
- **Meta (META)** - AI research and LLMs
- **Google (GOOGL)** - Alphabet AI division
- **Microsoft (MSFT)** - Copilot and enterprise AI
- **Adobe (ADBE)** - Generative AI tools
- **Palantir (PLTR)** - AI analytics
- **Broadcom (AVGO)** - AI infrastructure

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from market_observer import MarketAgent

# Initialize the agent
agent = MarketAgent()

# Get stock analysis
analysis = agent.analyze_stock('NVDA')
print(analysis)

# Get buy/sell recommendations
recommendation = agent.get_recommendation('NVDA')
print(recommendation)

# Monitor portfolio
portfolio_status = agent.monitor_portfolio()
print(portfolio_status)
```

## Project Structure

```
Market-observer/
├── market_observer/
│   ├── __init__.py
│   ├── agent.py              # Main agent logic
│   ├── data_fetcher.py       # Stock data collection
│   ├── analyzer.py           # Technical analysis
│   ├── config.py             # Configuration
│   └── utils.py              # Utility functions
├── scripts/
│   ├── run_agent.py          # Main entry point
│   └── backtest.py           # Backtesting tools
├── requirements.txt
├── config.yaml
└── README.md
```

## Configuration

See `config.yaml` to customize:
- Stock symbols to track
- Technical indicators parameters
- Buy/sell thresholds
- Data update frequency

## Trading Signals

- 🟢 **BUY**: Strong uptrend + RSI < 30 + bullish indicators
- 🔴 **SELL**: Strong downtrend + RSI > 70 + bearish indicators
- 🟡 **HOLD**: Mixed signals or consolidation

## Disclaimer

This tool is for educational purposes only. Not financial advice. Always consult with a financial advisor before trading.
