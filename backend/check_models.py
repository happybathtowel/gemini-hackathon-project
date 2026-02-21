from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("No API key found")
    exit(1)

client = genai.Client(api_key=api_key)

try:
    # List models
    # The syntax for v2 SDK might be client.models.list()
    # But let's try a simple generation to check specific models if listing is complex
    print("Checking gemini-1.5-flash...")
    try:
        client.models.generate_content(model="gemini-1.5-flash", contents="Hello")
        print("gemini-1.5-flash IS AVAILABLE")
    except Exception as e:
        print(f"gemini-1.5-flash failed: {e}")

    print("\nChecking gemini-2.0-flash-exp...")
    try:
        client.models.generate_content(model="gemini-2.0-flash-exp", contents="Hello")
        print("gemini-2.0-flash-exp IS AVAILABLE")
    except Exception as e:
        print(f"gemini-2.0-flash-exp failed: {e}")

    print("\nChecking gemini-1.5-pro...")
    try:
        client.models.generate_content(model="gemini-1.5-pro", contents="Hello")
        print("gemini-1.5-pro IS AVAILABLE")
    except Exception as e:
        print(f"gemini-1.5-pro failed: {e}")

except Exception as e:
    print(f"General error: {e}")
