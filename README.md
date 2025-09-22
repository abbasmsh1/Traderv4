# Multi-Agent Crypto Trading System

A sophisticated cryptocurrency trading system that combines multiple AI agents for market analysis, risk management, and automated trading decisions. The system uses real market data from Binance while executing trades in a virtual environment.

## Features

### Multi-Agent Architecture
- **Trader Agent**: Core trading decision maker
- **Risk Advisor**: Risk assessment and management
- **Technical Analyst**: Chart patterns and technical indicators
- **Financial Advisor**: Fundamental analysis and market overview
- **Sentiment Analyst**: Social media and news sentiment analysis
- **Macro Economic Analyst**: Global economic trends and impact
- **On-Chain Analyst**: Blockchain metrics and whale movements
- **Liquidity Analyst**: Market depth and execution analysis
- **Correlation Analyst**: Asset correlations and rotations
- **Consensus Advisor**: Synthesizes all analyses into actionable insights

### Real-Time Analysis
- Live market data from Binance API
- Technical indicator calculations (RSI, MACD, Moving Averages)
- Multi-timeframe analysis
- Portfolio tracking and performance metrics

### Virtual Trading Features
- Paper trading with real market data
- Virtual wallet management
- Position tracking
- Performance analytics
- State persistence between sessions

### Interactive Dashboard
- Real-time market overview
- Portfolio performance tracking
- Trade history visualization
- Agent discussion forum
- Technical charts and indicators

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Traderv4.git
cd Traderv4
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your API keys:
```env
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret
TOGETHER_API_KEY=your_together_api_key
```

## Usage

1. Start the Streamlit dashboard:
```bash
streamlit run Home.py
```

2. Access the dashboard at `http://localhost:8501`

### Dashboard Sections

#### Home Page
- Market Overview
- Portfolio Status
- Current Positions
- Trade History
- Performance Metrics

#### Agent Discussion Forum
- Real-time market analysis
- Multi-agent perspectives
- Consensus views
- Trading recommendations

## System Architecture

### Components

#### Trading System (`trading_system.py`)
- Core system coordination
- Market data management
- Trade execution
- State management

#### Agents (`agents/`)
- Base agent framework
- Specialized analysis agents
- Consensus generation

#### Wallet (`wallet.py`)
- Virtual balance management
- Position tracking
- Performance calculation

#### Dashboard (`Home.py`)
- Interactive UI
- Real-time updates
- Data visualization

### Data Flow
1. Market data fetched from Binance
2. Data processed by analysis agents
3. Consensus advisor synthesizes insights
4. Trading decisions executed virtually
5. Results displayed in dashboard

## Trading Strategy

### Analysis Layers
1. **Technical Analysis**
   - Chart patterns
   - Technical indicators
   - Volume analysis

2. **Fundamental Analysis**
   - Market conditions
   - Project fundamentals
   - Sector analysis

3. **Risk Management**
   - Position sizing
   - Portfolio diversification
   - Stop-loss management

4. **Market Sentiment**
   - Social media trends
   - News analysis
   - Community sentiment

5. **On-Chain Analysis**
   - Network metrics
   - Whale movements
   - DeFi analytics

### Decision Making
- Multi-factor analysis
- Consensus-based execution
- Risk-adjusted positioning
- Automated trade execution

## Configuration

### Trading Parameters
- Initial balance: $100 USD
- Auto BTC purchase: $20 on first run
- Position sizing: 20% of available balance
- Take profit: Dynamic based on analysis
- Stop loss: Recommended by risk advisor

### System Settings
- Analysis interval: 5 minutes (configurable)
- Auto-trading: Optional
- State persistence: Automatic
- Data refresh: Real-time

## Safety Features

- Virtual trading only
- Real market data
- Position limits
- Risk controls
- State backups

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Binance API for market data
- Together AI for agent capabilities
- Streamlit for dashboard framework
- TA-Lib for technical analysis
- LangChain for agent framework

## Disclaimer

This system is for educational and research purposes only. Do not use it for actual trading without proper testing and risk assessment. Cryptocurrency trading involves significant risk of loss.
