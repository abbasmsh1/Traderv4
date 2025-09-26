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
    if st.button("Export Market CSV"):
        ok = st.session_state.trading_system.save_all_market_data_csv()
        if ok:
            st.sidebar.success("Market data appended to CSV")
        else:
            st.sidebar.error("Failed to write CSV")

# Trading Pair Selection
coin_category = st.sidebar.radio(
    "Coin Category",
    ["Major Coins", "Meme Coins", "All"],
    help="Filter coins by category"
)

# Filter symbols based on category
if coin_category == "Major Coins":
    available_symbols = [
        "BTCUSDT",  # Bitcoin
        "ETHUSDT",  # Ethereum
        "BNBUSDT",  # Binance Coin
        "SOLUSDT",  # Solana
        "ADAUSDT",  # Cardano
        "XRPUSDT",  # XRP
        "TRXUSDT",  # TRON
        "LTCUSDT",  # Litecoin
        "BCHUSDT",  # Bitcoin Cash
        "DOTUSDT",  # Polkadot
        "MATICUSDT", # Polygon
        "AVAXUSDT",  # Avalanche
        "LINKUSDT",  # Chainlink
        "ATOMUSDT",  # Cosmos
        "FILUSDT",   # Filecoin
        "NEARUSDT",  # NEAR Protocol
        "ARBUSDT",   # Arbitrum
        "OPUSDT",    # Optimism
        "SUIUSDT",   # Sui
        "SEIUSDT",   # Sei
        "RUNEUSDT"   # THORChain
    ]
elif coin_category == "Meme Coins":
    available_symbols = [
        "DOGEUSDT",  # Dogecoin
        "SHIBUSDT",  # Shiba Inu
        "PEPEUSDT",  # Pepe
        "FLOKIUSDT", # Floki
        "BONKUSDT",  # Bonk
        "WIFUSDT",   # dogwifhat
        "MEMEUSDT",  # Memecoin
        "GMTUSDT",   # STEPN
        "GALAUSDT",  # Gala Games
        "APTUSDT",   # Aptos
        "IMXUSDT",   # Immutable X
        "MASKUSDT",  # Mask Network
        "FETUSDT",   # Fetch.ai
        "AGIXUSDT",  # SingularityNET
        "ICPUSDT",   # Internet Computer
        "JASMYUSDT", # JasmyCoin
        "GMXUSDT",   # GMX
        "CHZUSDT",   # Chiliz
        "PERPUSDT",  # Perpetual Protocol
        "STXUSDT",   # Stacks
        "REEFUSDT",  # Reef
        "TRUUSDT"    # TrueFi
    ]
else:
    available_symbols = [
        # Major Coins
        "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "ADAUSDT",
        "XRPUSDT", "TRXUSDT", "LTCUSDT", "BCHUSDT", "DOTUSDT",
        "MATICUSDT", "AVAXUSDT", "LINKUSDT", "ATOMUSDT", "FILUSDT",
        "NEARUSDT", "ARBUSDT", "OPUSDT", "SUIUSDT", "SEIUSDT", "RUNEUSDT",
        # Meme/Alt Coins
        "DOGEUSDT", "SHIBUSDT", "PEPEUSDT", "FLOKIUSDT", "BONKUSDT",
        "WIFUSDT", "MEMEUSDT", "GMTUSDT", "GALAUSDT", "APTUSDT",
        "IMXUSDT", "MASKUSDT", "FETUSDT", "AGIXUSDT", "ICPUSDT",
        "JASMYUSDT", "GMXUSDT", "CHZUSDT", "PERPUSDT", "STXUSDT",
        "REEFUSDT", "TRUUSDT"
    ]

symbol = st.sidebar.selectbox(
    "Select Trading Pair",
    available_symbols
)

# Autonomous Trading Controls
st.sidebar.subheader("Autonomous Trading")
auto_trade = st.sidebar.checkbox("Enable Autonomous Trading", value=True)
trade_interval = st.sidebar.slider("Analysis Interval (minutes)", 1, 60, 5)

# Trading Strategy Parameters
st.sidebar.subheader("Strategy Parameters")
st.sidebar.info("""
Autonomous Trading Rules:
- Initial $5 BTC purchase (minimum order size)
- Uses 20% of available balance for new positions
- Sells 50% of existing positions when sell signal
- Executes within 1% of recommended price
- 0.1% trading fees applied
- Realistic slippage simulation
- Analysis every {} minutes
""".format(trade_interval))

# Main dashboard
st.title("Trading Dashboard 📈")

# Market Overview
st.header("Market Overview")

# Define color function for price changes
def color_price_change(val):
    try:
        val = float(val.strip('%').strip('+'))
        color = 'green' if val > 0 else 'red'
        return f'color: {color}'
    except:
        return 'color: black'

market_overview = pd.DataFrame(st.session_state.trading_system.get_market_overview())

# Define major coins list
major_coins = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "ADAUSDT",
    "DOTUSDT", "MATICUSDT", "AVAXUSDT", "LINKUSDT", "ATOMUSDT"
]

# Add category column
market_overview['category'] = market_overview['symbol'].apply(
    lambda x: 'Major Coin' if x in major_coins else 'Meme Coin'
)

# Format columns
market_overview['price'] = market_overview['price'].map('${:,.2f}'.format)
market_overview['volume_24h'] = market_overview['volume_24h'].map('${:,.0f}'.format)
market_overview['price_change_24h'] = market_overview['price_change_24h'].map('{:+.2f}%'.format)
market_overview['rsi'] = market_overview['rsi'].map('{:.1f}'.format)

# Split into major and meme coins
major_df = market_overview[market_overview['category'] == 'Major Coin'].copy()
meme_df = market_overview[market_overview['category'] == 'Meme Coin'].copy()

# Create two columns for the market overview
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔷 Major Cryptocurrencies")
    # Drop category column and style the dataframe
    display_major_df = major_df.drop(columns=['category'])
    major_styled = display_major_df.style.map(
        color_price_change,
        subset=['price_change_24h']
    )
    st.dataframe(major_styled, height=400)
    
    # Add summary metrics for major coins
    avg_major_change = pd.to_numeric(major_df['price_change_24h'].str.rstrip('%').str.replace('+', '')).mean()
    total_major_volume = pd.to_numeric(major_df['volume_24h'].str.replace('$', '').str.replace(',', '')).sum()
    st.metric("Average 24h Change", f"{avg_major_change:+.2f}%")
    st.metric("Total Volume", f"${total_major_volume:,.0f}")

with col2:
    st.subheader("🎮 Meme Coins")
    # Drop category column and style the dataframe
    display_meme_df = meme_df.drop(columns=['category'])
    meme_styled = display_meme_df.style.map(
        color_price_change,
        subset=['price_change_24h']
    )
    st.dataframe(meme_styled, height=400)
    
    # Add summary metrics for meme coins
    avg_meme_change = pd.to_numeric(meme_df['price_change_24h'].str.rstrip('%').str.replace('+', '')).mean()
    total_meme_volume = pd.to_numeric(meme_df['volume_24h'].str.replace('$', '').str.replace(',', '')).sum()
    st.metric("Average 24h Change", f"{avg_meme_change:+.2f}%")
    st.metric("Total Volume", f"${total_meme_volume:,.0f}")

# Add market movement summary
st.subheader("Market Movement Summary")
movement_cols = st.columns(4)

with movement_cols[0]:
    major_up = len(major_df[pd.to_numeric(major_df['price_change_24h'].str.rstrip('%')) > 0])
    st.metric("Major Coins Up", f"{major_up}/{len(major_df)}")

with movement_cols[1]:
    major_down = len(major_df) - major_up
    st.metric("Major Coins Down", f"{major_down}/{len(major_df)}")

with movement_cols[2]:
    meme_up = len(meme_df[pd.to_numeric(meme_df['price_change_24h'].str.rstrip('%')) > 0])
    st.metric("Meme Coins Up", f"{meme_up}/{len(meme_df)}")

with movement_cols[3]:
    meme_down = len(meme_df) - meme_up
    st.metric("Meme Coins Down", f"{meme_down}/{len(meme_df)}")

# Display combined overview in expandable section
with st.expander("View All Coins", expanded=False):
    # Drop category column for display
    display_overview = market_overview.drop(columns=['category'])
    styled_overview = display_overview.style.map(
        color_price_change,
        subset=['price_change_24h']
    )
    st.dataframe(styled_overview, height=400)

# Portfolio Overview
st.header("Portfolio Overview")

# Get wallet summary
wallet_summary = st.session_state.trading_system.get_wallet_summary()

# Store previous values in session state if not exist
if 'last_portfolio_value' not in st.session_state:
    st.session_state.last_portfolio_value = wallet_summary['total_value']
if 'highest_portfolio_value' not in st.session_state:
    st.session_state.highest_portfolio_value = wallet_summary['total_value']
if 'lowest_portfolio_value' not in st.session_state:
    st.session_state.lowest_portfolio_value = wallet_summary['total_value']

# Calculate changes
total_change = wallet_summary['total_value'] - wallet_summary['initial_balance_usd']
total_change_pct = (total_change / wallet_summary['initial_balance_usd']) * 100

recent_change = wallet_summary['total_value'] - st.session_state.last_portfolio_value
recent_change_pct = (recent_change / st.session_state.last_portfolio_value) * 100 if st.session_state.last_portfolio_value else 0

# Update session state
st.session_state.last_portfolio_value = wallet_summary['total_value']
st.session_state.highest_portfolio_value = max(st.session_state.highest_portfolio_value, wallet_summary['total_value'])
st.session_state.lowest_portfolio_value = min(st.session_state.lowest_portfolio_value, wallet_summary['total_value'])

# Create columns for metrics
col1, col2, col3, col4 = st.columns(4)

# Total Portfolio Value with total change
col1.metric(
    "Total Portfolio Value",
    f"${wallet_summary['total_value']:.2f}",
    f"{total_change_pct:+.2f}% (${total_change:+.2f})",
    delta_color="normal"
)

# Recent change (since last update)
col2.metric(
    "Recent Change",
    f"${wallet_summary['total_value']:.2f}",
    f"{recent_change_pct:+.2f}% (${recent_change:+.2f})",
    delta_color="normal"
)

# Available USD
col3.metric(
    "Available USD",
    f"${wallet_summary['current_balance_usd']:.2f}",
    f"{len(wallet_summary['positions'])} positions"
)

# High/Low Indicators
col4.metric(
    "Portfolio High/Low",
    f"H: ${st.session_state.highest_portfolio_value:.2f}",
    f"L: ${st.session_state.lowest_portfolio_value:.2f}"
)

# Add a small chart showing portfolio value trend
if 'portfolio_value_history' not in st.session_state:
    st.session_state.portfolio_value_history = []
    st.session_state.portfolio_value_times = []

# Update portfolio history
current_time = datetime.now()
st.session_state.portfolio_value_history.append(wallet_summary['total_value'])
st.session_state.portfolio_value_times.append(current_time)

# Keep only last 100 points
if len(st.session_state.portfolio_value_history) > 100:
    st.session_state.portfolio_value_history.pop(0)
    st.session_state.portfolio_value_times.pop(0)

# Create mini chart
if len(st.session_state.portfolio_value_history) > 1:
    fig = px.line(
        x=st.session_state.portfolio_value_times,
        y=st.session_state.portfolio_value_history,
        title="Portfolio Value Trend"
    )
    fig.update_layout(
        showlegend=False,
        height=200,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

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
        if isinstance(analysis, dict):
            for agent, agent_analysis in analysis.items():
                with st.expander(agent, expanded=True):
                    st.write(agent_analysis)
        else:
            st.error(str(analysis))

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
            if isinstance(analysis, dict):
                for agent, agent_analysis in analysis.items():
                    with st.expander(agent, expanded=True):
                        st.write(agent_analysis)
            else:
                st.error(str(analysis))
            
            # Run scalping position manager after analysis
            st.session_state.trading_system.manage_open_positions()
    
    # Schedule next update
    time.sleep(1)
    st.rerun()
