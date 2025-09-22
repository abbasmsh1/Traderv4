import time

class Wallet:
    def __init__(self, initial_balance_usd=100.0, state=None):
        if state is None:
            print(f"Initializing virtual trading wallet with ${initial_balance_usd}")
            print("NOTE: All trades are simulated with real market data")
            self.initial_balance_usd = initial_balance_usd
            self.current_balance_usd = initial_balance_usd
            self.positions = {}  # Format: {"BTCUSDT": {"amount": 0.001, "avg_price": 45000, "total_cost": 45.0}}
            self.trade_history = []
            self.start_time = int(time.time() * 1000)  # Track when we started trading
        else:
            print("Restoring wallet from saved state")
            self.initial_balance_usd = state['initial_balance_usd']
            self.current_balance_usd = state['current_balance_usd']
            self.positions = state['positions']
            self.trade_history = state['trade_history']
            self.start_time = state['start_time']
            print(f"Restored wallet with ${self.current_balance_usd:.2f} balance and {len(self.positions)} positions")
            
        self.virtual_mode = True  # Always true as we're using virtual trading
        
    def can_execute_trade(self, symbol, side, amount_usd):
        """Check if there's enough balance to execute a trade"""
        if side.lower() == 'buy':
            return self.current_balance_usd >= amount_usd
        elif side.lower() == 'sell':
            if symbol not in self.positions:
                return False
            return True
        return False
    
    def update_after_trade(self, symbol, side, amount, price, timestamp):
        """Update wallet after a successful trade"""
        trade_value_usd = amount * price
        
        if side.lower() == 'buy':
            # Deduct from USD balance
            self.current_balance_usd -= trade_value_usd
            # Add to positions
            if symbol in self.positions:
                current_amount = self.positions[symbol]['amount']
                current_avg_price = self.positions[symbol]['avg_price']
                total_value = (current_amount * current_avg_price) + trade_value_usd
                new_amount = current_amount + amount
                self.positions[symbol] = {
                    'amount': new_amount,
                    'avg_price': total_value / new_amount
                }
            else:
                self.positions[symbol] = {
                    'amount': amount,
                    'avg_price': price
                }
        
        elif side.lower() == 'sell':
            # Add to USD balance
            self.current_balance_usd += trade_value_usd
            # Remove from positions
            if symbol in self.positions:
                current_amount = self.positions[symbol]['amount']
                if current_amount <= amount:
                    del self.positions[symbol]
                else:
                    self.positions[symbol]['amount'] = current_amount - amount
        
        # Record trade in history
        self.trade_history.append({
            'timestamp': timestamp,
            'symbol': symbol,
            'side': side,
            'amount': amount,
            'price': price,
            'value_usd': trade_value_usd,
            'balance_after': self.current_balance_usd
        })
    
    def get_position_value(self, symbol, current_price):
        """Get the current value of a position"""
        if symbol in self.positions:
            return self.positions[symbol]['amount'] * current_price
        return 0.0
    
    def get_total_value(self, price_dict):
        """Get total portfolio value including all positions"""
        total = self.current_balance_usd
        for symbol, position in self.positions.items():
            if symbol in price_dict:
                total += position['amount'] * price_dict[symbol]
        return total
    
    def get_portfolio_summary(self):
        """Get a detailed summary of current portfolio state"""
        # Calculate profit/loss from trades
        total_profit = 0
        winning_trades = 0
        for trade in self.trade_history:
            if trade['side'].lower() == 'sell':
                symbol = trade['symbol']
                sell_value = trade['amount'] * trade['price']
                # Find matching buy trade
                for prev_trade in self.trade_history:
                    if (prev_trade['symbol'] == symbol and 
                        prev_trade['side'].lower() == 'buy' and 
                        prev_trade['timestamp'] < trade['timestamp']):
                        buy_value = prev_trade['amount'] * prev_trade['price']
                        profit = sell_value - buy_value
                        total_profit += profit
                        if profit > 0:
                            winning_trades += 1
                        break

        # Calculate time in market
        time_in_market = int(time.time() * 1000) - self.start_time
        days_in_market = time_in_market / (1000 * 60 * 60 * 24)

        return {
            'mode': 'Virtual Trading with Real Market Data',
            'initial_balance_usd': self.initial_balance_usd,
            'current_balance_usd': self.current_balance_usd,
            'total_profit_usd': total_profit,
            'positions': self.positions,
            'trade_statistics': {
                'total_trades': len(self.trade_history),
                'winning_trades': winning_trades,
                'win_rate': winning_trades / len(self.trade_history) if self.trade_history else 0,
                'days_trading': round(days_in_market, 2),
                'avg_profit_per_day': round(total_profit / days_in_market, 2) if days_in_market > 0 else 0
            }
        }
