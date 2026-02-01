from google import genai
from google.genai import types
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

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

def analyze_filing(ticker: str, form_type: str, text_content: str) -> str:
    """
    Analyze the text of a filing using Gemini 3 (or latest available).
    Returns a markdown summary/analysis.
    """
    if not client:
        return "Error: GOOGLE_API_KEY not configured. Please check backend/.env"

    if not text_content:
        return "Error: No content to analyze."

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
        return response.text
    except Exception as e:
        # Fallback to flash if pro fails or unavailable
        try:
             response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
             return response.text
        except Exception as e2:
            logger.error(f"Gemini analysis failed: {e2}")
            return f"Analysis failed: {str(e2)}"

def summarize_company_history(ticker: str, filings_data: list) -> str:
    """
    Synthesize a history view from a list of filing summaries.
    This is a placeholder for a more complex RAG approach, here we just ask Gemini
    to summarize based on available metadata or snippets.
    """
    # For a hackathon, we might just analyze the most recent 10-K specifically for "History"
    return "Historical analysis requires processing multiple documents. (Implemented as single doc analysis for now)"
