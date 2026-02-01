from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from contextlib import asynccontextmanager

from scraper import get_recent_filings, get_filing_text
from analyzer import analyze_filing
from monitor import start_monitor, add_ticker_to_monitor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up SEC Scraper Backend...")
    start_monitor()
    yield
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(title="SEC Insight API", lifespan=lifespan)

# CORS (Allow frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev, restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TickerRequest(BaseModel):
    ticker: str

@app.get("/")
def read_root():
    return {"status": "ok", "message": "SEC Scraper API is running"}

@app.post("/api/track")
def track_ticker(request: TickerRequest):
    """
    Start tracking a ticker. Returns recent filings.
    """
    ticker = request.ticker.upper()
    logger.info(f"Received track request for {ticker}")
    
    # Add to background monitor
    add_ticker_to_monitor(ticker)
    
    # Return initial data
    filings = get_recent_filings(ticker)
    return {"ticker": ticker, "recent_filings": filings}

@app.post("/api/analyze")
def analyze_specific_filing(url: str, ticker: str, form: str):
    """
    Trigger on-demand analysis of a specific filing URL.
    """
    logger.info(f"Analyzing {form} for {ticker}...")
    text = get_filing_text(url)
    if not text:
        raise HTTPException(status_code=400, detail="Could not retrieve text from URL")
        
    analysis = analyze_filing(ticker, form, text)
    return {"analysis": analysis}

@app.get("/api/feed")
def get_feed():
    # Placeholder for checking if there are new notifications
    # In a real app, use SSE or Websockets
    return {"updates": []}
