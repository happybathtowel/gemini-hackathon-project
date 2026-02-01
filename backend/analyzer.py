from google import genai
from google.genai import types
import os
import logging
import hashlib
import json
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Cache setup
CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# Initialize client
api_key = os.getenv("GOOGLE_API_KEY")
client = None
if not api_key:
    logger.warning("GOOGLE_API_KEY not found in environment variables. Analysis will fail.")
else:
    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        logger.error(f"Failed to initialize Gemini client: {e}")

def get_cache_path(key: str) -> str:
    hash_key = hashlib.md5(key.encode('utf-8')).hexdigest()
    return os.path.join(CACHE_DIR, f"analysis_{hash_key}.md")

def analyze_filing(ticker: str, form_type: str, text_content: str) -> str:
    """
    Analyze the text of a filing using Gemini 3 (or latest available).
    Returns a markdown summary/analysis.
    """
    if not client:
        return "Error: GOOGLE_API_KEY not configured. Please check backend/.env"

    if not text_content:
        return "Error: No content to analyze."

    # Check cache
    # Key includes ticker, form, and content (to be safe if content changes, though unlikely for same URL)
    # Using content hash is safer but slower if content is huge. 
    # Let's use a hash of the content prefix + ticker + form as a proxy or just hash the content.
    # To avoid huge hash overhead on every call if not needed, we can just hash the text.
    cache_key = f"{ticker}_{form_type}_{text_content[:1000]}" # Simple key
    # Better: Hash the full content. Python's hashlib is fast enough for 100k chars.
    full_cache_key = f"{ticker}_{form_type}_{hashlib.md5(text_content.encode('utf-8')).hexdigest()}"
    cache_path = get_cache_path(full_cache_key)

    if os.path.exists(cache_path):
        logger.info(f"Analysis cache hit for {ticker} {form_type}")
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return f.read()
        except:
            pass

    prompt = f"""
    You are a highly experienced financial analyst. 
    Analyze the following {form_type} filing for {ticker}.
    
    Focus on:
    1. Key "Actionable Market Information" - anything that would move the stock price.
    2. Significant risks or legal proceedings.
    3. Financial health updates (if 10-K/10-Q).
    4. Executive leadership changes.
    
    Be concise but thorough. Use bullet points.
    
    Filing Content (truncated):
    {text_content[:50000]} 
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-3-flash-preview',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2
            )
        )
        result = response.text
        
        # Save to cache
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(result)
            
        return result
    except Exception as e:
        logger.error(f"Gemini analysis failed: {e}")
        return f"Analysis failed: {str(e)}"

def analyze_company_comprehensive(ticker: str, filings_list: list) -> str:
    """
    Analyze a collection of filings (10-K, 10-Q, 8-K) to produce a comprehensive report.
    filings_list: list of dicts { 'form': str, 'filingDate': str, 'content': str, 'accessionNumber': str }
    """
    if not client:
        return "Error: GOOGLE_API_KEY not configured."

    if not filings_list:
        return "No filings provided for analysis."

    # Generate cache key based on the list of accession numbers (identifies the exact set of docs)
    # Sort by date usually, but for hash order matters.
    accession_ids = sorted([f.get('accessionNumber', '') for f in filings_list])
    cache_key = f"comprehensive_{ticker}_{hashlib.md5(json.dumps(accession_ids).encode('utf-8')).hexdigest()}"
    cache_path = get_cache_path(cache_key)

    if os.path.exists(cache_path):
        logger.info(f"Comprehensive analysis cache hit for {ticker}")
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return f.read()
        except:
            pass

    # Construct Prompt
    # We will feed summaries or truncated text of multiple documents.
    # Given context limits, we should be careful. 
    # Strategy: 
    # 1. Identify which is the 10-K (Foundation)
    # 2. Identify subsequent 8-Ks/10-Qs (Updates)
    
    combined_text = f"Comprehensive Analysis Context for {ticker}:\n\n"
    
    for filing in filings_list:
        form = filing['form']
        date = filing['filingDate']
        content = filing.get('content', '')[:20000] # Cap per filing to fit context
        
        combined_text += f"---\nDOCUMENT: {form} (Filed: {date})\nCONTENT:\n{content}\n---\n\n"

    prompt = f"""
    You are a Chief Investment Officer preparing a comprehensive research report on {ticker}.
    
    You have access to the most recent 10-K/10-Q and subsequent 8-K filings below.
    
    Your goal is to synthesize this information into a single, cohesive "State of the Company" report.
    
    Structure your report as follows:
    # {ticker} Comprehensive Analysis
    
    ## 1. Executive Summary
    High-level outlook based on the latest annual/quarterly data and recent events.
    
    ## 2. Core Financial Review (Latest 10-K/10-Q)
    Key metrics, growth trajectory, and balance sheet health.
    
    ## 3. Recent Developments (8-Ks)
    Synthesize the recent 8-Ks. Do not just list them. Explain the *narrative* of what has happened since the last major report. 
    - Leadership changes?
    - Material agreements?
    - Earnings releases?
    
    ## 4. Risk Assessment
    Combine long-term risks (10-K) with any new risks unveiled in recent filings.
    
    ## 5. Investment Verdict
    Bull/Bear case summary based on the totality of data.
    
    DATA:
    {combined_text}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-3-flash-preview', 
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3
            )
        )
        result = response.text
        
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(result)
            
        return result
    except Exception as e:
        logger.error(f"Comprehensive analysis failed: {e}")
        return f"Comprehensive analysis failed: {str(e)}"

