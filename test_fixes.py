"""Quick test for the three failing test cases."""
import requests
import json
import time


def test_case(test_id: str, message: str, expected_result: str):
    """Test a single case."""
    url = "https://ai-honeypot-api-eluy.onrender.com/api/analyze"
    headers = {
        "X-API-Key": "honeypot-secure-key-2026",
        "Content-Type": "application/json"
    }
    
    payload = {
        "conversation_id": test_id,
        "message": message
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        result = response.json()
        
        print(f"\n{'='*80}")
        print(f"Test ID: {test_id}")
        print(f"{'='*80}")
        print(f"Message: {message[:100]}...")
        print(f"\nExpected: {expected_result}")
        print(f"Scam Detected: {result['scam_detected']}")
        print(f"Confidence: {result['confidence_score']:.2f}")
        print(f"Response: {result['response'][:80]}...")
        
        # Show extractions
        intel = result['extracted_intelligence']
        if intel.get('bank_accounts'):
            print(f"💳 Bank Accounts: {intel['bank_accounts']}")
        if intel.get('upi_ids'):
            print(f"💰 UPI IDs: {intel['upi_ids']}")
        if intel.get('phone_numbers'):
            print(f"📞 Phone Numbers: {intel['phone_numbers']}")
        if intel.get('email_addresses'):
            print(f"📧 Emails: {intel['email_addresses']}")
        
        return result
        
    except Exception as e:
        print(f"ERROR: {e}")
        return None


def main():
    print("🧪 Testing Failed Cases After Fixes")
    print("="*80)
    
    # Test 1: Crypto testimonial scam (was not detected)
    print("\n\n1️⃣  CRYPTO TESTIMONIAL SCAM TEST")
    test_case(
        "test-crypto-fix",
        "I made $50,000 in just 2 weeks with this crypto bot! Join now and get 5 free trades. Limited to first 100 members. Don't miss out!",
        "Should detect as scam (was FALSE NEGATIVE)"
    )
    
    time.sleep(1)
    
    # Test 2: Tech support with alphanumeric phone (phone not extracted)
    print("\n\n2️⃣  TECH SUPPORT PHONE EXTRACTION TEST")
    test_case(
        "test-phone-fix",
        "Microsoft Security Alert: Your computer is infected with virus. Call +1-800-555-FAKE immediately for urgent tech support.",
        "Should extract phone: +1-800-555-FAKE"
    )
    
    time.sleep(1)
    
    # Test 3: Multiple data extraction (bank account and phone failed)
    print("\n\n3️⃣  MULTI-DATA EXTRACTION TEST")
    test_case(
        "test-extract-fix",
        "Transfer to account 1234567890123456 or UPI: test@paytm. Call +91-9876543210 or email scam@fraud.com",
        "Should extract: bank account (16 digits), UPI, phone, email"
    )
    
    print("\n\n" + "="*80)
    print("✅ Testing Complete!")
    print("="*80)
    print("\nNote: Changes will take effect after Render redeploys (~5 minutes)")


if __name__ == "__main__":
    main()
