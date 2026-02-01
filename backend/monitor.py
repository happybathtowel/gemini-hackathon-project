import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from scraper import get_recent_filings
# from analyzer import analyze_filing # import when ready to integrate fully

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

# In-memory store for latest accession numbers to detect new filings
# Structure: { "AAPL": "0000320193-23-000123" }
latest_accessions = {}
tracked_tickers = set()

async def check_updates():
    """
    Background task to check for new filings.
    """
    logger.info("Checking for SEC updates...")
    for ticker in tracked_tickers:
        try:
            filings = get_recent_filings(ticker)
            if not filings:
                continue
            
            most_recent = filings[0]
            last_known = latest_accessions.get(ticker)
            
            if last_known and most_recent['accessionNumber'] != last_known:
                logger.info(f"NEW FILING DETECTED FOR {ticker}: {most_recent['form']}")
                # Here we would trigger analysis and notification
                # await notify_new_filing(ticker, most_recent)
            
            # Update latest
            latest_accessions[ticker] = most_recent['accessionNumber']
            
        except Exception as e:
            logger.error(f"Error monitoring {ticker}: {e}")

def start_monitor():
    scheduler.add_job(check_updates, 'interval', minutes=10) # 10 mins for safe polling
    scheduler.start()
    logger.info("Background monitor started.")

def add_ticker_to_monitor(ticker: str):
    tracked_tickers.add(ticker)
    # Perform initial fetch to set baseline
    try:
        filings = get_recent_filings(ticker)
        if filings:
            latest_accessions[ticker] = filings[0]['accessionNumber']
            logger.info(f"Started tracking {ticker}. Latest: {filings[0]['accessionNumber']}")
    except Exception as e:
        logger.error(f"Failed to init tracking for {ticker}: {e}")
