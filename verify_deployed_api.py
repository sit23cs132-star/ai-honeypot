"""Quick verification script for the deployed API on Render."""
import requests
import json

# Your deployed URL
DEPLOYED_URL = "https://ai-honeypot-api-eluy.onrender.com/api/analyze"
API_KEY = "honeypot-secure-key-2026"

# Hackathon format request
hackathon_request = {
    "sessionId": "1fc994e9-f4c5-47ee-8806-90aeb969928f",
    "message": {
        "sender": "scammer",
        "text": "Your bank account will be blocked today. Verify immediately.",
        "timestamp": 1769776085000
    },
    "conversationHistory": [],
    "metadata": {
        "channel": "SMS",
        "language": "English",
        "locale": "IN"
    }
}

print("=" * 70)
print("VERIFYING DEPLOYED API ON RENDER")
print("=" * 70)
print(f"URL: {DEPLOYED_URL}")
print(f"Testing with hackathon evaluation format...\n")

try:
    response = requests.post(
        DEPLOYED_URL,
        json=hackathon_request,
        headers={
            "X-API-Key": API_KEY,
            "Content-Type": "application/json"
        },
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        response_data = response.json()
        print(f"\nResponse:")
        print(json.dumps(response_data, indent=2))
        
        # Check if format is correct
        if "status" in response_data and "reply" in response_data:
            print("\n" + "=" * 70)
            print("✅ SUCCESS! API IS READY FOR HACKATHON EVALUATION")
            print("=" * 70)
            print(f"✅ Correct format: {{'status': '{response_data['status']}', 'reply': '...'}}")
            print(f"✅ Status: {response_data['status']}")
            print(f"✅ Reply: {response_data['reply'][:50]}...")
            print("\n🎉 Your API is now compatible with the hackathon evaluator!")
        else:
            print("\n❌ ISSUE: Response format missing 'status' or 'reply' fields")
            print("Please wait a few minutes for Render to complete deployment.")
    else:
        print(f"\n❌ ERROR: HTTP {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.Timeout:
    print("\n⏱️  TIMEOUT: Request took too long")
    print("Note: Render free tier may take 50+ seconds for first request after idle")
    print("Please try again in a moment.")
    
except requests.exceptions.RequestException as e:
    print(f"\n❌ REQUEST ERROR: {e}")
    print("Check that the deployed URL is correct and accessible.")

print("\n" + "=" * 70)
