import json
import os
from datetime import datetime

class StateManager:
    def __init__(self, state_file='trading_state.json'):
        self.state_file = state_file
        
    def save_state(self, wallet_data):
        """Save the wallet state to a JSON file"""
        state = {
            'initial_balance_usd': wallet_data.initial_balance_usd,
            'current_balance_usd': wallet_data.current_balance_usd,
            'positions': wallet_data.positions,
            'trade_history': wallet_data.trade_history,
            'start_time': wallet_data.start_time,
            'last_saved': datetime.now().isoformat()
        }
        
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=4)
            print(f"State saved successfully to {self.state_file}")
            return True
        except Exception as e:
            print(f"Error saving state: {e}")
            return False
            
    def load_state(self):
        """Load the wallet state from a JSON file"""
        if not os.path.exists(self.state_file):
            print("No saved state found")
            return None
            
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)
            print(f"State loaded successfully from {self.state_file}")
            return state
        except Exception as e:
            print(f"Error loading state: {e}")
            return None
            
    def delete_state(self):
        """Delete the saved state file"""
        if os.path.exists(self.state_file):
            try:
                os.remove(self.state_file)
                print(f"State file {self.state_file} deleted successfully")
                return True
            except Exception as e:
                print(f"Error deleting state file: {e}")
                return False
        return True  # Return True if file doesn't exist
