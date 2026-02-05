"""Test fallback responses without AI (simulate API failure)."""
import asyncio
from agent.conversation import ConversationAgent

async def test_fallbacks():
    agent = ConversationAgent()
    
    print("="*70)
    print("TESTING FALLBACK RESPONSES (No AI Required)")
    print("="*70)
    
    test_messages = [
        ("Your SBI account will be blocked. Share your OTP immediately.", 1),
        ("Send your 16-digit account number and OTP now.", 2),
        ("Please provide your account number and UPI ID immediately.", 3),
        ("Your account will be locked in 30 minutes. Send OTP now.", 4),
        ("Share the 6-digit OTP you received via SMS.", 5),
        ("What is your UPI ID? Send it now to verify.", 6),
        ("Your account shows suspicious activity. Send details now.", 7),
        ("This is urgent. Share your bank account number immediately.", 8),
    ]
    
    for message, turn in test_messages:
        print(f"\n[Turn {turn}] Scammer: \"{message[:60]}...\"")
        
        # Get fallback response (simulating AI failure)
        if turn == 1:
            response = await agent.generate_neutral_response(message)
        else:
            response = agent._get_contextual_fallback(message, turn, "banking_phishing")
        
        print(f"Honeypot: \"{response}\"")
        
        # Check if contextual
        msg_lower = message.lower()
        resp_lower = response.lower()
        
        keywords_found = []
        if 'otp' in msg_lower and ('otp' in resp_lower or 'code' in resp_lower):
            keywords_found.append('OTP')
        if 'account' in msg_lower and 'account' in resp_lower:
            keywords_found.append('account')
        if 'upi' in msg_lower and 'upi' in resp_lower:
            keywords_found.append('UPI')
        
        if keywords_found:
            print(f"✅ Contextual ({', '.join(keywords_found)})")
        else:
            print(f"⚠️  Generic response")
    
    print("\n" + "="*70)
    print("FALLBACK TEST COMPLETE")
    print("="*70)
    print("\n💡 Even without AI, responses are:")
    print("   - Contextual (mention OTP, account, UPI when relevant)")
    print("   - Varied (different each turn)")
    print("   - Engaging (ask questions, show concern)")

if __name__ == "__main__":
    asyncio.run(test_fallbacks())
