import streamlit as st
import pandas as pd
from trading_system import TradingSystem
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Agent Discussion Forum",
    page_icon="💬",
    layout="wide"
)

# Initialize session state for discussions
if 'trading_system' not in st.session_state:
    st.session_state.trading_system = TradingSystem(initial_balance_usd=100.0, auto_buy_btc=True)

if 'discussions' not in st.session_state:
    st.session_state.discussions = []

if 'last_discussion_update' not in st.session_state:
    st.session_state.last_discussion_update = None

st.title("Agent Discussion Forum 💬")

# Sidebar controls
st.sidebar.header("Discussion Controls")
update_interval = st.sidebar.slider("Update Interval (minutes)", 1, 60, 5)
auto_update = st.sidebar.checkbox("Enable Auto Updates", value=True)

# Main discussion area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Agent Discussions")
    
    if st.button("Start New Discussion") or (auto_update and (
        st.session_state.last_discussion_update is None or 
        time.time() - st.session_state.last_discussion_update > update_interval * 60
    )):
        with st.spinner("Agents are discussing..."):
            # Get market data for all pairs
            market_data = st.session_state.trading_system.get_all_market_data()
            
            # Get individual analyses
            trader_analysis = st.session_state.trading_system.trader.get_response(market_data, True)
            risk_analysis = st.session_state.trading_system.risk_advisor.get_response(market_data, True)
            technical_analysis = st.session_state.trading_system.graph_analyst.get_response(market_data, True)
            financial_analysis = st.session_state.trading_system.financial_advisor.get_response(market_data, True)
            
            # Create discussion entry
            discussion = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'discussion': [
                    {
                        'agent': 'Trader',
                        'message': trader_analysis,
                        'focus': 'Trading Opportunities'
                    },
                    {
                        'agent': 'Risk Advisor',
                        'message': risk_analysis,
                        'focus': 'Risk Assessment'
                    },
                    {
                        'agent': 'Technical Analyst',
                        'message': technical_analysis,
                        'focus': 'Market Patterns'
                    },
                    {
                        'agent': 'Financial Advisor',
                        'message': financial_analysis,
                        'focus': 'Market Overview'
                    }
                ]
            }
            
            st.session_state.discussions.insert(0, discussion)
            st.session_state.last_discussion_update = time.time()

    # Display discussions
    for idx, discussion in enumerate(st.session_state.discussions):
        with st.expander(f"Discussion from {discussion['timestamp']}", expanded=(idx == 0)):
            for entry in discussion['discussion']:
                st.markdown(f"**{entry['agent']} ({entry['focus']}):**")
                st.markdown(entry['message'])
                st.markdown("---")

with col2:
    st.header("Market Summary")
    
    # Get current wallet status
    wallet_summary = st.session_state.trading_system.get_wallet_summary()
    
    # Display wallet metrics
    st.metric("Total Portfolio Value", f"${wallet_summary['total_value']:.2f}")
    st.metric("Available USD", f"${wallet_summary['current_balance_usd']:.2f}")
    
    # Display positions
    st.subheader("Current Positions")
    if wallet_summary['positions']:
        positions_df = pd.DataFrame.from_dict(wallet_summary['positions'], orient='index')
        st.dataframe(positions_df)
    else:
        st.info("No open positions")
    
    # Display recent trades and statistics
    st.subheader("Trading Overview")
    
    # Display trade statistics
    if wallet_summary['trade_statistics']['total_trades'] > 0:
        st.metric("Win Rate", f"{wallet_summary['trade_statistics']['win_rate']:.1%}")
        st.metric("Total P/L", f"${wallet_summary['total_profit_usd']:.2f}")
        
        # Display most recent trades
        st.subheader("Recent Trades")
        trades_df = pd.DataFrame(st.session_state.trading_system.wallet.trade_history[-5:])
        trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp'], unit='ms')
        st.dataframe(trades_df)
    else:
        st.info("No trades yet")

# Footer
st.markdown("---")
st.markdown("*Note: Discussions are automatically updated based on the selected interval when auto-updates are enabled.*")
