import sys
import os
import asyncio
import json

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from analyzer import analyze_filings_batch

# Mock filings data
mock_filings = [
    {
        "form": "4",
        "filingDate": "2025-02-01",
        "accessionNumber": "0001",
        "content": "Reporting Person: COOK TIMOTHY D\nTransaction: Sale of 100,000 shares at $220.00\nNature of Ownership: Direct"
    },
    {
        "form": "4",
        "filingDate": "2025-02-02",
        "accessionNumber": "0002",
        "content": "Reporting Person: MAESTRI LUCA\nTransaction: Sale of 50,000 shares at $221.00\nNature of Ownership: Direct"
    }
]

def test_analysis():
    print("Testing analyze_filings_batch with reasoning field...")
    try:
        # Call the analyzer directly
        result_json_str = analyze_filings_batch("AAPL", mock_filings)
        
        print("\n--- Raw Result ---")
        print(result_json_str)
        
        # Parse JSON
        try:
            # Clean possible markdown code blocks
            clean_json = result_json_str.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
            
            print("\n--- Parsed Data ---")
            print(f"Score: {data.get('confidence_score')}")
            print(f"Summary: {data.get('summary')}")
            print(f"Reasoning: {data.get('reasoning')}")
            
            if 'reasoning' in data and isinstance(data['reasoning'], list) and len(data['reasoning']) > 0:
                print("\nSUCCESS: Reasoning field present and is a list.")
            else:
                print("\nFAILURE: Reasoning field missing or invalid.")
                
        except json.JSONDecodeError as e:
            print(f"\nJSON Parse Error: {e}")
            
    except Exception as e:
        print(f"\nAnalysis Error: {e}")

if __name__ == "__main__":
    test_analysis()
