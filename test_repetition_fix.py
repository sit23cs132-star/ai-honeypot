"""Test to verify the repetition fix works correctly."""
import asyncio
from agent.conversation import ConversationAgent

async def test_repeated_messages():
    """Test that we get varied contextual responses, not repetition."""
    agent = ConversationAgent()
    
    # Simulate the exact scenario from user's test
    test_messages = [
        "URGENT: Your SBI account has been compromised. Share your account number and OTP immediately.",
        "Exactly, that's the OTP—send it right away along with your account number 1234567890123456.",
        "Send the OTP you just received together with your account number 1234567890123456 and your UPI PIN.",
        "Send the OTP you just received plus your UPI PIN for scammer.fraud@fakebank immediately.",
        "Send the OTP you just received along with your UPI PIN for scammer.fraud@fakebank immediately.",
        "Send the OTP you just received and your UPI PIN for scammer.fraud@fakebank immediately.",
        "You must send the OTP and your UPI PIN to scammer.fraud@fakebank right now.",
        "Please send the OTP you just received along with your UPI PIN to scammer.fraud@fakebank.",
        "Send the OTP and your UPI PIN to scammer.fraud@fakebank immediately.",
        "Send the OTP and your UPI PIN to scammer.fraud@fakebank immediately."
    ]
    
    print("="*80)
    print("TESTING REPETITION FIX")
    print("="*80)
    
    responses = []
    
    for i, message in enumerate(test_messages, 1):
        print(f"\nTurn {i}:")
        print(f"Scammer: {message[:60]}...")
        
        # Use generate_neutral_response (no conversation history case)
        response = await agent.generate_neutral_response(message)
        responses.append(response)
        
        print(f"Honeypot: {response}")
    
    print(f"\n{'='*80}")
    print("ANALYSIS")
    print(f"{'='*80}")
    
    # Check for the problematic repetitive response
    bad_response = "Tell me exactly what I should do. I don't want any problems!"
    bad_count = sum(1 for r in responses if r == bad_response)
    
    if bad_count > 0:
        print(f"❌ FAILED: '{bad_response}' appeared {bad_count} times")
    else:
        print(f"✅ SUCCESS: No repetitive generic responses!")
    
    # Check for contextual keywords in responses
    contextual_keywords = ['otp', 'code', 'upi', 'pin', 'account', 'bank', 'transfer', 'email']
    contextual_count = 0
    for r in responses:
        r_lower = r.lower()
        if any(kw in r_lower for kw in contextual_keywords):
            contextual_count += 1
    
    print(f"✅ {contextual_count}/10 responses were contextual (mentioned keywords)")
    
    # Check unique responses
    unique_count = len(set(responses))
    print(f"✅ {unique_count}/10 unique responses (variety)")
    
    # Show unique responses
    print(f"\nUnique responses:")
    for i, resp in enumerate(set(responses), 1):
        print(f"{i}. \"{resp}\"")
    
    if bad_count == 0 and contextual_count >= 8 and unique_count >= 3:
        print(f"\n🎉 EXCELLENT! Ready for deployment!")
        return True
    else:
        print(f"\n⚠️  Needs improvement")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_repeated_messages())
    exit(0 if result else 1)
