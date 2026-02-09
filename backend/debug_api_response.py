import requests
import json

def check_api():
    url = "http://localhost:8000/api/track"
    payload = {"ticker": "AAPL"}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        
        print(f"Ticker in response root: {data.get('ticker')}")
        filings = data.get('recent_filings', [])
        print(f"Number of filings: {len(filings)}")
        
        if filings:
            first_filing = filings[0]
            print("First filing keys:", first_filing.keys())
            print("First filing ticker:", first_filing.get('ticker'))
            print("First filing sample:", json.dumps(first_filing, indent=2))
        else:
            print("No filings returned.")
            
    except Exception as e:
        print(f"API call failed: {e}")

if __name__ == "__main__":
    check_api()
