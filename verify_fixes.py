"""Verification script to test false positive fixes."""
import requests
import json
from typing import Dict
import time


class FixVerifier:
    """Verify that detection fixes work correctly."""
    
    def __init__(self, base_url: str = "https://ai-honeypot-api-eluy.onrender.com"):
        self.base_url = base_url
        self.api_key = "honeypot-secure-key-2026"
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def test_message(self, test_name: str, message: str, expected_scam: bool) -> Dict:
        """Test a single message and return results."""
        url = f"{self.base_url}/api/analyze"
        
        payload = {
            "conversation_id": f"verify-{test_name.lower().replace(' ', '-')}",
            "message": message
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            # Check if detection matches expectation
            is_correct = result['scam_detected'] == expected_scam
            
            return {
                "test_name": test_name,
                "message": message,
                "expected_scam": expected_scam,
                "actual_scam": result['scam_detected'],
                "confidence": result['confidence_score'],
                "response": result['response'],
                "is_correct": is_correct,
                "extracted": {
                    "upi_ids": result['extracted_intelligence'].get('upi_ids', []),
                    "urls": result['extracted_intelligence'].get('phishing_urls', []),
                    "phones": result['extracted_intelligence'].get('phone_numbers', []),
                    "indicators": result['extracted_intelligence'].get('scam_indicators', [])[:3]
                }
            }
        except Exception as e:
            return {
                "test_name": test_name,
                "message": message,
                "error": str(e),
                "is_correct": False
            }
    
    def print_result(self, result: Dict):
        """Print test result in a readable format."""
        status_icon = "✅" if result.get('is_correct') else "❌"
        
        print(f"\n{status_icon} {result['test_name']}")
        print("=" * 70)
        print(f"Message: \"{result['message'][:80]}...\"" if len(result['message']) > 80 else f"Message: \"{result['message']}\"")
        
        if 'error' in result:
            print(f"❌ ERROR: {result['error']}")
            return
        
        print(f"\nExpected Scam: {result['expected_scam']}")
        print(f"Detected Scam: {result['actual_scam']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Response: \"{result['response'][:100]}...\"" if len(result['response']) > 100 else f"Response: \"{result['response']}\"")
        
        # Show extracted intelligence if any
        extracted = result['extracted']
        if any([extracted['upi_ids'], extracted['urls'], extracted['phones'], extracted['indicators']]):
            print(f"\nExtracted Intelligence:")
            if extracted['upi_ids']:
                print(f"  💰 UPI IDs: {', '.join(extracted['upi_ids'])}")
            if extracted['urls']:
                print(f"  🔗 URLs: {', '.join(extracted['urls'])}")
            if extracted['phones']:
                print(f"  📞 Phones: {', '.join(extracted['phones'])}")
            if extracted['indicators']:
                print(f"  ⚠️  Indicators: {', '.join(extracted['indicators'])}")
        
        print()
    
    def run_verification_suite(self):
        """Run all verification tests."""
        print("=" * 70)
        print("🧪 FALSE POSITIVE FIX VERIFICATION")
        print("=" * 70)
        print("\nTesting AI-first detection logic and reduced pattern matching...")
        
        # Test cases
        test_cases = [
            # FALSE POSITIVE TESTS (should NOT be detected as scams)
            {
                "name": "Normal Coffee Chat",
                "message": "Hey! How are you doing? Want to meet for coffee tomorrow at 5pm? Let me know if you're free.",
                "expected_scam": False
            },
            {
                "name": "Friendly Invitation",
                "message": "Hi! Are you interested in joining us for dinner this weekend? Would love to catch up!",
                "expected_scam": False
            },
            {
                "name": "Work Meeting",
                "message": "Can we meet tomorrow to discuss the project deadline? I think we need to review the documents.",
                "expected_scam": False
            },
            
            # TRUE POSITIVE TESTS (should be detected as scams)
            {
                "name": "UPI Prize Scam",
                "message": "Congratulations! You have won Rs. 50,000 prize money. To claim, please send processing fee of Rs. 500 to 9876543210@paytm. Hurry, offer valid for 24 hours only!",
                "expected_scam": True
            },
            {
                "name": "Banking Fraud",
                "message": "URGENT! Your SBI account has been compromised. Your account will be blocked in 2 hours. Share your account number and OTP immediately to verify your identity.",
                "expected_scam": True
            },
            {
                "name": "Investment Scam",
                "message": "Exclusive investment opportunity! Earn 300% returns in 30 days. Bitcoin trading guaranteed profits. Invest now at crypto-profits.biz",
                "expected_scam": True
            },
            {
                "name": "Tech Support Scam",
                "message": "Microsoft Security Alert: Your computer is infected with virus. Call +1-800-555-FAKE immediately for urgent tech support.",
                "expected_scam": True
            },
        ]
        
        results = []
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}] Testing: {test_case['name']}...")
            
            result = self.test_message(
                test_name=test_case['name'],
                message=test_case['message'],
                expected_scam=test_case['expected_scam']
            )
            
            results.append(result)
            self.print_result(result)
            
            # Add small delay to not overwhelm the API
            if i < len(test_cases):
                time.sleep(1)
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 70)
        
        correct_count = sum(1 for r in results if r.get('is_correct', False))
        total_count = len(results)
        
        false_positive_tests = [r for r in results if not r['expected_scam']]
        false_positive_correct = sum(1 for r in false_positive_tests if r.get('is_correct', False))
        
        true_positive_tests = [r for r in results if r['expected_scam']]
        true_positive_correct = sum(1 for r in true_positive_tests if r.get('is_correct', False))
        
        print(f"\nOverall: {correct_count}/{total_count} tests passed ({correct_count/total_count*100:.1f}%)")
        print(f"False Positive Prevention: {false_positive_correct}/{len(false_positive_tests)} passed")
        print(f"True Positive Detection: {true_positive_correct}/{len(true_positive_tests)} passed")
        
        if correct_count == total_count:
            print("\n🎉 ALL TESTS PASSED! False positive fix is working correctly.")
        elif false_positive_correct == len(false_positive_tests):
            print("\n✅ False positive fix is working! Some scam detection may need tuning.")
        else:
            print(f"\n⚠️  {len(false_positive_tests) - false_positive_correct} false positive(s) still detected.")
            print("The AI model may need additional tuning or the API needs redeployment.")
        
        return results


def main():
    """Main verification entry point."""
    print("\nStarting verification process...")
    print("This will test the deployed API to verify false positive fixes.\n")
    
    verifier = FixVerifier()
    
    try:
        results = verifier.run_verification_suite()
        
        print("\n" + "=" * 70)
        print("Verification complete! Check results above.")
        print("=" * 70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\nVerification interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Verification failed: {e}")


if __name__ == "__main__":
    main()
