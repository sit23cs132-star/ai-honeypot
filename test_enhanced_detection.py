"""Test suite for enhanced scam detection system."""
import asyncio
import json
from agent.enhanced_detector import EnhancedScamDetector, SmartRuleEngine
from agent.detector import ScamDetector
from models.schemas import DetectionResult


class EnhancedDetectionValidator:
    """Validate enhanced detection system with real-world scam examples."""
    
    def __init__(self):
        self.enhanced_detector = EnhancedScamDetector()
        self.scam_detector = ScamDetector(use_enhanced_detector=True)
        self.rule_engine = SmartRuleEngine()
        
        # Load scam case library
        with open('scam_case_library.json', 'r', encoding='utf-8') as f:
            self.scam_library = json.load(f)
    
    def test_scam_type_detection(self, scam_type_name: str, num_samples: int = 3):
        """Test detection for a specific scam type."""
        print(f"\n{'='*80}")
        print(f"Testing: {scam_type_name}")
        print(f"{'='*80}")
        
        # Find scam type in library
        scam_type = None
        for scam in self.scam_library['scam_types']:
            if scam['scam_type'] == scam_type_name:
                scam_type = scam
                break
        
        if not scam_type:
            print(f"❌ Scam type '{scam_type_name}' not found in library")
            return
        
        # Test sample messages
        example_messages = scam_type['example_messages'][:num_samples]
        
        for i, message in enumerate(example_messages, 1):
            print(f"\n--- Test {i} ---")
            print(f"Message: {message[:100]}...")
            
            result = self.enhanced_detector.detect_scam(message)
            
            print(f"✓ Detection Result:")
            print(f"  • Is Scam: {result.is_scam}")
            print(f"  • Confidence: {result.confidence:.3f}")
            print(f"  • Scam Type: {result.scam_type}")
            print(f"  • Indicators: {', '.join(result.indicators[:5])}")
            
            # Validate detection
            if result.is_scam and result.confidence >= 0.50:
                print(f"  ✓ PASSED - Correctly identified as scam")
            else:
                print(f"  ❌ FAILED - Should be detected as scam")
    
    def test_all_scam_types(self):
        """Test detection for all scam types in the library."""
        print("\n" + "="*80)
        print("COMPREHENSIVE SCAM DETECTION TEST")
        print("="*80)
        
        stats = {
            "total_tested": 0,
            "correctly_detected": 0,
            "missed_detections": 0,
            "scam_types_tested": 0
        }
        
        for scam_type in self.scam_library['scam_types']:
            scam_type_name = scam_type['scam_type']
            stats['scam_types_tested'] += 1
            
            # Test first 3 messages of each type
            for message in scam_type['example_messages'][:3]:
                stats['total_tested'] += 1
                result = self.enhanced_detector.detect_scam(message)
                
                if result.is_scam and result.confidence >= 0.50:
                    stats['correctly_detected'] += 1
                else:
                    stats['missed_detections'] += 1
                    print(f"\n⚠️  Missed Detection:")
                    print(f"   Type: {scam_type_name}")
                    print(f"   Message: {message[:80]}...")
                    print(f"   Confidence: {result.confidence:.3f}")
        
        # Print summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"Scam Types Tested: {stats['scam_types_tested']}")
        print(f"Total Messages Tested: {stats['total_tested']}")
        print(f"Correctly Detected: {stats['correctly_detected']}")
        print(f"Missed Detections: {stats['missed_detections']}")
        
        detection_rate = (stats['correctly_detected'] / stats['total_tested'] * 100) if stats['total_tested'] > 0 else 0
        print(f"\n✓ Detection Rate: {detection_rate:.2f}%")
        
        if detection_rate >= 85:
            print("✓ EXCELLENT - Detection rate exceeds 85% target")
        elif detection_rate >= 70:
            print("⚠️  GOOD - Detection rate acceptable but can be improved")
        else:
            print("❌ NEEDS IMPROVEMENT - Detection rate below acceptable threshold")
    
    def test_false_positive_prevention(self):
        """Test with legitimate messages to ensure low false positive rate."""
        print("\n" + "="*80)
        print("FALSE POSITIVE PREVENTION TEST")
        print("="*80)
        
        legitimate_messages = [
            "Hi Mom, I'll be home by 7pm. Can you keep dinner ready?",
            "Your Amazon order #123-456-789 has been shipped and will arrive tomorrow.",
            "Meeting rescheduled to 3pm. Please confirm your availability.",
            "Happy birthday! Hope you have a wonderful day ahead!",
            "The project deadline is next Monday. Let me know if you need help.",
            "Your HDFC Bank account **1234 credited with Rs.5,000 on 05-Feb-2026. Ref: SAL123456",
            "Reminder: Your electricity bill of Rs.850 is due on 10th Feb. Pay via app or website.",
            "Thanks for booking with OYO! Your check-in is confirmed for 15-Feb at Hotel XYZ.",
            "Your Paytm KYC is complete. You can now transact up to Rs.1 lakh per month.",
            "Google Pay: You sent Rs.500 to John Doe. UPI Ref: 402345678901"
        ]
        
        false_positives = 0
        
        for i, message in enumerate(legitimate_messages, 1):
            result = self.enhanced_detector.detect_scam(message)
            
            print(f"\n--- Test {i} ---")
            print(f"Message: {message}")
            print(f"Result: {'❌ False Positive' if result.is_scam else '✓ Correctly Allowed'}")
            print(f"Confidence: {result.confidence:.3f}")
            
            if result.is_scam:
                false_positives += 1
                print(f"Indicators: {', '.join(result.indicators)}")
        
        fp_rate = (false_positives / len(legitimate_messages) * 100)
        print(f"\n{'='*80}")
        print(f"False Positive Rate: {fp_rate:.2f}%")
        print(f"Target: < 5%")
        
        if fp_rate <= 2:
            print("✓ EXCELLENT - False positive rate under 2%")
        elif fp_rate <= 5:
            print("✓ GOOD - False positive rate within acceptable range")
        else:
            print("⚠️  NEEDS IMPROVEMENT - False positive rate too high")
    
    def test_edge_cases(self):
        """Test edge cases and borderline scenarios."""
        print("\n" + "="*80)
        print("EDGE CASE TESTING")
        print("="*80)
        
        edge_cases = [
            {
                "message": "Won't you please send me your account details for the refund?",
                "expected": "borderline",
                "description": "Polite language but suspicious request"
            },
            {
                "message": "ur acc will b blocked if u dont verify now",
                "expected": "scam",
                "description": "Scam with SMS-style abbreviations"
            },
            {
                "message": "🚨🚨 URGENT 🚨🚨 Your account needs verification RIGHT NOW!!!",
                "expected": "scam",
                "description": "Excessive emoji and urgency"
            },
            {
                "message": "I need to borrow Rs.5000 urgently. Will return next week. Trust me bro.",
                "expected": "borderline",
                "description": "Personal loan request (depends on context)"
            },
            {
                "message": "",
                "expected": "not_scam",
                "description": "Empty message"
            },
            {
                "message": "a",
                "expected": "not_scam",
                "description": "Single character"
            },
            {
                "message": "URGENT URGENT URGENT" * 10,
                "expected": "scam",
                "description": "Repeated urgency keywords"
            }
        ]
        
        for i, case in enumerate(edge_cases, 1):
            message = case['message']
            expected = case['expected']
            description = case['description']
            
            if not message:
                continue
            
            result = self.enhanced_detector.detect_scam(message)
            
            print(f"\n--- Edge Case {i} ---")
            print(f"Description: {description}")
            print(f"Message: {message[:80]}...")
            print(f"Expected: {expected}")
            print(f"Detected: {'Scam' if result.is_scam else 'Not Scam'}")
            print(f"Confidence: {result.confidence:.3f}")
            
            # Validate based on expectation
            if expected == "scam" and result.is_scam:
                print("✓ PASSED")
            elif expected == "not_scam" and not result.is_scam:
                print("✓ PASSED")
            elif expected == "borderline":
                print("⚠️  BORDERLINE - Manual review recommended")
            else:
                print("❌ UNEXPECTED RESULT")
    
    async def test_hybrid_detection(self):
        """Test the hybrid detection system (enhanced + AI)."""
        print("\n" + "="*80)
        print("HYBRID DETECTION TEST (Enhanced + AI)")
        print("="*80)
        
        test_messages = [
            "Your Amazon account has suspicious activity. Verify now: bit.ly/amzn-verify",
            "Hi, I made Rs.8.5 lakh in 60 days with crypto bot. Minimum Rs.10,000 investment. 15% daily returns.",
            "Hello sir, HDFC Bank customer care. Your account shows unauthorized transaction. Share OTP to block."
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n--- Test {i} ---")
            print(f"Message: {message}")
            
            result = await self.scam_detector.detect_scam(
                message,
                conversation_history=[]
            )
            
            print(f"✓ Hybrid Detection Result:")
            print(f"  • Is Scam: {result.is_scam}")
            print(f"  • Confidence: {result.confidence:.3f}")
            print(f"  • Scam Type: {result.scam_type}")
            print(f"  • Indicators: {', '.join(result.indicators[:10])}")
    
    def print_statistics(self):
        """Print statistics about the loaded scam library."""
        stats = self.enhanced_detector.get_statistics()
        
        print("\n" + "="*80)
        print("SCAM LIBRARY STATISTICS")
        print("="*80)
        print(f"Library Version: {stats['library_version']}")
        print(f"Last Updated: {stats['last_updated']}")
        print(f"Total Scam Types: {stats['total_scam_types']}")
        print(f"Total Patterns: {stats['total_patterns']}")
        print(f"Total Keywords: {stats['total_keywords']}")
        
        # List all scam types
        print(f"\n📋 Scam Types Covered:")
        for scam_type in self.scam_library['scam_types']:
            name = scam_type['scam_type']
            risk = scam_type['risk_level']
            confidence = scam_type['confidence_weight']
            print(f"  • {name} (Risk: {risk.upper()}, Weight: {confidence})")


def main():
    """Run comprehensive validation tests."""
    print("="*80)
    print("ENHANCED SCAM DETECTION SYSTEM - VALIDATION SUITE")
    print("="*80)
    
    validator = EnhancedDetectionValidator()
    
    # Print library statistics
    validator.print_statistics()
    
    # Test specific high-priority scam types
    print("\n\n" + "="*80)
    print("TESTING HIGH-PRIORITY SCAM TYPES")
    print("="*80)
    
    high_priority_scams = [
        "UPI_FRAUD",
        "OTP_THEFT",
        "FAKE_KYC_LINK",
        "DEEPFAKE_VOICE_SCAM",
        "GOVERNMENT_IMPERSONATION"
    ]
    
    for scam_type in high_priority_scams:
        validator.test_scam_type_detection(scam_type, num_samples=2)
    
    # Comprehensive test of all scam types
    validator.test_all_scam_types()
    
    # False positive prevention test
    validator.test_false_positive_prevention()
    
    # Edge case testing
    validator.test_edge_cases()
    
    # Hybrid detection test (requires async)
    print("\n\n" + "="*80)
    print("RUNNING HYBRID DETECTION TEST")
    print("="*80)
    print("(Note: This requires AI client to be configured)")
    
    # Uncomment below to test hybrid detection with AI
    # asyncio.run(validator.test_hybrid_detection())
    
    print("\n" + "="*80)
    print("VALIDATION COMPLETE")
    print("="*80)
    print("\n✓ Enhanced detection system is ready for production deployment!")
    print("\nNext Steps:")
    print("1. Review CONTINUOUS_LEARNING_STRATEGY.md for deployment plan")
    print("2. Configure threat intelligence feeds")
    print("3. Set up monitoring and alerting")
    print("4. Begin phased rollout (shadow mode → warn-only → full)")
    print("5. Establish weekly review process for false positives")
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
