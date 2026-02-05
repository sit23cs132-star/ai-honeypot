"""Test script to verify the hackathon format compatibility."""
import requests
import json

# Test with local server first
BASE_URL = "http://localhost:8000"
# Uncomment to test against deployed server
# BASE_URL = "https://ai-honeypot-api-eluy.onrender.com"

API_KEY = "honeypot-secure-key-2026"

# Test 1: Hackathon format (as sent by evaluation system)
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

# Test 2: Standard format (backward compatibility)
standard_request = {
    "conversation_id": "test-123",
    "message": "Your bank account will be blocked today. Verify immediately.",
    "conversation_history": []
}

def test_endpoint(url, payload, test_name):
    """Test the API endpoint with given payload."""
    print(f"\n{'='*60}")
    print(f"Test: {test_name}")
    print(f"{'='*60}")
    print(f"Request URL: {url}")
    print(f"Request Payload:\n{json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers={
                "X-API-Key": API_KEY,
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"Response Body:\n{json.dumps(response_data, indent=2)}")
            
            # Validate hackathon format
            if "sessionId" in payload:
                if "status" in response_data and "reply" in response_data:
                    print(f"\n✅ SUCCESS: Response matches expected hackathon format!")
                    print(f"   - status: {response_data.get('status')}")
                    print(f"   - reply: {response_data.get('reply')}")
                else:
                    print(f"\n❌ FAILED: Response missing 'status' or 'reply' fields")
                    print(f"   Expected: {{'status': 'success', 'reply': '...'}}")
                    print(f"   Got: {list(response_data.keys())}")
            else:
                # Standard format should have detailed response
                if "response" in response_data:
                    print(f"\n✅ SUCCESS: Standard format works correctly")
                else:
                    print(f"\n❌ FAILED: Standard format missing 'response' field")
                    
        except json.JSONDecodeError as e:
            print(f"Response Body (raw): {response.text}")
            print(f"\n❌ FAILED: Response is not valid JSON: {e}")
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ FAILED: Request error: {e}")

if __name__ == "__main__":
    print("Testing Hackathon Format Compatibility")
    print("="*60)
    
    # Test hackathon format
    test_endpoint(
        f"{BASE_URL}/api/analyze",
        hackathon_request,
        "Hackathon Format (as sent by evaluator)"
    )
    
    # Test standard format (backward compatibility)
    test_endpoint(
        f"{BASE_URL}/api/analyze",
        standard_request,
        "Standard Format (backward compatibility)"
    )
    
    print(f"\n{'='*60}")
    print("Testing Complete!")
    print(f"{'='*60}")
