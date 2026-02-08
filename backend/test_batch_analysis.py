from analyzer import analyze_filings_batch
import google.genai
import sys

print(f"GenAI Version: {google.genai.__version__}")

# Mock filings
filings = [
    {
        "form": "4",
        "filingDate": "2023-10-27",
        "accessionNumber": "0001",
        "content": "Statement of changes in beneficial ownership of securities."
    }
]

print("Testing batch analysis...")
result = analyze_filings_batch("AAPL", filings)
print("-" * 20)
print(result)
print("-" * 20)
