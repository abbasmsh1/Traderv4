import os
from dotenv import load_dotenv
from binance.client import Client
from binance.exceptions import BinanceAPIException
import pandas as pd
import talib
from agents.specialized_agents import (
    TraderAgent,
    RiskAdvisorAgent,
    GraphAnalystAgent,
    FinancialAdvisorAgent,
    ConsensusAdvisorAgent,
    SentimentAnalysisAgent,
    MacroEconomicAgent,
    OnChainAnalysisAgent,
    LiquidityAnalysisAgent,
    CorrelationAnalysisAgent
)
from wallet import Wallet

from state_manager import StateManager

class TradingSystem:
    def __init__(self, initial_balance_usd=100.0, auto_buy_btc=True, load_saved_state=True):
        load_dotenv()
        
        # Initialize state manager
        self.state_manager = StateManager()
        
        # Initialize Binance client for real market data
        self.client = Client(
            os.getenv('BINANCE_API_KEY'),
            os.getenv('BINANCE_API_SECRET')
        )
        
        # Test connection and verify market data access
        try:
            self.client.get_system_status()
            print("Successfully connected to Binance (Read-only mode)")
            print("Trading will be executed virtually with real market data")
        except Exception as e:
            print(f"Warning: Could not connect to Binance: {e}")
            return
        
        # Load saved state if available
        saved_state = self.state_manager.load_state() if load_saved_state else None
        self.wallet = Wallet(initial_balance_usd, state=saved_state)
        
        # Initialize agents
        together_key = os.getenv('TOGETHER_API_KEY')
        # Core trading agents
        self.trader = TraderAgent(together_key)
        self.risk_advisor = RiskAdvisorAgent(together_key)
        self.graph_analyst = GraphAnalystAgent(together_key)
        self.financial_advisor = FinancialAdvisorAgent(together_key)
        
        # Specialized analysis agents
        self.sentiment_analyst = SentimentAnalysisAgent(together_key)
        self.macro_analyst = MacroEconomicAgent(together_key)
        self.onchain_analyst = OnChainAnalysisAgent(together_key)
        self.liquidity_analyst = LiquidityAnalysisAgent(together_key)
        self.correlation_analyst = CorrelationAnalysisAgent(together_key)
        
        # Consensus advisor (synthesizes all analyses)
        self.consensus_advisor = ConsensusAdvisorAgent(together_key)
        
        # Automatic initial BTC purchase only if:
        # 1. auto_buy_btc is enabled
        # 2. No saved state was loaded
        # 3. No positions exist in the wallet
        if (auto_buy_btc and 
            saved_state is None and 
            not self.wallet.positions and 
            self.wallet.current_balance_usd >= 20.0):
            print("Making initial BTC purchase...")
            self.execute_trade('BTCUSDT', 'BUY', 20.0)
        
    def reset_system(self, initial_balance_usd=100.0):
        """Reset the trading system to initial state"""
        self.state_manager.delete_state()
        self.wallet = Wallet(initial_balance_usd)
        return True
        
    def save_system_state(self):
        """Save the current system state"""
        return self.state_manager.save_state(self.wallet)
        
        # Automatic initial BTC purchase
        if auto_buy_btc:
            self.execute_trade('BTCUSDT', 'buy', 20.0)
        
    def get_market_data(self, symbol, interval='1h', limit=100):
        """
        Fetch market data and calculate technical indicators for a single symbol
        """
        try:
            # Get kline data
            klines = self.client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            
            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Convert price columns to float
            df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
            
            # Calculate technical indicators
            df['RSI'] = talib.RSI(df['close'])
            macd, macdsignal, macdhist = talib.MACD(df['close'])
            df['MACD'] = macd
            df['MACD_SIGNAL'] = macdsignal
            df['MACD_HIST'] = macdhist
            df['SMA_20'] = talib.SMA(df['close'], timeperiod=20)
            df['SMA_50'] = talib.SMA(df['close'], timeperiod=50)
            
            # Add 24h price change percentage
            df['price_change_24h'] = ((df['close'] - df['close'].shift(24)) / df['close'].shift(24)) * 100
            
            return df.iloc[-1].to_dict()  # Return the most recent data point
            
        except BinanceAPIException as e:
            print(f"Error fetching market data: {e}")
            return None
            
    def get_all_market_data(self, symbols=None, interval='1h', limit=100):
        """
        Fetch market data for multiple symbols including major coins and meme tokens
        """
        if symbols is None:
            # Major cryptocurrencies (verified on Binance)
            major_coins = [
                "BTCUSDT",  # Bitcoin
                "ETHUSDT",  # Ethereum
                "BNBUSDT",  # Binance Coin
                "SOLUSDT",  # Solana
                "ADAUSDT",  # Cardano
                "DOTUSDT",  # Polkadot
                "MATICUSDT", # Polygon
                "AVAXUSDT", # Avalanche
                "LINKUSDT", # Chainlink
                "ATOMUSDT"  # Cosmos
            ]
            
            # Meme coins and community tokens (verified on Binance)
            meme_coins = [
                "DOGEUSDT",  # Dogecoin
                "SHIBUSDT",  # Shiba Inu
                "PEPEUSDT",  # Pepe
                "FLOKIUSDT", # Floki
                "INJUSDT",   # Injective (New DeFi meme)
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
            
            symbols = major_coins + meme_coins
            
            # Verify symbols are valid on Binance
            valid_symbols = []
            for symbol in symbols:
                try:
                    # Test if symbol exists by getting ticker
                    self.client.get_symbol_ticker(symbol=symbol)
                    valid_symbols.append(symbol)
                except Exception as e:
                    print(f"Skipping invalid symbol {symbol}: {str(e)}")
                    continue
            
            symbols = valid_symbols
        
        market_data = {}
        for symbol in symbols:
            data = self.get_market_data(symbol, interval, limit)
            if data:
                market_data[symbol] = data
        
        return market_data
        
    def get_market_overview(self):
        """
        Get a quick overview of all supported trading pairs
        """
        market_data = self.get_all_market_data()
        overview = []
        
        for symbol, data in market_data.items():
            overview.append({
                'symbol': symbol,
                'price': data['close'],
                'volume_24h': data['volume'],
                'price_change_24h': data.get('price_change_24h', 0),
                'rsi': data['RSI']
            })
        
        return overview
            
    def extract_trading_signals(self, analysis):
        """
        Extract trading signals from agent analysis
        """
        trading_signals = []
        
        try:
            # Parse trader's analysis for specific recommendations
            trader_analysis = analysis.get("Trader's Analysis", "")
            if isinstance(trader_analysis, str) and "Top Trading Opportunities" in trader_analysis:
                for line in trader_analysis.split('\n'):
                    if "Symbol:" in line:
                        symbol = line.split("Symbol:")[1].strip()
                    elif "Action:" in line:
                        action = line.split("Action:")[1].strip().lower()
                    elif "Entry Price:" in line:
                        try:
                            entry_price = float(line.split("Entry Price:")[1].strip().replace('$', ''))
                            if all(v is not None for v in [symbol, action]):
                                trading_signals.append({
                                    'symbol': symbol,
                                    'action': action,
                                    'entry_price': entry_price
                                })
                        except (ValueError, AttributeError):
                            continue
        except Exception as e:
            print(f"Error extracting trading signals: {e}")
            
        return trading_signals

    def execute_autonomous_trades(self, trading_signals):
        """
        Execute trades based on agent recommendations
        """
        for signal in trading_signals:
            symbol = signal['symbol']
            action = signal['action']
            
            # Get current price
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            current_price = float(ticker['price'])
            
            # Check if price is within 1% of recommended entry
            price_diff_pct = abs(current_price - signal['entry_price']) / signal['entry_price']
            
            if price_diff_pct <= 0.01:  # Within 1% of recommended entry
                available_usd = self.wallet.current_balance_usd
                
                if action == 'buy' and available_usd >= 20:
                    # Use 20% of available balance or $20, whichever is larger
                    trade_amount = max(available_usd * 0.2, 20)
                    self.execute_trade(symbol, action, trade_amount)
                    
                elif action == 'sell' and symbol in self.wallet.positions:
                    # Sell 50% of the position
                    position = self.wallet.positions[symbol]
                    trade_amount = position['amount'] * current_price * 0.5
                    self.execute_trade(symbol, action, trade_amount)

    def analyze_market(self, symbol=None):
        """
        Get analysis from all agents and make a trading decision
        If symbol is None, analyze all pairs
        """
        try:
            # Get market data
            if symbol:
                market_data = self.get_market_data(symbol)
                if not market_data:
                    return "Failed to fetch market data"
                multi_pair = False
            else:
                market_data = self.get_all_market_data()
                if not market_data:
                    return "Failed to fetch market data"
                multi_pair = True
            
            # Get analysis from each agent
            analyses = {
                # Core analyses
                "Trader's Analysis": None,
                "Risk Assessment": None,
                "Technical Analysis": None,
                "Financial Analysis": None,
                # Specialized analyses
                "Market Sentiment": None,
                "Macro Environment": None,
                "On-Chain Metrics": None,
                "Liquidity Analysis": None,
                "Correlation Analysis": None
            }
            
            # Core analyses
            try:
                analyses["Trader's Analysis"] = self.trader.get_response(market_data, multi_pair)
            except Exception as e:
                analyses["Trader's Analysis"] = f"Error: {str(e)}"
                
            try:
                analyses["Risk Assessment"] = self.risk_advisor.get_response(market_data, multi_pair)
            except Exception as e:
                analyses["Risk Assessment"] = f"Error: {str(e)}"
                
            try:
                analyses["Technical Analysis"] = self.graph_analyst.get_response(market_data, multi_pair)
            except Exception as e:
                analyses["Technical Analysis"] = f"Error: {str(e)}"
                
            try:
                analyses["Financial Analysis"] = self.financial_advisor.get_response(market_data, multi_pair)
            except Exception as e:
                analyses["Financial Analysis"] = f"Error: {str(e)}"
                
            # Specialized analyses
            try:
                analyses["Market Sentiment"] = self.sentiment_analyst.get_response(market_data, multi_pair)
            except Exception as e:
                analyses["Market Sentiment"] = f"Error: {str(e)}"
                
            try:
                analyses["Macro Environment"] = self.macro_analyst.get_response(market_data, multi_pair)
            except Exception as e:
                analyses["Macro Environment"] = f"Error: {str(e)}"
                
            try:
                analyses["On-Chain Metrics"] = self.onchain_analyst.get_response(market_data, multi_pair)
            except Exception as e:
                analyses["On-Chain Metrics"] = f"Error: {str(e)}"
                
            try:
                analyses["Liquidity Analysis"] = self.liquidity_analyst.get_response(market_data, multi_pair)
            except Exception as e:
                analyses["Liquidity Analysis"] = f"Error: {str(e)}"
                
            try:
                analyses["Correlation Analysis"] = self.correlation_analyst.get_response(market_data, multi_pair)
            except Exception as e:
                analyses["Correlation Analysis"] = f"Error: {str(e)}"
                
            # Get consensus view after collecting all analyses
            try:
                analyses["Consensus Summary"] = self.consensus_advisor.get_consensus(analyses)
            except Exception as e:
                analyses["Consensus Summary"] = f"Error generating consensus: {str(e)}"
            
            # Extract and execute trades automatically if analyzing all pairs
            if multi_pair:
                trading_signals = self.extract_trading_signals(analyses)
                self.execute_autonomous_trades(trading_signals)
            
            return analyses
            
        except Exception as e:
            return f"Error in market analysis: {str(e)}"
        
    def execute_trade(self, symbol, side, amount_usd):
        """
        Execute a virtual trade using real market data
        """
        try:
            # Get real-time price from Binance
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            current_price = float(ticker['price'])
            
            # Get symbol information for precision
            info = self.client.get_symbol_info(symbol)
            lot_size_filter = next((x for x in info['filters'] if x['filterType'] == 'LOT_SIZE'), None)
            step_size = float(lot_size_filter['stepSize'])
            qty_precision = len(str(step_size).split('.')[-1])
            
            # Calculate quantity based on USD amount
            quantity = amount_usd / current_price
            quantity = round(quantity, qty_precision)
            
            # Check if we can execute the virtual trade
            if not self.wallet.can_execute_trade(symbol, side, amount_usd):
                raise Exception(f"Insufficient virtual funds for {side} trade of {amount_usd} USD")
            
            # Create virtual order with real market price
            import time
            order = {
                'symbol': symbol,
                'side': side.upper(),
                'status': 'FILLED',
                'executedQty': str(quantity),
                'fills': [{'price': str(current_price)}],
                'transactTime': int(time.time() * 1000),
                'type': 'VIRTUAL'  # Mark as virtual trade
            }
            
            # Update virtual wallet
            self.wallet.update_after_trade(
                symbol=symbol,
                side=side,
                amount=float(order['executedQty']),
                price=float(order['fills'][0]['price']),
                timestamp=order['transactTime']
            )
            
            print(f"Virtual {side.upper()} order executed: {quantity} {symbol} @ ${current_price}")
            
            # Save system state after successful trade
            self.save_system_state()
            
            return order
            
        except Exception as e:
            print(f"Error executing virtual trade: {e}")
            return None
            
        except BinanceAPIException as e:
            print(f"Error executing trade: {e}")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
            
    def get_wallet_summary(self):
        """
        Get current wallet status
        """
        # Get current prices for all positions
        price_dict = {}
        for symbol in self.wallet.positions.keys():
            try:
                ticker = self.client.get_symbol_ticker(symbol=symbol)
                price_dict[symbol] = float(ticker['price'])
            except BinanceAPIException:
                price_dict[symbol] = 0.0
        
        summary = self.wallet.get_portfolio_summary()
        summary['total_value'] = self.wallet.get_total_value(price_dict)
        return summary
