import json
from langchain.schema import SystemMessage
from .base_agent import BaseAgent


# ============================
# Specialized Agents
# ============================

class TraderAgent(BaseAgent):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.system_message = SystemMessage(content="""You are an expert cryptocurrency trader...""")

    def get_trade_from_consensus(self, consensus_summary: str, market_data: dict, multi_pair: bool = False) -> str:
        """
        Generate a trading plan using consensus summary and market data.
        """
        consensus_section = f"<CONSENSUS_SUMMARY>\n{consensus_summary}\n</CONSENSUS_SUMMARY>"

        # Format market data
        if not multi_pair:
            formatted_data = {
                "price_data": {k: float(market_data.get(k, 0)) for k in ["close", "open", "high", "low", "volume"]},
                "indicators": {k: float(market_data.get(k, 0)) for k in ["RSI", "SMA_20", "SMA_50", "MACD", "MACD_SIGNAL", "MACD_HIST", "price_change_24h"]},
            }
        else:
            formatted_data = {
                symbol: {
                    "price_data": {k: float(data.get(k, 0)) for k in ["close", "open", "high", "low", "volume"]},
                    "indicators": {k: float(data.get(k, 0)) for k in ["RSI", "SMA_20", "SMA_50", "MACD", "MACD_SIGNAL", "MACD_HIST", "price_change_24h"]},
                }
                for symbol, data in market_data.items()
            }

        prompt = f"""
{self.system_message.content}

Use the following consensus summary to refine your final trading plan.
{consensus_section}

Current Market Data:
{json.dumps(formatted_data, indent=2)}

Provide the final consensus-driven trading plan now.
"""
        return self.get_response(prompt)


class RiskAdvisorAgent(BaseAgent):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.system_message = SystemMessage(content="""You are a risk management expert...""")


class GraphAnalystAgent(BaseAgent):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.system_message = SystemMessage(content="""You are a technical analysis expert...""")


class FinancialAdvisorAgent(BaseAgent):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.system_message = SystemMessage(content="""You are a financial advisor specializing in crypto...""")


class SentimentAnalysisAgent(BaseAgent):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.system_message = SystemMessage(content="""You are a sentiment analysis expert...""")


class MacroEconomicAgent(BaseAgent):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.system_message = SystemMessage(content="""You are a macroeconomic analyst...""")


class OnChainAnalysisAgent(BaseAgent):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.system_message = SystemMessage(content="""You are an on-chain analysis expert...""")


class LiquidityAnalysisAgent(BaseAgent):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.system_message = SystemMessage(content="""You are a liquidity analyst...""")


class CorrelationAnalysisAgent(BaseAgent):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.system_message = SystemMessage(content="""You are a correlation analysis expert...""")


class ConsensusAdvisorAgent(BaseAgent):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.system_message = SystemMessage(content="""You are a market synthesizer...""")

    def get_consensus(self, analyses: dict) -> str:
        """
        Generate a consensus view from multiple analyses.
        """
        ordered_keys = [
            "Trader's Analysis", "Risk Assessment", "Technical Analysis", "Financial Analysis",
            "Market Sentiment", "Macro Environment", "On-Chain Metrics",
            "Liquidity Analysis", "Correlation Analysis",
        ]
        for key in analyses.keys():
            if key not in ordered_keys:
                ordered_keys.append(key)

        prompt = "Synthesize the following analyses into a unified trading view:\n\n"
        for key in ordered_keys:
            if key in analyses:
                prompt += f"=== {key.upper()} ===\n{analyses[key]}\n\n"

        return self.get_response(prompt)


# ============================
# Orchestrator
# ============================

class MarketOrchestrator:
    """
    Runs multiple agents, gathers their outputs,
    and produces a consensus-driven final trading plan.
    """

    def __init__(self, api_key: str):
        self.trader = TraderAgent(api_key)
        self.risk = RiskAdvisorAgent(api_key)
        self.graph = GraphAnalystAgent(api_key)
        self.financial = FinancialAdvisorAgent(api_key)
        self.sentiment = SentimentAnalysisAgent(api_key)
        self.macro = MacroEconomicAgent(api_key)
        self.onchain = OnChainAnalysisAgent(api_key)
        self.liquidity = LiquidityAnalysisAgent(api_key)
        self.correlation = CorrelationAnalysisAgent(api_key)
        self.consensus = ConsensusAdvisorAgent(api_key)

    def run_all(self, market_data: dict, multi_pair: bool = False) -> str:
        """
        Runs all agents and returns the final consensus trading plan.
        """
        analyses = {
            "Trader's Analysis": self.trader.get_response(json.dumps(market_data)),
            "Risk Assessment": self.risk.get_response(json.dumps(market_data)),
            "Technical Analysis": self.graph.get_response(json.dumps(market_data)),
            "Financial Analysis": self.financial.get_response(json.dumps(market_data)),
            "Market Sentiment": self.sentiment.get_response(json.dumps(market_data)),
            "Macro Environment": self.macro.get_response(json.dumps(market_data)),
            "On-Chain Metrics": self.onchain.get_response(json.dumps(market_data)),
            "Liquidity Analysis": self.liquidity.get_response(json.dumps(market_data)),
            "Correlation Analysis": self.correlation.get_response(json.dumps(market_data)),
        }

        # Get consensus summary
        consensus_summary = self.consensus.get_consensus(analyses)

        # Get final trading plan from TraderAgent
        return self.trader.get_trade_from_consensus(consensus_summary, market_data, multi_pair=multi_pair)
