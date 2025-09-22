from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
from trading_system import TradingSystem
import asyncio
from datetime import datetime

app = FastAPI(title="Trading System API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/ui")
async def get_ui():
    return FileResponse("static/index.html")

# Initialize trading system
trading_system = TradingSystem(initial_balance_usd=100.0, auto_buy_btc=True)

# Pydantic models for request/response
class Trade(BaseModel):
    symbol: str
    side: str
    amount: float

class Position(BaseModel):
    amount: float
    avg_price: float

class WalletInfo(BaseModel):
    total_value: float
    current_balance_usd: float
    initial_balance_usd: float
    positions: Dict[str, Position]
    trade_count: int

class MarketData(BaseModel):
    symbol: str
    price: float
    volume_24h: float
    price_change_24h: float
    rsi: float

class AgentAnalysis(BaseModel):
    timestamp: datetime
    trader_analysis: str
    risk_analysis: str
    technical_analysis: str
    financial_analysis: str

# Store recent analyses
recent_analyses: List[AgentAnalysis] = []
max_analyses = 50  # Maximum number of analyses to store

@app.get("/")
async def root():
    return {"message": "Trading System API is running"}

@app.get("/wallet", response_model=WalletInfo)
async def get_wallet_info():
    """Get current wallet information"""
    try:
        wallet_summary = trading_system.get_wallet_summary()
        return wallet_summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market/overview", response_model=List[MarketData])
async def get_market_overview():
    """Get overview of all trading pairs"""
    try:
        overview = trading_system.get_market_overview()
        return overview
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market/data/{symbol}")
async def get_market_data(symbol: str):
    """Get detailed market data for a specific symbol"""
    try:
        data = trading_system.get_market_data(symbol)
        if data is None:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trade")
async def execute_trade(trade: Trade):
    """Execute a trade"""
    try:
        result = trading_system.execute_trade(trade.symbol, trade.side, trade.amount)
        return {"status": "success", "order": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analysis/latest")
async def get_latest_analysis():
    """Get the most recent market analysis"""
    try:
        analysis = trading_system.analyze_market()
        current_time = datetime.now()
        
        agent_analysis = AgentAnalysis(
            timestamp=current_time,
            trader_analysis=analysis["Trader's Analysis"],
            risk_analysis=analysis["Risk Assessment"],
            technical_analysis=analysis["Technical Analysis"],
            financial_analysis=analysis["Financial Analysis"]
        )
        
        # Store the analysis
        recent_analyses.append(agent_analysis)
        if len(recent_analyses) > max_analyses:
            recent_analyses.pop(0)
            
        return agent_analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analysis/history")
async def get_analysis_history():
    """Get historical market analyses"""
    return recent_analyses

@app.get("/trades/history")
async def get_trade_history():
    """Get trading history"""
    try:
        return trading_system.wallet.trade_history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Background task for autonomous trading
async def autonomous_trading():
    while True:
        try:
            analysis = trading_system.analyze_market()
            current_time = datetime.now()
            
            # Store the analysis
            agent_analysis = AgentAnalysis(
                timestamp=current_time,
                trader_analysis=analysis["Trader's Analysis"],
                risk_analysis=analysis["Risk Assessment"],
                technical_analysis=analysis["Technical Analysis"],
                financial_analysis=analysis["Financial Analysis"]
            )
            
            recent_analyses.append(agent_analysis)
            if len(recent_analyses) > max_analyses:
                recent_analyses.pop(0)
                
        except Exception as e:
            print(f"Error in autonomous trading: {e}")
            
        await asyncio.sleep(300)  # 5-minute interval

@app.on_event("startup")
async def startup_event():
    """Start autonomous trading on server startup"""
    asyncio.create_task(autonomous_trading())

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
