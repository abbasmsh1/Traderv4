from trading_system import TradingSystem

def main():
    # Initialize the trading system with $100 USD
    trading_system = TradingSystem(initial_balance_usd=100.0)
    
    # Define the trading pair
    symbol = 'BTCUSDT'
    
    # Print initial wallet status
    print("\nInitial Wallet Status:")
    print("-" * 50)
    print(trading_system.get_wallet_summary())
    print("-" * 50)
    
    # Get market analysis from all agents
    analysis = trading_system.analyze_market(symbol)
    
    # Print the analysis from each agent
    for agent, agent_analysis in analysis.items():
        print(f"\n{agent}:")
        print("-" * 50)
        print(agent_analysis)
        print("-" * 50)
    
    # Example trade (commented out for safety - uncomment to test with real trading)
    # trading_system.execute_trade(symbol, 'buy', 50.0)  # Buy $50 worth of BTC
    
    # Print final wallet status
    print("\nFinal Wallet Status:")
    print("-" * 50)
    print(trading_system.get_wallet_summary())
    print("-" * 50)

if __name__ == "__main__":
    main()
