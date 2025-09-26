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
from agents.rl_agent import RLForecastAgent
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
        mistral_key = os.getenv('MISTRAL_API_KEY')
        # Core trading agents
        self.trader = TraderAgent(mistral_key)
        self.risk_advisor = RiskAdvisorAgent(mistral_key)
        self.graph_analyst = GraphAnalystAgent(mistral_key)
        self.financial_advisor = FinancialAdvisorAgent(mistral_key)
        
        # Specialized analysis agents
        self.sentiment_analyst = SentimentAnalysisAgent(mistral_key)
        self.macro_analyst = MacroEconomicAgent(mistral_key)
        self.onchain_analyst = OnChainAnalysisAgent(mistral_key)
        self.liquidity_analyst = LiquidityAnalysisAgent(mistral_key)
        self.correlation_analyst = CorrelationAnalysisAgent(mistral_key)
        
        # Consensus advisor (synthesizes all analyses)
        self.consensus_advisor = ConsensusAdvisorAgent(mistral_key)

        # RL + LSTM forecast agent (optional, uses CSV history)
        self.rl_forecast_agent = RLForecastAgent(csv_path='market_data.csv')
        
        # Scalping configuration (micro profits, quick losses)
        self.scalp_take_profit_pct = 0.0025  # 0.25%
        self.scalp_stop_loss_pct = 0.0015    # 0.15%
        
        # Automatic initial BTC purchase only if:
        # 1. auto_buy_btc is enabled
        # 2. No saved state was loaded
        # 3. No positions exist in the wallet
        # 4. Balance is at least $5 (minimum order size)
        if (auto_buy_btc and 
            saved_state is None and 
            not self.wallet.positions and 
            self.wallet.current_balance_usd >= 5.0):
            print("Making initial BTC purchase...")
            self.execute_trade('BTCUSDT', 'BUY', 5.0)
        
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
                "XRPUSDT",  # XRP
                "TRXUSDT",  # TRON
                "LTCUSDT",  # Litecoin
                "BCHUSDT",  # Bitcoin Cash
                "DOTUSDT",  # Polkadot
                "MATICUSDT", # Polygon
                "AVAXUSDT", # Avalanche
                "LINKUSDT", # Chainlink
                "ATOMUSDT",  # Cosmos
                "FILUSDT",   # Filecoin
                "NEARUSDT",  # NEAR Protocol
                "ARBUSDT",   # Arbitrum
                "OPUSDT",    # Optimism
                "SUIUSDT",   # Sui
                "SEIUSDT",   # Sei
                "RUNEUSDT"   # THORChain
            ]
            
            # Meme coins and community tokens (verified on Binance)
            meme_coins = [
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

    def save_all_market_data_csv(self, filepath='market_data.csv'):
        """Fetch all market data and append to a CSV snapshot (one row per symbol)."""
        try:
            market_data = self.get_all_market_data()
            if not market_data:
                return False

            import pandas as pd
            from datetime import datetime
            rows = []
            timestamp = int(pd.Timestamp.utcnow().timestamp() * 1000)
            for symbol, data in market_data.items():
                rows.append({
                    'timestamp': timestamp,
                    'symbol': symbol,
                    'open': data.get('open'),
                    'high': data.get('high'),
                    'low': data.get('low'),
                    'close': data.get('close'),
                    'volume': data.get('volume'),
                    'RSI': data.get('RSI'),
                    'SMA_20': data.get('SMA_20'),
                    'SMA_50': data.get('SMA_50'),
                    'MACD': data.get('MACD'),
                    'MACD_SIGNAL': data.get('MACD_SIGNAL'),
                    'MACD_HIST': data.get('MACD_HIST'),
                    'price_change_24h': data.get('price_change_24h')
                })

            df = pd.DataFrame(rows)
            # Append or create
            import os
            if os.path.exists(filepath):
                df.to_csv(filepath, mode='a', header=False, index=False)
            else:
                df.to_csv(filepath, index=False)
            return True
        except Exception as e:
            print(f"Error saving market data CSV: {e}")
            return False
        
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
                
                if action == 'buy' and available_usd >= 5:
                    # Use 10% of available balance or $5 minimum, whichever is larger (scalping)
                    trade_amount = max(available_usd * 0.1, 5)
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
            def _format_prompt(agent, md, multi_pair_flag):
                try:
                    base = agent.system_message.content if hasattr(agent, 'system_message') and agent.system_message else ""
                except Exception:
                    base = ""
                if not multi_pair_flag:
                    formatted = {
                        "price_data": {
                            "close": float(md.get("close", 0)),
                            "open": float(md.get("open", 0)),
                            "high": float(md.get("high", 0)),
                            "low": float(md.get("low", 0)),
                            "volume": float(md.get("volume", 0)),
                        },
                        "indicators": {
                            "RSI": float(md.get("RSI", 0)),
                            "SMA_20": float(md.get("SMA_20", 0)),
                            "SMA_50": float(md.get("SMA_50", 0)),
                            "MACD": float(md.get("MACD", 0)),
                            "MACD_SIGNAL": float(md.get("MACD_SIGNAL", 0)),
                            "MACD_HIST": float(md.get("MACD_HIST", 0)),
                            "price_change_24h": float(md.get("price_change_24h", 0)),
                        },
                    }
                else:
                    formatted = {}
                    for sym, data in md.items():
                        formatted[sym] = {
                            "price_data": {
                                "close": float(data.get("close", 0)),
                                "open": float(data.get("open", 0)),
                                "high": float(data.get("high", 0)),
                                "low": float(data.get("low", 0)),
                                "volume": float(data.get("volume", 0)),
                            },
                            "indicators": {
                                "RSI": float(data.get("RSI", 0)),
                                "SMA_20": float(data.get("SMA_20", 0)),
                                "SMA_50": float(data.get("SMA_50", 0)),
                                "MACD": float(data.get("MACD", 0)),
                                "MACD_SIGNAL": float(data.get("MACD_SIGNAL", 0)),
                                "MACD_HIST": float(data.get("MACD_HIST", 0)),
                                "price_change_24h": float(data.get("price_change_24h", 0)),
                            },
                        }
                import json as _json
                return f"""
{base}

Current Market Data:
{_json.dumps(formatted, indent=2)}

Provide your analysis based on this market data.
"""
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
                prompt = _format_prompt(self.trader, market_data, multi_pair)
                analyses["Trader's Analysis"] = self.trader.get_response(prompt)
            except Exception as e:
                analyses["Trader's Analysis"] = f"Error: {str(e)}"
                
            try:
                prompt = _format_prompt(self.risk_advisor, market_data, multi_pair)
                analyses["Risk Assessment"] = self.risk_advisor.get_response(prompt)
            except Exception as e:
                analyses["Risk Assessment"] = f"Error: {str(e)}"
                
            try:
                prompt = _format_prompt(self.graph_analyst, market_data, multi_pair)
                analyses["Technical Analysis"] = self.graph_analyst.get_response(prompt)
            except Exception as e:
                analyses["Technical Analysis"] = f"Error: {str(e)}"
                
            try:
                prompt = _format_prompt(self.financial_advisor, market_data, multi_pair)
                analyses["Financial Analysis"] = self.financial_advisor.get_response(prompt)
            except Exception as e:
                analyses["Financial Analysis"] = f"Error: {str(e)}"
                
            # Specialized analyses
            try:
                prompt = _format_prompt(self.sentiment_analyst, market_data, multi_pair)
                analyses["Market Sentiment"] = self.sentiment_analyst.get_response(prompt)
            except Exception as e:
                analyses["Market Sentiment"] = f"Error: {str(e)}"
                
            try:
                prompt = _format_prompt(self.macro_analyst, market_data, multi_pair)
                analyses["Macro Environment"] = self.macro_analyst.get_response(prompt)
            except Exception as e:
                analyses["Macro Environment"] = f"Error: {str(e)}"
                
            try:
                prompt = _format_prompt(self.onchain_analyst, market_data, multi_pair)
                analyses["On-Chain Metrics"] = self.onchain_analyst.get_response(prompt)
            except Exception as e:
                analyses["On-Chain Metrics"] = f"Error: {str(e)}"
                
            try:
                prompt = _format_prompt(self.liquidity_analyst, market_data, multi_pair)
                analyses["Liquidity Analysis"] = self.liquidity_analyst.get_response(prompt)
            except Exception as e:
                analyses["Liquidity Analysis"] = f"Error: {str(e)}"
                
            try:
                prompt = _format_prompt(self.correlation_analyst, market_data, multi_pair)
                analyses["Correlation Analysis"] = self.correlation_analyst.get_response(prompt)
            except Exception as e:
                analyses["Correlation Analysis"] = f"Error: {str(e)}"
                
            # Get consensus view after collecting all analyses
            try:
                analyses["Consensus Summary"] = self.consensus_advisor.get_consensus(analyses)
            except Exception as e:
                analyses["Consensus Summary"] = f"Error generating consensus: {str(e)}"

            # Pass the consensus summary back into the trader for a final plan
            try:
                consensus_text = analyses.get("Consensus Summary", "")
                if isinstance(consensus_text, str):
                    final_trader_plan = self.trader.get_trade_from_consensus(consensus_text, market_data, multi_pair)
                    analyses["Trader's Final Plan"] = final_trader_plan
            except Exception as e:
                analyses["Trader's Final Plan"] = f"Error generating final plan: {str(e)}"

            # RL Forecast agent analysis (uses CSV history if available)
            try:
                analyses["RL Forecast"] = self.rl_forecast_agent.get_response(market_data, multi_pair)
            except Exception as e:
                analyses["RL Forecast"] = f"Error in RL Forecast: {str(e)}"
            
            # Extract and execute trades automatically if analyzing all pairs
            if multi_pair:
                trading_signals = self.extract_trading_signals(analyses)
                self.execute_autonomous_trades(trading_signals)
            
            return analyses
            
        except Exception as e:
            return f"Error in market analysis: {str(e)}"
    
    def manage_open_positions(self):
        """
        Scalping manager: close positions quickly for micro-profits or small losses.
        Sells 100% of position when thresholds are met.
        """
        try:
            symbols = list(self.wallet.positions.keys())
            for symbol in symbols:
                try:
                    pos = self.wallet.positions.get(symbol)
                    if not pos:
                        continue
                    avg_price = float(pos.get('avg_price', 0) or 0)
                    if avg_price <= 0:
                        continue
                    # Current price
                    ticker = self.client.get_symbol_ticker(symbol=symbol)
                    current_price = float(ticker['price'])
                    pnl_pct = (current_price - avg_price) / avg_price
                    # Decide action
                    if pnl_pct >= self.scalp_take_profit_pct or pnl_pct <= -self.scalp_stop_loss_pct:
                        # Sell full position
                        amount_base = pos.get('amount', 0.0)
                        if amount_base <= 0:
                            continue
                        amount_usd = amount_base * current_price
                        self.execute_trade(symbol, 'sell', amount_usd)
                except Exception as e:
                    print(f"Scalp manager error for {symbol}: {e}")
        except Exception as e:
            print(f"Scalp manager error: {e}")
        
    def execute_trade(self, symbol, side, amount_usd):
        """
        Execute a virtual trade using real market data with realistic conditions
        """
        try:
            # Get real-time price from Binance
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            current_price = float(ticker['price'])
            
            # Get symbol information for precision and minimum order size
            info = self.client.get_symbol_info(symbol)
            lot_size_filter = next((x for x in info['filters'] if x['filterType'] == 'LOT_SIZE'), None)
            min_notional_filter = next((x for x in info['filters'] if x['filterType'] == 'MIN_NOTIONAL'), None)
            
            step_size = float(lot_size_filter['stepSize'])
            qty_precision = len(str(step_size).split('.')[-1])
            min_notional = float(min_notional_filter['minNotional']) if min_notional_filter else 5.0
            
            # Calculate quantity based on USD amount
            quantity = amount_usd / current_price
            quantity = round(quantity, qty_precision)
            
            # Apply realistic slippage (0.01% to 0.1% for liquid pairs)
            import random
            slippage_factor = random.uniform(0.0001, 0.001)  # 0.01% to 0.1%
            if side.lower() == 'buy':
                execution_price = current_price * (1 + slippage_factor)
            else:
                execution_price = current_price * (1 - slippage_factor)
            
            # Calculate realistic trading fees (0.1% maker/taker)
            trade_value = quantity * execution_price
            fees_usd = trade_value * 0.001  # 0.1% fee
            
            # Check minimum order value
            if trade_value < min_notional:
                raise Exception(f"Order value ${trade_value:.2f} below minimum ${min_notional:.2f} for {symbol}")
            
            # Check if we can execute the virtual trade
            can_trade, error_msg = self.wallet.can_execute_trade(symbol, side, trade_value)
            if not can_trade:
                raise Exception(error_msg or f"Insufficient virtual funds for {side} trade of ${trade_value:.2f}")
            
            # Create virtual order with realistic execution
            import time
            order = {
                'symbol': symbol,
                'side': side.upper(),
                'status': 'FILLED',
                'executedQty': str(quantity),
                'fills': [{'price': str(execution_price)}],
                'transactTime': int(time.time() * 1000),
                'type': 'VIRTUAL',
                'fees': fees_usd,
                'slippage': slippage_factor
            }
            
            # Update virtual wallet with fees
            self.wallet.update_after_trade(
                symbol=symbol,
                side=side,
                amount=float(order['executedQty']),
                price=float(order['fills'][0]['price']),
                timestamp=order['transactTime'],
                fees_usd=fees_usd
            )
            
            print(f"Virtual {side.upper()} order executed: {quantity} {symbol} @ ${execution_price:.4f} (fees: ${fees_usd:.2f}, slippage: {slippage_factor:.4f})")
            
            # Save system state after successful trade
            self.save_system_state()
            
            return order
            
        except BinanceAPIException as e:
            print(f"Error executing trade: {e}")
            return None
        except Exception as e:
            print(f"Error executing virtual trade: {e}")
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
