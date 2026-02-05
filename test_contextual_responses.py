"""Test improved contextual responses locally."""
import requests
import json

BASE_URL = "http://localhost:8000"
API_KEY = "honeypot-secure-key-2026"

# Test cases matching the hackathon evaluation
test_scenarios = [
    {
        "name": "Banking Phishing - First Message",
        "message": "URGENT: Your SBI account has been compromised. Your account will be blocked in 2 hours. Share your account number and OTP immediately to verify your identity.",
        "expected_keywords": ["bank", "account", "what", "which", "otp", "worried", "serious"]
    },
    {
        "name": "Banking Phishing - OTP Request",
        "message": "Please send me your 16‑digit account number and the OTP you just received via SMS so we can secure your account immediately",
        "expected_keywords": ["otp", "account", "bank", "which", "what", "number", "code"]
    },
    {
        "name": "Urgent Time Pressure",
        "message": "Your account will be locked in 30 minutes unless you send your account details right now.",
        "expected_keywords": ["urgent", "what", "do", "need", "how", "serious", "steps"]
    }
]

print("="*80)
print("TESTING IMPROVED CONTEXTUAL RESPONSES")
print("="*80)

for i, scenario in enumerate(test_scenarios, 1):
    print(f"\n[Test {i}] {scenario['name']}")
    print(f"{'='*80}")
    print(f"Scammer Message:\n  \"{scenario['message'][:80]}...\"")
    
    # Create hackathon format request
    request_data = {
        "sessionId": f"test-context-{i}",
        "message": {
            "sender": "scammer",
            "text": scenario['message'],
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
            f"{BASE_URL}/api/analyze",
            json=request_data,
            headers={
                "X-API-Key": API_KEY,
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            reply = data.get("reply", "")
            print(f"\nHoneypot Response:\n  \"{reply}\"")
            
            # Check if response is contextual
            reply_lower = reply.lower()
            found_keywords = [kw for kw in scenario['expected_keywords'] if kw in reply_lower]
            
            if found_keywords:
                print(f"\n✅ CONTEXTUAL: Found keywords {found_keywords}")
            else:
                print(f"\n⚠️  GENERIC: Expected keywords like {scenario['expected_keywords'][:3]}")
                
            # Check if it's old generic response
            generic_responses = [
                "hello! how can i help you?",
                "hi there! what's this about?",
                "hello! i'm here. what do you need?",
                "hi! yes, i'm available. what's going on?"
            ]
            
            if reply_lower.strip('?!. ') in [g.strip('?!. ') for g in generic_responses]:
                print(f"⚠️  WARNING: Still using old generic response!")
        else:
            print(f"\n❌ Error: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("")

print("="*80)
print("TEST COMPLETE")
print("="*80)
print("\n💡 Good responses should:")
print("  1. Acknowledge the scam context (bank, OTP, urgency)")
print("  2. Ask clarifying questions")
print("  3. Show concern or interest")
print("  4. NOT be generic greetings")
