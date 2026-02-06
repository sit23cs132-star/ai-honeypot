"""Test the full conversation flow with history to simulate hackathon evaluation."""
import asyncio
from agent.conversation import ConversationAgent
from agent.detector import ScamDetector

async def test_with_history():
    """Test with conversation history like the hackathon eval does."""
    agent = ConversationAgent()
    detector = ScamDetector()
    
    # Simulate the exact test from user
    messages = [
        "URGENT: Your SBI account has been compromised. Your account will be blocked in 2 hours. Share your account number and OTP immediately to verify your identity.",
        "Send me the complete 6‑digit OTP right now, and also provide your UPI PIN to verify and unblock your account immediately.",
        "Send me the 6‑digit OTP and your UPI PIN right now, and confirm your account number 1234567890123456 so we can unblock your account immediately.",
        "Send the 6‑digit OTP and your UPI PIN immediately to +91-9876543210 or email scammer.fraud@fakebank, otherwise your account will be blocked.",
        "Send the 6‑digit OTP and your UPI PIN immediately to +91-9876543210; otherwise your account will be locked within minutes."
    ]
    
    print("="*80)
    print("TESTING WITH CONVERSATION HISTORY (Simulating Hackathon Eval)")
    print("="*80)
    
    conversation_history = []
    responses = []
    
    for turn, message in enumerate(messages, 1):
        print(f"\n{'='*80}")
        print(f"TURN {turn}")
        print(f"{'='*80}")
        print(f"Scammer: {message[:70]}...")
        
        # Detect scam (like the API does)
        detection = await detector.detect_scam(message, conversation_history)
        print(f"Scam detected: {detection.is_scam} (confidence: {detection.confidence:.2f})")
        
        if turn == 1 or not detection.is_scam:
            # First turn or not detected - use neutral response
            response = await agent.generate_neutral_response(message)
            print(f"Path: generate_neutral_response()")
        else:
            # Subsequent turns with scam detected - use full response generation
            agent_response = await agent.generate_response(
                message=message,
                conversation_history=conversation_history,
                turn_count=turn,
                scam_type=detection.scam_type,
                strategy="extract"
            )
            response = agent_response["response"]
            print(f"Path: generate_response() -> fallback")
        
        print(f"Honeypot: {response}")
        responses.append(response)
        
        # Update history
        conversation_history.append({"role": "scammer", "message": message})
        conversation_history.append({"role": "agent", "message": response})
    
    print(f"\n{'='*80}")
    print("ANALYSIS")
    print(f"{'='*80}")
    
    # Check for repetition
    unique = len(set(responses))
    print(f"Unique responses: {unique}/{len(responses)}")
    
    # Check for OTP mentions
    otp_count = sum(1 for r in responses if any(w in r.lower() for w in ['otp', 'code', 'digit', 'number']))
    print(f"OTP-related responses: {otp_count}/{len(responses)}")
    
    # Check for generic response
    generic = "I'm a bit confused but willing to help. Guide me?"
    generic_count = sum(1 for r in responses if r == generic)
    if generic_count > 0:
        print(f"❌ FAILED: Generic response appeared {generic_count} times")
    else:
        print(f"✅ SUCCESS: No generic repetition!")
    
    print(f"\nAll responses:")
    for i, r in enumerate(responses, 1):
        print(f"{i}. {r}")

if __name__ == "__main__":
    asyncio.run(test_with_history())
