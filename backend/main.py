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

class CompanyAnalysisRequest(BaseModel):
    ticker: str

@app.post("/api/analyze-company")
def analyze_company(request: CompanyAnalysisRequest):
    """
    Perform a comprehensive analysis of the company based on recent filings.
    """
    ticker = request.ticker.upper()
    logger.info(f"Starting comprehensive analysis for {ticker}")
    
    # 1. Fetch recent filings (enough history to find 10-K)
    filings = get_recent_filings(ticker, limit=100)
    if not filings:
        raise HTTPException(status_code=404, detail="No filings found for ticker")
        
    # 2. Filter logic: Find latest 10-K and all subsequent 8-Ks/10-Qs
    relevant_filings = []
    found_10k_or_10q = False
    
    # Iterate through chronological filings (they are usually sorted desc already)
    # We want the *latest* 10-K or 10-Q as a base, and all 8-Ks since then?
    # Actually, let's grab the latest 10-K (Annual) as the base foundation.
    # And include 10-Qs and 8-Ks filed *after* it.
    
    latest_10k_index = -1
    for i, f in enumerate(filings):
        if f['form'] == '10-K':
            latest_10k_index = i
            break
            
    if latest_10k_index != -1:
        # Everything before the 10-K (index 0 to i) are newer
        # Include the 10-K itself
        candidates = filings[:latest_10k_index+1]
        
        # Filter for 10-K, 10-Q, 8-K only
        for f in candidates:
            if f['form'] in ['10-K', '10-Q', '8-K']:
                relevant_filings.append(f)
    else:
        # No 10-K found in recent list? Fallback to just taking the most recent relevant 5 docs
        logger.warning(f"No 10-K found for {ticker} in recent 100 filings. Using generic recent set.")
        count = 0
        for f in filings:
            if f['form'] in ['10-K', '10-Q', '8-K']:
                relevant_filings.append(f)
                count += 1
            if count >= 5: break
            
    if not relevant_filings:
        raise HTTPException(status_code=404, detail="No relevant filings (10-K/Q/8-K) found.")

    logger.info(f"Selected {len(relevant_filings)} docs for analysis.")
    
    # 3. Retrieve content
    filing_data_list = []
    for f in relevant_filings:
        text = get_filing_text(f['url'])
        if text:
            filing_data_list.append({
                'form': f['form'],
                'filingDate': f['filingDate'],
                'accessionNumber': f['accessionNumber'], # Important for cache key stability
                'content': text
            })
            
    # 4. Analyze
    from analyzer import analyze_company_comprehensive
    report = analyze_company_comprehensive(ticker, filing_data_list)
    



# Redefining Request to include metadata
class FilingMetadata(BaseModel):
    url: str
    form: str
    filingDate: str
    accessionNumber: str

class BatchAnalysisRequest(BaseModel):
    ticker: str
    filings: list[FilingMetadata]

@app.post("/api/analyze-batch")
def analyze_filings_batch_endpoint(request: BatchAnalysisRequest):
    """
    Analyze a batch of filings.
    """
    ticker = request.ticker.upper()
    logger.info(f"Received batch analysis request for {ticker} with {len(request.filings)} filings")
    
    filings_list = []
    for f in request.filings:
        text = get_filing_text(f.url)
        if text:
            filings_list.append({
                'form': f.form,
                'filingDate': f.filingDate,
                'accessionNumber': f.accessionNumber,
                'content': text
            })
            
    if not filings_list:
         raise HTTPException(status_code=400, detail="Could not retrieve text for any filings")
         
    from analyzer import analyze_filings_batch
    report = analyze_filings_batch(ticker, filings_list)
    return {"analysis": report}


@app.get("/api/tracked")
def get_tracked_tickers_endpoint():
    """
    Get list of all currently tracked tickers.
    """
    from monitor import get_tracked_tickers
    return {"tickers": get_tracked_tickers()}

@app.get("/api/feed")
def get_feed():
    # Placeholder for checking if there are new notifications
    # In a real app, use SSE or Websockets
    from monitor import get_recent_filings, get_tracked_tickers
    
    # Simple feed implementation: Get most recent filing for each ticker
    # This is inefficient for production but fine for hackathon
    feed_items = []
    for ticker in get_tracked_tickers():
         filings = get_recent_filings(ticker)
         if filings:
             for f in filings[:3]: # Top 3 per company
                 f['ticker'] = ticker # Add ticker context
                 feed_items.append(f)
    
    # Sort by date desc
    feed_items.sort(key=lambda x: x['filingDate'], reverse=True)
    return {"updates": feed_items[:20]}

@app.get("/api/stock-history")
def get_stock_history(ticker: str, period: str = "1mo"):
    """
    Get stock price history for a ticker.
    """
    import yfinance as yf
    import pandas as pd
    
    logger.info(f"Fetching stock history for {ticker} over {period}")
    
    try:
        ticker = ticker.upper()
        stock = yf.Ticker(ticker)
        # Fetch history
        # period options: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        hist = stock.history(period=period)
        
        if hist.empty:
            logger.warning(f"No stock history found for {ticker}")
            return {"ticker": ticker, "history": []}
            
        # Reset index to get Date as a column
        hist = hist.reset_index()
        
        # Format for frontend: { date: "YYYY-MM-DD", price: float }
        data = []
        for index, row in hist.iterrows():
            # Date might be Timestamp
            date_str = row['Date'].strftime('%Y-%m-%d')
            # Use Close price
            price = round(row['Close'], 2)
            data.append({"date": date_str, "price": price})
            
        return {"ticker": ticker, "history": data}
        
    except Exception as e:
        logger.error(f"Failed to fetch stock history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
