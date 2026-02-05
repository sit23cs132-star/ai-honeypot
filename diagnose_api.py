"""Diagnostic script to troubleshoot API issues."""
import requests
import json
import time

DEPLOYED_URL = "https://ai-honeypot-api-eluy.onrender.com"
API_KEY = "honeypot-secure-key-2026"

print("=" * 70)
print("API DIAGNOSTIC TOOL")
print("=" * 70)

# Test 1: Health check (no auth required)
print("\n[1] Testing health endpoint (no authentication)...")
print(f"URL: {DEPLOYED_URL}/health")
try:
    response = requests.get(f"{DEPLOYED_URL}/health", timeout=60)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Health check passed: {response.json()}")
    else:
        print(f"❌ Health check failed: {response.text}")
except requests.exceptions.Timeout:
    print("⏱️  TIMEOUT: Request took more than 60 seconds")
    print("💡 Render free tier may be spinning up (takes 50+ seconds after idle)")
    print("💡 Trying again in 10 seconds...")
    time.sleep(10)
    try:
        response = requests.get(f"{DEPLOYED_URL}/health", timeout=60)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Still failed: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: API endpoint with hackathon format
print("\n[2] Testing /api/analyze with hackathon format...")
print(f"URL: {DEPLOYED_URL}/api/analyze")

hackathon_request = {
    "sessionId": "test-502-debug",
    "message": {
        "sender": "scammer",
        "text": "Test message",
        "timestamp": 1769776085000
    },
    "conversationHistory": [],
    "metadata": {
        "channel": "SMS",
        "language": "English",
        "locale": "IN"
    }
}

try:
    response = requests.post(
        f"{DEPLOYED_URL}/api/analyze",
        json=hackathon_request,
        headers={
            "X-API-Key": API_KEY,
            "Content-Type": "application/json"
        },
        timeout=60
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 502:
        print("\n❌ 502 BAD GATEWAY ERROR DETECTED")
        print("\nPossible causes:")
        print("1. Application crashed during startup")
        print("2. Missing or invalid environment variables")
        print("3. Python dependencies not installed correctly")
        print("4. Application code has runtime errors")
        print("5. Render service is having issues")
        
        print("\n📋 TROUBLESHOOTING STEPS:")
        print("1. Check Render logs for error messages")
        print("2. Verify environment variables in Render dashboard:")
        print("   - API_KEY=honeypot-secure-key-2026")
        print("   - OPENAI_API_KEY or ANTHROPIC_API_KEY is set")
        print("   - AI_PROVIDER=openai or anthropic")
        print("3. Check if deployment succeeded in Render")
        print("4. Try manual redeploy from Render dashboard")
        
    elif response.status_code == 200:
        print(f"\n✅ SUCCESS!")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"\n⚠️  Unexpected status code")
        print(f"Response: {response.text[:500]}")
        
except requests.exceptions.Timeout:
    print("⏱️  TIMEOUT: Request took more than 60 seconds")
    print("This suggests the server might be stuck or processing very slowly")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)
print("\n💡 If you see 502 errors:")
print("   1. Go to https://dashboard.render.com/")
print("   2. Click on your 'ai-honeypot-api' service")
print("   3. Check the 'Logs' tab for error messages")
print("   4. Look for Python errors or missing dependencies")
print("=" * 70)
