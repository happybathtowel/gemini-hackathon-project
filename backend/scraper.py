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

def get_recent_filings(ticker: str, filing_type: str = ""):
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
            
            # Limit to recent 10 for now to avoid overload
            if len(results) >= 10:
                break
                
        return results
        
    except Exception as e:
        logger.error(f"Error fetching filings for {ticker}: {e}")
        return []

def get_filing_text(url: str) -> str:
    """
    Fetch and parse the text content of a filing URL.
    """
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml') # using lxml for speed
        
        # Remove scripts and styles
        for script in soup(["script", "style"]):
            script.decompose()
            
        text = soup.get_text(separator="\n", strip=True)
        return text[:100000] # Limit to 100k chars for API limits (rough safety)
        
    except Exception as e:
        logger.error(f"Error fetching text from {url}: {e}")
        return ""
