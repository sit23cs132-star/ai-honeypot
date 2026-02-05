"""Automated test runner for evaluators to test the API comprehensively."""
import requests
import json
import time
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class TestCase:
    """Test case data structure."""
    id: str
    category: str
    message: str
    expected_scam: bool
    expected_confidence_min: float = 0.0
    expected_extractions: Dict = None
    conversation_history: List[Dict] = None
    description: str = ""


class EvaluatorTestRunner:
    """Comprehensive test runner for API evaluation."""
    
    def __init__(self, base_url: str = "https://ai-honeypot-api-eluy.onrender.com"):
        self.base_url = base_url
        self.api_key = "honeypot-secure-key-2026"
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        self.results = []
    
    def run_test(self, test: TestCase) -> Dict:
        """Execute a single test case."""
        url = f"{self.base_url}/api/analyze"
        
        payload = {
            "conversation_id": test.id,
            "message": test.message
        }
        
        if test.conversation_history:
            payload["conversation_history"] = test.conversation_history
        
        try:
            start_time = time.time()
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            elapsed = time.time() - start_time
            
            response.raise_for_status()
            result = response.json()
            
            # Evaluate test outcome
            scam_correct = result['scam_detected'] == test.expected_scam
            confidence_ok = result['confidence_score'] >= test.expected_confidence_min
            
            # Check extractions if specified
            extractions_ok = True
            extraction_details = {}
            if test.expected_extractions:
                intel = result['extracted_intelligence']
                for key, expected_items in test.expected_extractions.items():
                    actual_items = intel.get(key, [])
                    extraction_details[key] = {
                        'expected': expected_items,
                        'actual': actual_items,
                        'found': all(item in actual_items for item in expected_items)
                    }
                    if not extraction_details[key]['found']:
                        extractions_ok = False
            
            passed = scam_correct and confidence_ok and extractions_ok
            
            return {
                'test_id': test.id,
                'category': test.category,
                'description': test.description,
                'message': test.message[:80] + '...' if len(test.message) > 80 else test.message,
                'passed': passed,
                'expected_scam': test.expected_scam,
                'actual_scam': result['scam_detected'],
                'scam_correct': scam_correct,
                'confidence': result['confidence_score'],
                'confidence_ok': confidence_ok,
                'expected_confidence_min': test.expected_confidence_min,
                'response': result['response'][:100],
                'response_time': round(elapsed, 2),
                'extractions_ok': extractions_ok,
                'extraction_details': extraction_details,
                'turn_count': result.get('turn_count', 0),
                'extracted_intelligence': result['extracted_intelligence']
            }
            
        except Exception as e:
            return {
                'test_id': test.id,
                'category': test.category,
                'description': test.description,
                'passed': False,
                'error': str(e)
            }
    
    def print_result(self, result: Dict):
        """Print a single test result."""
        status = "✅ PASS" if result['passed'] else "❌ FAIL"
        print(f"\n{status} | {result['test_id']} | {result['category']}")
        print("─" * 80)
        
        if 'error' in result:
            print(f"❌ ERROR: {result['error']}")
            return
        
        print(f"Description: {result['description']}")
        print(f"Message: \"{result['message']}\"")
        print(f"\n  Expected Scam: {result['expected_scam']} | Actual: {result['actual_scam']} | {'✓' if result['scam_correct'] else '✗'}")
        print(f"  Confidence: {result['confidence']:.2f} (min: {result['expected_confidence_min']}) | {'✓' if result['confidence_ok'] else '✗'}")
        print(f"  Response Time: {result['response_time']}s")
        print(f"  Agent Response: \"{result['response']}...\"")
        
        # Show extraction results if tested
        if result['extraction_details']:
            print(f"\n  Intelligence Extraction:")
            for key, details in result['extraction_details'].items():
                status_icon = '✓' if details['found'] else '✗'
                print(f"    {status_icon} {key}: Expected {details['expected']} | Got {details['actual']}")
        
        # Show all extracted intelligence
        intel = result['extracted_intelligence']
        if any([intel.get('bank_accounts'), intel.get('upi_ids'), intel.get('phishing_urls'),
                intel.get('phone_numbers'), intel.get('email_addresses')]):
            print(f"\n  All Extracted:")
            if intel.get('bank_accounts'):
                print(f"    💳 Bank: {', '.join(intel['bank_accounts'])}")
            if intel.get('upi_ids'):
                print(f"    💰 UPI: {', '.join(intel['upi_ids'])}")
            if intel.get('phishing_urls'):
                print(f"    🔗 URLs: {', '.join(intel['phishing_urls'])}")
            if intel.get('phone_numbers'):
                print(f"    📞 Phone: {', '.join(intel['phone_numbers'])}")
            if intel.get('email_addresses'):
                print(f"    📧 Email: {', '.join(intel['email_addresses'])}")
    
    def run_test_suite(self, tests: List[TestCase], suite_name: str):
        """Run a suite of tests."""
        print(f"\n{'=' * 80}")
        print(f"🧪 {suite_name}")
        print(f"{'=' * 80}")
        
        suite_results = []
        for i, test in enumerate(tests, 1):
            print(f"\n[{i}/{len(tests)}] Running: {test.id}...")
            result = self.run_test(test)
            self.print_result(result)
            suite_results.append(result)
            
            # Small delay between tests
            if i < len(tests):
                time.sleep(0.5)
        
        # Suite summary
        passed_count = sum(1 for r in suite_results if r['passed'])
        print(f"\n{'─' * 80}")
        print(f"Suite Results: {passed_count}/{len(tests)} passed ({passed_count/len(tests)*100:.1f}%)")
        print(f"{'=' * 80}")
        
        return suite_results
    
    def generate_report(self):
        """Generate final evaluation report."""
        print(f"\n\n{'=' * 80}")
        print("📊 FINAL EVALUATION REPORT")
        print(f"{'=' * 80}\n")
        
        # Group by category
        categories = {}
        for result in self.results:
            cat = result['category']
            if cat not in categories:
                categories[cat] = {'passed': 0, 'total': 0}
            categories[cat]['total'] += 1
            if result['passed']:
                categories[cat]['passed'] += 1
        
        # Category breakdown
        print("Category Performance:")
        print("─" * 80)
        for cat, stats in sorted(categories.items()):
            pct = stats['passed'] / stats['total'] * 100
            status = "✅" if pct >= 80 else "⚠️" if pct >= 60 else "❌"
            print(f"{status} {cat:25s}: {stats['passed']:2d}/{stats['total']:2d} ({pct:5.1f}%)")
        
        # Overall metrics
        total_passed = sum(r['passed'] for r in self.results)
        total_tests = len(self.results)
        overall_pct = total_passed / total_tests * 100
        
        avg_response_time = sum(r.get('response_time', 0) for r in self.results if 'response_time' in r) / len([r for r in self.results if 'response_time' in r])
        
        print(f"\n{'─' * 80}")
        print(f"Overall Score: {total_passed}/{total_tests} ({overall_pct:.1f}%)")
        print(f"Average Response Time: {avg_response_time:.2f}s")
        
        # Grade
        if overall_pct >= 95:
            grade = "A+ (Excellent)"
        elif overall_pct >= 90:
            grade = "A (Very Good)"
        elif overall_pct >= 80:
            grade = "B (Good)"
        elif overall_pct >= 70:
            grade = "C (Acceptable)"
        else:
            grade = "D (Needs Improvement)"
        
        print(f"Final Grade: {grade}")
        print(f"{'=' * 80}\n")


def main():
    """Run comprehensive evaluator tests."""
    runner = EvaluatorTestRunner()
    
    # ===== FALSE POSITIVE PREVENTION TESTS =====
    fp_tests = [
        TestCase(
            id="fp-social-01",
            category="False Positive",
            message="Hey! Want to grab lunch tomorrow? There's a new cafe that just opened near the office.",
            expected_scam=False,
            expected_confidence_min=0.0,
            description="Social lunch invitation"
        ),
        TestCase(
            id="fp-work-01",
            category="False Positive",
            message="Can we meet tomorrow to review the quarterly report? I need your account analysis by 5pm.",
            expected_scam=False,
            expected_confidence_min=0.0,
            description="Work meeting discussion"
        ),
        TestCase(
            id="fp-business-01",
            category="False Positive",
            message="Your Amazon order #12345 has been shipped. Track your package at amazon.com/track. Delivery expected by Friday.",
            expected_scam=False,
            expected_confidence_min=0.0,
            description="Legitimate business notification"
        ),
    ]
    
    # ===== ADVANCED SCAM TESTS =====
    scam_tests = [
        TestCase(
            id="as-upi-01",
            category="Advanced Scam",
            message="Congratulations! You have won Rs. 50,000 prize money. To claim, please send processing fee of Rs. 500 to 9876543210@paytm. Hurry, offer valid for 24 hours only!",
            expected_scam=True,
            expected_confidence_min=0.75,
            expected_extractions={'upi_ids': ['9876543210@paytm']},
            description="Prize scam with UPI payment"
        ),
        TestCase(
            id="as-banking-01",
            category="Advanced Scam",
            message="URGENT! Your SBI account has been compromised. Your account will be blocked in 2 hours. Share your account number and OTP immediately to verify your identity.",
            expected_scam=True,
            expected_confidence_min=0.80,
            description="Banking fraud impersonation"
        ),
        TestCase(
            id="as-crypto-01",
            category="Advanced Scam",
            message="I made $50,000 in just 2 weeks with this crypto bot! Join now and get 5 free trades. Limited to first 100 members. Don't miss out!",
            expected_scam=True,
            expected_confidence_min=0.70,
            description="Cryptocurrency investment scam"
        ),
        TestCase(
            id="as-tech-01",
            category="Advanced Scam",
            message="Microsoft Security Alert: Your computer is infected with virus. Call +1-800-555-FAKE immediately for urgent tech support.",
            expected_scam=True,
            expected_confidence_min=0.75,
            expected_extractions={'phone_numbers': ['+1-800-555-FAKE']},
            description="Tech support scam"
        ),
    ]
    
    # ===== INTELLIGENCE EXTRACTION TESTS =====
    intel_tests = [
        TestCase(
            id="ie-multi-01",
            category="Intelligence",
            message="Transfer to account 1234567890123456 or UPI: test@paytm. Call +91-9876543210 or email scam@fraud.com",
            expected_scam=True,
            expected_confidence_min=0.60,
            expected_extractions={
                'bank_accounts': ['1234567890123456'],
                'upi_ids': ['test@paytm'],
                'phone_numbers': ['+91-9876543210'],
                'email_addresses': ['scam@fraud.com']
            },
            description="Multiple data type extraction"
        ),
    ]
    
    # ===== EDGE CASE TESTS =====
    edge_tests = [
        TestCase(
            id="ec-short-01",
            category="Edge Case",
            message="Hi",
            expected_scam=False,
            expected_confidence_min=0.0,
            description="Very short message"
        ),
        TestCase(
            id="ec-caps-01",
            category="Edge Case",
            message="URGENT!!! YOUR ACCOUNT HAS BEEN HACKED!!! CALL +1-800-SCAM-NOW IMMEDIATELY OR LOSE ALL YOUR MONEY!!!",
            expected_scam=True,
            expected_confidence_min=0.70,
            description="ALL CAPS urgent scam"
        ),
    ]
    
    # Run all test suites
    print("=" * 80)
    print("🎯 COMPREHENSIVE API EVALUATION")
    print("=" * 80)
    print(f"\nTesting API: {runner.base_url}")
    print(f"Total Test Cases: {len(fp_tests) + len(scam_tests) + len(intel_tests) + len(edge_tests)}")
    print("\nStarting tests in 2 seconds...")
    time.sleep(2)
    
    runner.results.extend(runner.run_test_suite(fp_tests, "FALSE POSITIVE PREVENTION"))
    runner.results.extend(runner.run_test_suite(scam_tests, "ADVANCED SCAM DETECTION"))
    runner.results.extend(runner.run_test_suite(intel_tests, "INTELLIGENCE EXTRACTION"))
    runner.results.extend(runner.run_test_suite(edge_tests, "EDGE CASES"))
    
    # Generate final report
    runner.generate_report()


if __name__ == "__main__":
    main()
