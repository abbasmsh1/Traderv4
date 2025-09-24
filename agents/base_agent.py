from langchain_together import Together
from langchain.schema import SystemMessage
from langchain.globals import set_verbose
import json

# Set verbosity globally
set_verbose(False)

class BaseAgent:
    def __init__(self, api_key):
        # LLM is optional to support non-LLM agents
        if api_key:
            self.llm = Together(
                model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                temperature=0.7,
                together_api_key=api_key,
                max_tokens=2048
            )
        else:
            self.llm = None
        self.system_message = None
        
    def get_response(self, market_data, multi_pair=False):
        """
        Get agent's response based on market data
        Args:
            market_data (dict): Current market data including price, volume, indicators, etc.
            multi_pair (bool): Whether the data contains multiple pairs
        Returns:
            str: Agent's analysis and recommendation
        """
        if not self.system_message:
            raise NotImplementedError("System message must be defined in child class")
        
        if not multi_pair:
            # Format single pair market data
            formatted_data = {
                "price_data": {
                    "close": float(market_data.get("close", 0)),
                    "open": float(market_data.get("open", 0)),
                    "high": float(market_data.get("high", 0)),
                    "low": float(market_data.get("low", 0)),
                    "volume": float(market_data.get("volume", 0))
                },
                "indicators": {
                    "RSI": float(market_data.get("RSI", 0)),
                    "SMA_20": float(market_data.get("SMA_20", 0)),
                    "SMA_50": float(market_data.get("SMA_50", 0)),
                    "MACD": float(market_data.get("MACD", 0)),
                    "MACD_SIGNAL": float(market_data.get("MACD_SIGNAL", 0)),
                    "MACD_HIST": float(market_data.get("MACD_HIST", 0)),
                    "price_change_24h": float(market_data.get("price_change_24h", 0))
                }
            }
        else:
            # Format multi-pair market data
            formatted_data = {}
            for symbol, data in market_data.items():
                formatted_data[symbol] = {
                    "price_data": {
                        "close": float(data.get("close", 0)),
                        "open": float(data.get("open", 0)),
                        "high": float(data.get("high", 0)),
                        "low": float(data.get("low", 0)),
                        "volume": float(data.get("volume", 0))
                    },
                    "indicators": {
                        "RSI": float(data.get("RSI", 0)),
                        "SMA_20": float(data.get("SMA_20", 0)),
                        "SMA_50": float(data.get("SMA_50", 0)),
                        "MACD": float(data.get("MACD", 0)),
                        "MACD_SIGNAL": float(data.get("MACD_SIGNAL", 0)),
                        "MACD_HIST": float(data.get("MACD_HIST", 0)),
                        "price_change_24h": float(data.get("price_change_24h", 0))
                    }
                }
        
        prompt = f"""<s>[INST] {self.system_message.content}

Current Market Data:
{json.dumps(formatted_data, indent=2)}

Please provide your analysis based on this market data. [/INST]</s>"""
        
        if self.llm is None:
            return "LLM disabled: missing Together API key. Set TOGETHER_API_KEY to enable this agent."
        try:
            response = self.llm.invoke(prompt)
            return response
        except Exception as e:
            return f"Error getting analysis: {str(e)}. Please check your Together API key and try again."
