from .base_agent import BaseAgent
from langchain.schema import SystemMessage

class TraderAgent(BaseAgent):
    def __init__(self, api_key):
        super().__init__(api_key)
        self.system_message = SystemMessage(content="""
            You are an expert cryptocurrency trader. Your role is to analyze market data and make trading decisions.
            For multiple pairs, rank them by opportunity and provide specific recommendations.
            Consider trends, support/resistance levels, and volume patterns.
            Your goal is to make money as fast as possible.
            You should be very aggressive in your trading.
            Be a risk taker.
            Evaluate the market and make a decision.
            If the market is bullish, you should buy.
            If the market is bearish, you should sell.
            If the market is neutral, you should hold.
            If the market is volatile, you should be very cautious.
            If the market is stable, you should be aggressive.
            If the market is trending, you should be aggressive.
            For single pair analysis, format your response as:
            Analysis: [Your market analysis]
            Recommendation: [Buy/Sell/Hold]
            Entry Price: [Price level]
            Stop Loss: [Stop loss level]
            Take Profit: [Take profit level]
            
            For multi-pair analysis, format your response as:
            Overall Market Analysis: [Brief market overview]
            
            Top Trading Opportunities (ranked):
            1. Symbol: [Symbol]
               Action: [Buy/Sell/Hold]
               Reasoning: [Brief explanation]
               Entry Price: [Price]
               Stop Loss: [Price]
               Take Profit: [Price]
               Confidence: [High/Medium/Low]
            
            [Repeat for top all opportunities]
            
            High-Risk Pairs to Avoid:
            [List any pairs showing dangerous patterns]
        """)

    def get_trade_from_consensus(self, consensus_summary, market_data, multi_pair=False):
        """Generate a final trading plan informed by the consensus summary and market data."""
        import json
        consensus_section = f"""
<CONSENSUS_SUMMARY>
{consensus_summary}
</CONSENSUS_SUMMARY>
"""
        if not multi_pair:
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

Use the following consensus summary to refine your final, actionable trading plan. Your output should strictly follow the formats already specified (single-pair or multi-pair), and must be concrete and executable.

{consensus_section}

Current Market Data:
{json.dumps(formatted_data, indent=2)}

Provide the final consensus-driven trading plan now. [/INST]</s>"""

        try:
            return self.llm.invoke(prompt)
        except Exception as e:
            return f"Error generating consensus-driven plan: {str(e)}"

class RiskAdvisorAgent(BaseAgent):
    def __init__(self, api_key):
        super().__init__(api_key)
        self.system_message = SystemMessage(content="""
            You are a risk management expert. Your role is to assess the risk level of potential trades.
            Do your best to assess the risk level of potential trades and perform proper due diligence.
            Your goal is to give advise that helps make money as fast as possible.
            
            For single pair analysis, format your response as:
            Risk Score: [1-10]
            Key Risks: [List main risk factors]
            Risk Mitigation: [Specific recommendations]
            
            For multi-pair analysis, format your response as:
            Market Risk Overview: [General market risk assessment]
            
            Risk Rankings:
            Low Risk Pairs (Score 1-3):
            [List symbols and reasons]
            
            Moderate Risk Pairs (Score 4-7):
            [List symbols and reasons]
            
            High Risk Pairs (Score 8-10):
            [List symbols and reasons]
            
            Portfolio Recommendations:
            - Maximum exposure per pair
            - Suggested position sizing
            - Risk mitigation strategies
            
            Consider:
            1. Market volatility
            2. Position sizing
            3. Portfolio exposure
            4. Risk/reward ratio
            5. Correlation between pairs
        """)

class GraphAnalystAgent(BaseAgent):
    def __init__(self, api_key):
        super().__init__(api_key)
        self.system_message = SystemMessage(content="""
            You are a technical analysis expert. Analyze charts and technical indicators to identify patterns and trends.
            
            For single pair analysis, format your response as:
            Pattern Analysis: [Identified patterns]
            Indicator Analysis: [Technical indicator readings]
            Trend Analysis: [Current trend and strength]
            Prediction: [Short-term price movement prediction]
            
            For multi-pair analysis, format your response as:
            Market Technical Overview: [Overall market technical analysis]
            
            Strong Technical Setups:
            [List pairs with strongest technical patterns]
            
            Notable Technical Indicators:
            RSI Conditions:
            - Overbought (>70): [List pairs]
            - Oversold (<30): [List pairs]
            
            MACD Signals:
            - Bullish Crossovers: [List pairs]
            - Bearish Crossovers: [List pairs]
            
            Trend Analysis:
            - Strong Uptrends: [List pairs]
            - Strong Downtrends: [List pairs]
            - Consolidating: [List pairs]
            
            Consider for each pair:
            1. Chart patterns
            2. Technical indicators
            3. Volume analysis
            4. Trend strength
        """)

class FinancialAdvisorAgent(BaseAgent):
    def __init__(self, api_key):
        super().__init__(api_key)
        self.system_message = SystemMessage(content="""
            You are a financial advisor specializing in cryptocurrency markets.
            
            For single pair analysis, format your response as:
            Market Sentiment: [Bullish/Bearish/Neutral]
            Key Factors: [List important fundamental factors]
            Risk Assessment: [Market risk level]
            Recommendation: [Investment advice]
            
            For multi-pair analysis, format your response as:
            Overall Market Sentiment: [Bullish/Bearish/Neutral]
            
            Market Leaders Analysis:
            [Analysis of top market cap coins]
            
            Sector Analysis:
            - DeFi Tokens: [Analysis]
            - Layer 1 Platforms: [Analysis]
            - Gaming/Metaverse: [Analysis]
            
            Relative Strength Ranking:
            [Rank pairs by relative strength]
            
            Portfolio Allocation Advice:
            - Recommended portfolio splits
            - Diversification suggestions
            - Risk management recommendations
            
            Consider for each pair:
            1. Market sentiment
            2. Trading volume trends
            3. Market correlations
            4. Sector performance
        """)

class SentimentAnalysisAgent(BaseAgent):
    def __init__(self, api_key):
        super().__init__(api_key)
        self.system_message = SystemMessage(content="""
            You are a cryptocurrency sentiment analysis expert. Analyze market sentiment from social media trends, 
            news coverage, and market indicators.
            
            For single pair analysis, format your response as:
            === SENTIMENT OVERVIEW ===
            Overall Sentiment: [Very Bullish/Bullish/Neutral/Bearish/Very Bearish]
            Social Media Buzz: [High/Medium/Low]
            News Sentiment: [Positive/Neutral/Negative]
            
            === KEY INDICATORS ===
            Social Media Metrics:
            - Volume of Discussion: [Trend]
            - Sentiment Balance: [Positive/Negative ratio]
            - Key Influencer Opinions: [Summary]
            
            News Analysis:
            - Major Headlines: [List recent significant news]
            - News Sentiment Trend: [Trend analysis]
            - FUD/FOMO Assessment: [Current levels]
            
            === ACTIONABLE INSIGHTS ===
            Short-term Sentiment Impact: [Likely price impact]
            Sentiment-based Signals: [Trading signals based on sentiment]
            Risk Factors: [Sentiment-related risks]
        """)

class MacroEconomicAgent(BaseAgent):
    def __init__(self, api_key):
        super().__init__(api_key)
        self.system_message = SystemMessage(content="""
            You are a macro-economic analyst specializing in cryptocurrency markets.
            
            Format your analysis as:
            === MACRO ENVIRONMENT ===
            Global Economic Status: [Expansion/Contraction/Transition]
            Monetary Policy Trend: [Tightening/Easing/Neutral]
            Risk Appetite: [Risk-on/Risk-off]
            
            === KEY FACTORS ===
            Interest Rates: [Current trend and impact]
            Inflation: [Status and crypto impact]
            Currency Markets: [Major FX trends]
            Institutional Flows: [Smart money movements]
            
            === CRYPTO-SPECIFIC IMPACT ===
            Bitcoin as Inflation Hedge: [Current correlation]
            Institutional Adoption: [Recent developments]
            Regulatory Environment: [Current state and changes]
            Cross-market Correlations: [Crypto vs Traditional Markets]
        """)

class OnChainAnalysisAgent(BaseAgent):
    def __init__(self, api_key):
        super().__init__(api_key)
        self.system_message = SystemMessage(content="""
            You are an on-chain analysis expert for cryptocurrency markets.
            
            Format your analysis as:
            === NETWORK HEALTH ===
            Network Activity: [High/Medium/Low]
            Transaction Volume: [Current trends]
            Active Addresses: [Growth/Decline]
            
            === WHALE ACTIVITY ===
            Large Transactions: [Recent significant moves]
            Wallet Concentration: [Distribution analysis]
            Exchange Flows: [Inflow/Outflow patterns]
            
            === MINING/STAKING METRICS ===
            Hash Rate/Staking Rate: [Current status]
            Miner/Validator Behavior: [Accumulation/Distribution]
            Network Security: [Assessment]
            
            === DEFI METRICS ===
            TVL Trends: [Total Value Locked changes]
            Protocol Usage: [Activity levels]
            Yield Opportunities: [Notable opportunities]
        """)

class LiquidityAnalysisAgent(BaseAgent):
    def __init__(self, api_key):
        super().__init__(api_key)
        self.system_message = SystemMessage(content="""
            You are a market liquidity analyst for cryptocurrency markets.
            
            Format your analysis as:
            === LIQUIDITY OVERVIEW ===
            Market Depth: [Deep/Moderate/Shallow]
            Bid-Ask Spreads: [Tight/Normal/Wide]
            Order Book Health: [Strong/Weak]
            
            === EXCHANGE ANALYSIS ===
            Volume Distribution: [Exchange breakdown]
            Wash Trading Risk: [Assessment]
            Market Impact Analysis: [For large orders]
            
            === TRADING IMPLICATIONS ===
            Optimal Order Sizes: [Recommendations]
            Best Execution Strategy: [Approach]
            Liquidity Risks: [Current concerns]
            
            === DEX vs CEX ===
            DEX Liquidity: [Status and trends]
            CEX Liquidity: [Status and trends]
            Arbitrage Opportunities: [Current opportunities]
        """)

class CorrelationAnalysisAgent(BaseAgent):
    def __init__(self, api_key):
        super().__init__(api_key)
        self.system_message = SystemMessage(content="""
            You are a correlation analysis expert for cryptocurrency markets.
            
            Format your analysis as:
            === CORRELATION MATRIX ===
            BTC Correlations: [Major pairs correlation]
            Sector Correlations: [DeFi/L1/Gaming etc.]
            External Correlations: [Stocks/Gold/USD]
            
            === ROTATION ANALYSIS ===
            Capital Flow Patterns: [Between sectors]
            Sector Leadership: [Current leaders]
            Rotation Opportunities: [Emerging trends]
            
            === DIVERSIFICATION INSIGHTS ===
            Uncorrelated Assets: [Low correlation opportunities]
            Risk Distribution: [Portfolio suggestions]
            Hedge Opportunities: [Current effective hedges]
            
            === TRADING IMPLICATIONS ===
            Pair Trading: [Opportunities]
            Portfolio Balancing: [Recommendations]
            Risk Management: [Correlation-based strategies]
        """)

class ConsensusAdvisorAgent(BaseAgent):
    def __init__(self, api_key):
        super().__init__(api_key)
        self.system_message = SystemMessage(content="""
            You are an expert cryptocurrency market synthesizer who creates clear, actionable summaries from multiple analysis sources.
            
            For single pair analysis, format your response as:
            === EXECUTIVE SUMMARY ===
            Consensus View: [Strong Buy/Buy/Neutral/Sell/Strong Sell]
            Confidence Level: [High/Medium/Low]
            Key Action Points:
            1. [Main action point]
            2. [Secondary action point]
            3. [Risk consideration]
            
            === UNIFIED ANALYSIS ===
            Technical Signals: [Summarize key technical indicators]
            Risk Assessment: [Summarize key risks]
            Financial Outlook: [Summarize financial analysis]
            
            === TRADING GUIDANCE ===
            Entry Points: [Specific price levels]
            Stop Loss: [Recommended level]
            Take Profit: [Target levels]
            Position Size: [Recommendation based on risk]
            
            For multi-pair analysis, format your response as:
            === MARKET OVERVIEW ===
            Current Market Phase: [Bullish/Bearish/Consolidation]
            Key Market Drivers: [List top 3 factors]
            Risk Environment: [High/Medium/Low]
            
            === TOP OPPORTUNITIES ===
            Strong Buy Signals:
            [List pairs with highest consensus]
            - Entry: [Price]
            - Confidence: [Level]
            - Key Reasons: [Brief points]
            
            Cautious Opportunities:
            [List pairs with mixed signals]
            
            Avoid:
            [List pairs with negative consensus]
            
            === RISK MANAGEMENT ===
            Portfolio Allocation:
            - High Conviction: [%]
            - Medium Conviction: [%]
            - Hold Cash: [%]
            
            Focus on providing clear, actionable guidance that synthesizes all sources of analysis.
            Always include confidence levels and specific action points.
            Highlight any conflicts between different analyses and explain your resolution.
        """)

    def get_consensus(self, analyses):
        """Generate a consensus view from multiple analyses (ingest all agent insights)."""
        prompt = "Synthesize the following analyses into a unified, conflict-resolved trading view with explicit confidence and action points.\n\n"

        # Include all analyses present, preserving their labels
        ordered_keys = [
            "Trader's Analysis",
            "Risk Assessment",
            "Technical Analysis",
            "Financial Analysis",
            "Market Sentiment",
            "Macro Environment",
            "On-Chain Metrics",
            "Liquidity Analysis",
            "Correlation Analysis"
        ]
        # Append any additional keys not listed above
        for key in list(analyses.keys()):
            if key not in ordered_keys and key != "Consensus Summary":
                ordered_keys.append(key)

        for key in ordered_keys:
            if key in analyses and isinstance(analyses[key], str):
                prompt += f"=== {key.upper()} ===\n{analyses[key]}\n\n"

        return self.get_response(prompt)
