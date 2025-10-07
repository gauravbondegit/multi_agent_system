# test_api.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

print("Attempting to test Google API Key...")

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ ERROR: GOOGLE_API_KEY not found in .env file.")
else:
    try:
        
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel('gemini-2.5-flash')

        print("✅ Key configured successfully. Sending test prompt to Gemini...")

        # Send a simple prompt
        response = model.generate_content("Why is the sky blue?")

        print("✅ Success! API responded.")
        print("Response:", response.text)

    except Exception as e:
        print(f"❌ ERROR: An error occurred while testing the API key.")
        print(f"Error Details: {e}")
