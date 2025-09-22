import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from trading_system import TradingSystem
import time

# Page configuration
st.set_page_config(
    page_title="Trading Dashboard",
    page_icon="📈",
    layout="wide"
)

# Initialize session state
if 'trading_system' not in st.session_state:
    st.session_state.trading_system = TradingSystem(initial_balance_usd=100.0, auto_buy_btc=True)
    
if 'last_update' not in st.session_state:
    st.session_state.last_update = None

# Sidebar
st.sidebar.title("Trading Controls")

# System Controls
with st.sidebar.expander("System Controls", expanded=False):
    if st.button("Reset Trading System"):
        if st.session_state.trading_system.reset_system():
            st.session_state.trading_system = TradingSystem(initial_balance_usd=100.0, auto_buy_btc=True)
            st.rerun()

# Trading Pair Selection
symbol = st.sidebar.selectbox(
    "Select Trading Pair",
    [
        "BTCUSDT",  # Bitcoin
        "ETHUSDT",  # Ethereum
        "BNBUSDT",  # Binance Coin
        "ADAUSDT",  # Cardano
        "DOTUSDT",  # Polkadot
        "SOLUSDT",  # Solana
        "AVAXUSDT", # Avalanche
        "MATICUSDT", # Polygon
        "LINKUSDT", # Chainlink
        "ATOMUSDT", # Cosmos
        "ALGOUSDT", # Algorand
        "NEARUSDT", # NEAR Protocol
        "FTMUSDT",  # Fantom
        "SANDUSDT", # The Sandbox
        "MANAUSDT"  # Decentraland
    ]
)

# Autonomous Trading Controls
st.sidebar.subheader("Autonomous Trading")
auto_trade = st.sidebar.checkbox("Enable Autonomous Trading", value=True)
trade_interval = st.sidebar.slider("Analysis Interval (minutes)", 1, 60, 5)

# Trading Strategy Parameters
st.sidebar.subheader("Strategy Parameters")
st.sidebar.info("""
Autonomous Trading Rules:
- Initial $20 BTC purchase
- Uses 20% of available balance for new positions
- Sells 50% of existing positions when sell signal
- Executes within 1% of recommended price
- Analysis every {} minutes
""".format(trade_interval))

# Main dashboard
st.title("Trading Dashboard 📈")

# Market Overview
st.header("Market Overview")
market_overview = pd.DataFrame(st.session_state.trading_system.get_market_overview())
market_overview['price'] = market_overview['price'].map('${:,.2f}'.format)
market_overview['volume_24h'] = market_overview['volume_24h'].map('${:,.0f}'.format)
market_overview['price_change_24h'] = market_overview['price_change_24h'].map('{:+.2f}%'.format)
market_overview['rsi'] = market_overview['rsi'].map('{:.1f}'.format)

# Color-code the price change column
def color_price_change(val):
    val = float(val.strip('%').strip('+'))
    color = 'green' if val > 0 else 'red'
    return f'color: {color}'

styled_overview = market_overview.style.map(
    color_price_change,
    subset=['price_change_24h']
)
st.dataframe(styled_overview, height=400)

# Portfolio Overview
st.header("Portfolio Overview")
col1, col2, col3 = st.columns(3)

# Get wallet summary
wallet_summary = st.session_state.trading_system.get_wallet_summary()

col1.metric(
    "Total Portfolio Value",
    f"${wallet_summary['total_value']:.2f}",
    f"{(wallet_summary['total_value'] - wallet_summary['initial_balance_usd']):.2f}"
)

col2.metric(
    "Available USD",
    f"${wallet_summary['current_balance_usd']:.2f}"
)

col3.metric(
    "Number of Positions",
    len(wallet_summary['positions'])
)

# Current Positions
st.subheader("Current Positions")
if wallet_summary['positions']:
    positions_df = pd.DataFrame.from_dict(wallet_summary['positions'], orient='index')
    st.dataframe(positions_df)
else:
    st.info("No open positions")

# Market Analysis
st.header("Market Analysis")
analysis_type = st.radio(
    "Analysis Type",
    ["Single Pair", "All Pairs"],
    horizontal=True
)

if st.button("Analyze Market") or (auto_trade and (st.session_state.last_update is None or 
    time.time() - st.session_state.last_update > trade_interval * 60)):
    
    with st.spinner("Analyzing market..."):
        if analysis_type == "Single Pair":
            analysis = st.session_state.trading_system.analyze_market(symbol)
        else:
            analysis = st.session_state.trading_system.analyze_market()
        st.session_state.last_update = time.time()
        
        # Display analysis from each agent in expandable sections
        for agent, agent_analysis in analysis.items():
            with st.expander(agent, expanded=True):
                st.write(agent_analysis)

# Market Data Visualization
st.header("Market Data Visualization")
market_data = st.session_state.trading_system.get_market_data(symbol)
if market_data:
    # Convert market data to DataFrame for visualization
    df = pd.DataFrame([market_data])
    
    # Candlestick chart
    fig = go.Figure(data=[go.Candlestick(
        open=[market_data['open']],
        high=[market_data['high']],
        low=[market_data['low']],
        close=[market_data['close']]
    )])
    fig.update_layout(title=f"{symbol} Price", xaxis_title="Time", yaxis_title="Price")
    st.plotly_chart(fig)
    
    # Technical Indicators
    indicators_fig = go.Figure()
    indicators_fig.add_trace(go.Scatter(y=[market_data['RSI']], name='RSI'))
    indicators_fig.add_trace(go.Scatter(y=[market_data['SMA_20']], name='SMA 20'))
    indicators_fig.add_trace(go.Scatter(y=[market_data['SMA_50']], name='SMA 50'))
    indicators_fig.update_layout(title="Technical Indicators", xaxis_title="Time", yaxis_title="Value")
    st.plotly_chart(indicators_fig)

# Trade History
st.header("Trade History")
if wallet_summary['trade_statistics']['total_trades'] > 0:
    trades_df = pd.DataFrame(st.session_state.trading_system.wallet.trade_history)
    trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp'], unit='ms')
    st.dataframe(trades_df)
    
    # Show trade statistics
    st.subheader("Trading Statistics")
    stats_col1, stats_col2, stats_col3 = st.columns(3)
    
    stats_col1.metric(
        "Win Rate",
        f"{wallet_summary['trade_statistics']['win_rate']:.1%}"
    )
    
    stats_col2.metric(
        "Total Profit/Loss",
        f"${wallet_summary['total_profit_usd']:.2f}"
    )
    
    stats_col3.metric(
        "Avg. Profit per Day",
        f"${wallet_summary['trade_statistics']['avg_profit_per_day']:.2f}"
    )
    
    # Trade Performance Visualization
    fig = px.line(trades_df, x='timestamp', y='balance_after', 
                  title='Portfolio Balance History')
    st.plotly_chart(fig)
else:
    st.info("No trades executed yet")

# Autonomous Trading Execution
if auto_trade:
    current_time = time.time()
    if (st.session_state.last_update is None or 
        current_time - st.session_state.last_update > trade_interval * 60):
        
        with st.spinner("Analyzing market and executing trades..."):
            # Always analyze all pairs in autonomous mode
            analysis = st.session_state.trading_system.analyze_market()
            st.session_state.last_update = current_time
            
            # Display analysis from each agent in expandable sections
            for agent, agent_analysis in analysis.items():
                with st.expander(agent, expanded=True):
                    st.write(agent_analysis)
    
    # Schedule next update
    time.sleep(1)
    st.rerun()
