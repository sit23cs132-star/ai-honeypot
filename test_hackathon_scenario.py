"""Test with hackathon's exact test scenario - varied message types."""
import requests
import json
import time

DEPLOYED_URL = "https://ai-honeypot-api-eluy.onrender.com/api/analyze"
API_KEY = "honeypot-secure-key-2026"

# Exact messages from the hackathon test result
test_messages = [
    "URGENT: Your SBI account has been compromised. Your account will be blocked in 2 hours. Share your account number and OTP immediately to verify your identity.",
    "Send me the OTP right now, otherwise your account will be locked within minutes.",
    "Your account number is 1234567890123456. Please send the OTP you just received right now to verify and avoid the account being blocked.",
    "Your account shows a high-value transfer attempt; to stop it you must send the OTP and your UPI PIN to scammer.fraud@fakebank right now.",
    "Your account shows a high-value transfer of Rs.10,000 to an unknown beneficiary; to stop it, reply with the OTP and your UPI PIN to scammer.fraud@fakebank immediately.",
    "A suspicious Rs.10,000 transfer is pending; please reply with the OTP and your UPI PIN to scammer.fraud@fakebank within 5 minutes to prevent your account from being blocked.",
    "A transaction of Rs.10,000 (ID: 987654321) is pending on account 1234567890123456; reply with the OTP and your UPI PIN to scammer.fraud@fakebank within 3 minutes to stop it.",
    "A Rs.10,000 transfer to an unknown beneficiary is pending on account 1234567890123456; reply with the OTP and your UPI PIN to scammer.fraud@fakebank within 2 minutes to stop it.",
    "The Rs.10,000 transfer (ID: 987654321) on account 1234567890123456 will be cancelled unless you email the OTP and your UPI PIN to scammer.fraud@fakebank within the next minute.",
    "The Rs.10,000 transfer (ID:987654321) on account 1234567890123456 will be processed in 1 minute; send the OTP and your UPI PIN to scammer.fraud@fakebank now to cancel it."
]

print("="*80)
print("HACKATHON TEST SCENARIO - Exact Message Sequence")
print("="*80)

responses = []

for turn, message in enumerate(test_messages, 1):
    print(f"\nTurn {turn}: {message[:60]}...")
    
    request_data = {
        "sessionId": f"hackathon-test-{int(time.time())}",
        "message": {
            "sender": "scammer",
            "text": message,
            "timestamp": int(time.time() * 1000)
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
            DEPLOYED_URL,
            json=request_data,
            headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            reply = data.get("reply", "")
            responses.append(reply)
            print(f"Honeypot: {reply}")
        else:
            print(f"❌ HTTP {response.status_code}")
            responses.append("[ERROR]")
            
        time.sleep(0.3)
        
    except Exception as e:
        print(f"❌ Error: {str(e)[:100]}")
        responses.append("[ERROR]")

print(f"\n{'='*80}")
print("ANALYSIS")
print(f"{'='*80}")

# Check for the bad pattern
bad_pattern = "I'm listening. Can you give me more details?"
bad_count = sum(1 for r in responses if bad_pattern.lower() in r.lower())

if bad_count == 0:
    print("✅ EXCELLENT: No repetitive generic 'I'm listening...' responses")
else:
    print(f"❌ FAILED: {bad_count}/10 responses were generic 'I'm listening...'")

# Check for contextual responses
contextual_count = 0
for r in responses:
    r_lower = r.lower()
    if any(word in r_lower for word in ['otp', 'code', 'transfer', 'account', 'upi', 'pin', 'email', 'bank']):
        contextual_count += 1

print(f"✅ {contextual_count}/10 responses were contextual (mentioned scam keywords)")

# Check variety
unique = len(set(responses))
print(f"✅ {unique}/10 unique responses (variety score)")

if bad_count == 0 and contextual_count >= 7:
    print(f"\n🎉 SUCCESS! API is ready for hackathon evaluation!")
else:
    print(f"\n⚠️  Some issues remain, but much better than before")
