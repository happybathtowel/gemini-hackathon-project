import requests
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SEC EDGAR requires a User-Agent in the format: "Sample Company Name AdminContact@<sample company domain>.com"
# or "Individual Name AdminContact@<email>.com"
HEADERS = {
    "User-Agent": "Individual Investor gemini_hackathon@example.com",
    # "Accept-Encoding": "gzip, deflate",
    # "Host": "www.sec.gov"
}

def get_cik(ticker: str) -> str:
    """
    Fetch the CIK (Central Index Key) for a given ticker symbol.
    Uses the SEC's company tickers JSON.
    """
    try:
        url = "https://www.sec.gov/files/company_tickers.json"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        
        ticker = ticker.upper()
        for idx, entry in data.items():
            if entry['ticker'] == ticker:
                # CIK must be 10 digits, padded with leading zeros
                return str(entry['cik_str']).zfill(10)
        logger.error(f"Ticker {ticker} not found.")
        return None
    except Exception as e:
        logger.error(f"Error fetching CIK for {ticker}: {e}")
        return None

def get_recent_filings(ticker: str, filing_type: str = "", limit: int = 10):
    """
    Fetch recent filings for a ticker.
    filing_type can be "10-K", "8-K", etc.
    """
    cik = get_cik(ticker)
    if not cik:
        return []

    # SEC Submissions API
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        
        filings = data.get("filings", {}).get("recent", {})
        if not filings:
            return []
            
        # Parse into a list of dicts
        results = []
        count = len(filings["accessionNumber"])
        
        for i in range(count):
            form = filings["form"][i]
            if filing_type and form != filing_type:
                continue
                
            accession_number = filings["accessionNumber"][i]
            primary_document = filings["primaryDocument"][i]
            filing_date = filings["filingDate"][i]
            report_date = filings["reportDate"][i]
            
            # Construct the full URL to the document
            # URL format: https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{primaryDocument}
            # Accession number in URL usually has dashes removed
            accession_no_dash = accession_number.replace("-", "")
            doc_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_no_dash}/{primary_document}"
            
            results.append({
                "ticker": ticker,
                "cik": cik,
                "form": form,
                "accessionNumber": accession_number,
                "filingDate": filing_date,
                "reportDate": report_date,
                "url": doc_url
            })
            
            if len(results) >= limit:
                break
                
        return results
        
    except Exception as e:
        logger.error(f"Error fetching filings for {ticker}: {e}")
        return []

import hashlib
import os

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def get_filing_text(url: str) -> str:
    """
    Fetch and parse the text content of a filing URL.
    Caches the result locally to avoid repeated requests.
    """
    # Generate a safe filename from the URL
    url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
    cache_path = os.path.join(CACHE_DIR, f"{url_hash}.txt")

    # Check cache first
    if os.path.exists(cache_path):
        logger.info(f"Cache hit for {url}")
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading cache for {url}: {e}")
            # Fallthrough to fetch if cache read fails

    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml') # using lxml for speed
        
        # Remove scripts and styles
        for script in soup(["script", "style"]):
            script.decompose()
            
        text = soup.get_text(separator="\n", strip=True)
        text = text[:100000] # Limit to 100k chars
        
        # Save to cache
        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                f.write(text)
        except Exception as e:
            logger.error(f"Error writing to cache for {url}: {e}")
            
        return text
        
    except Exception as e:
        logger.error(f"Error fetching text from {url}: {e}")
        return ""
