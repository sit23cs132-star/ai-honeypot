"""Quick manual test of specific scam messages."""
from agent.enhanced_detector import EnhancedScamDetector
import json

def test_specific_messages():
    """Test specific scam scenarios and show detailed breakdown."""
    
    detector = EnhancedScamDetector()
    
    test_messages = [
        {
            "category": "UPI Fraud",
            "message": "Hello sir, I am from Paytm customer care. Your KYC is pending. Please complete verification by sending Rs.1 to verify.paytm@paytm",
            "should_detect": True
        },
        {
            "category": "OTP Theft",
            "message": "Your OTP is 543210. Do not share with anyone. Valid for 10 minutes.",
            "should_detect": False
        },
        {
            "category": "Phishing Link",
            "message": "Your account has been compromised. Click here to secure: bit.ly/secure-acc-now",
            "should_detect": True
        },
        {
            "category": "QR Code Scam",
            "message": "I will buy your item. Scan this QR code to receive payment of Rs.5000",
            "should_detect": True
        },
        {
            "category": "Legitimate Message",
            "message": "Hi, meeting is at 3pm today. See you there!",
            "should_detect": False
        },
        {
            "category": "Crypto Investment",
            "message": "Join our Bitcoin trading group. Guaranteed 300% returns in 30 days. Minimum investment Rs.10,000",
            "should_detect": True
        },
        {
            "category": "Deepfake Voice",
            "message": "[Voice call] Papa I'm in trouble. Met with accident. Need Rs.50,000 urgent for hospital. Don't call this number, it's borrowed phone",
            "should_detect": True
        },
        {
            "category": "Fake KYC",
            "message": "HDFC Bank: Your KYC will expire today. Update now at hdfc-kyc-update.com or account will be frozen",
            "should_detect": True
        }
    ]
    
    print("="*80)
    print("MANUAL DETECTION TEST - SPECIFIC SCENARIOS")
    print("="*80)
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_messages, 1):
        print(f"\n{'─'*80}")
        print(f"Test {i}: {test['category']}")
        print(f"{'─'*80}")
        print(f"Message: {test['message']}")
        print(f"\nExpected: {'SCAM' if test['should_detect'] else 'LEGITIMATE'}")
        
        result = detector.detect_scam(test['message'])
        
        print(f"\n🔍 Detection Result:")
        print(f"   Detected as: {'SCAM' if result.is_scam else 'LEGITIMATE'}")
        print(f"   Confidence: {result.confidence:.3f}")
        print(f"   Scam Type: {result.scam_type if result.scam_type else 'None'}")
        print(f"   Indicators Found ({len(result.indicators)}):")
        for ind in result.indicators[:8]:
            print(f"      • {ind}")
        
        # Check if detection matches expectation
        correct = (result.is_scam and result.confidence >= 0.50) == test['should_detect']
        
        if correct:
            print(f"\n   ✅ PASS - Detected correctly")
            passed += 1
        else:
            print(f"\n   ❌ FAIL - Detection mismatch")
            failed += 1
    
    print(f"\n{'='*80}")
    print(f"SUMMARY: {passed}/{len(test_messages)} tests passed ({passed/len(test_messages)*100:.1f}%)")
    print(f"{'='*80}")

def show_library_stats():
    """Show scam library statistics."""
    
    with open('scam_case_library.json', 'r', encoding='utf-8') as f:
        library = json.load(f)
    
    print("\n" + "="*80)
    print("SCAM CASE LIBRARY STATISTICS")
    print("="*80)
    
    print(f"\nLibrary Version: {library['metadata']['version']}")
    print(f"Last Updated: {library['metadata']['last_updated']}")
    print(f"Total Scam Types: {library['metadata']['total_scam_types']}")
    
    total_examples = 0
    total_keywords = 0
    total_patterns = 0
    
    risk_breakdown = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
    
    for scam in library['scam_types']:
        total_examples += len(scam['example_messages'])
        total_keywords += len(scam['keywords'])
        total_patterns += len(scam['regex_patterns'])
        risk_breakdown[scam['risk_level']] += 1
    
    print(f"\n📊 Content Statistics:")
    print(f"   Total Example Messages: {total_examples}")
    print(f"   Total Keywords: {total_keywords}")
    print(f"   Total Regex Patterns: {total_patterns}")
    
    print(f"\n⚠️  Risk Level Distribution:")
    print(f"   Critical: {risk_breakdown['critical']}")
    print(f"   High: {risk_breakdown['high']}")
    print(f"   Medium: {risk_breakdown['medium']}")
    print(f"   Low: {risk_breakdown['low']}")
    
    print(f"\n📋 All Scam Types:")
    for scam in library['scam_types']:
        print(f"   • {scam['scam_type']} ({scam['risk_level'].upper()})")

if __name__ == "__main__":
    show_library_stats()
    print("\n")
    test_specific_messages()
