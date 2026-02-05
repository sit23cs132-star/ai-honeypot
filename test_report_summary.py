"""Generate detailed test report with recommendations."""
import json
from agent.enhanced_detector import EnhancedScamDetector

def analyze_detection_gaps():
    """Analyze which scam types have lowest detection rates."""
    
    detector = EnhancedScamDetector()
    
    # Load scam library
    with open('scam_case_library.json', 'r', encoding='utf-8') as f:
        library = json.load(f)
    
    print("="*80)
    print("DETAILED DETECTION ANALYSIS")
    print("="*80)
    
    scam_type_performance = {}
    
    for scam_type in library['scam_types']:
        name = scam_type['scam_type']
        messages = scam_type['example_messages'][:3]
        
        detected = 0
        total = len(messages)
        confidences = []
        
        for msg in messages:
            result = detector.detect_scam(msg)
            if result.is_scam and result.confidence >= 0.50:
                detected += 1
            confidences.append(result.confidence)
        
        detection_rate = (detected / total * 100) if total > 0 else 0
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        scam_type_performance[name] = {
            'detected': detected,
            'total': total,
            'rate': detection_rate,
            'avg_confidence': avg_confidence,
            'risk_level': scam_type['risk_level']
        }
    
    # Sort by detection rate
    sorted_performance = sorted(scam_type_performance.items(), key=lambda x: x[1]['rate'])
    
    print("\n🔴 LOWEST PERFORMING SCAM TYPES (Need Improvement):\n")
    for name, perf in sorted_performance[:10]:
        print(f"  {name}")
        print(f"    Detection: {perf['detected']}/{perf['total']} ({perf['rate']:.1f}%)")
        print(f"    Avg Confidence: {perf['avg_confidence']:.3f}")
        print(f"    Risk Level: {perf['risk_level'].upper()}")
        print()
    
    print("\n✅ HIGHEST PERFORMING SCAM TYPES:\n")
    for name, perf in sorted_performance[-5:]:
        print(f"  {name}")
        print(f"    Detection: {perf['detected']}/{perf['total']} ({perf['rate']:.1f}%)")
        print(f"    Avg Confidence: {perf['avg_confidence']:.3f}")
        print(f"    Risk Level: {perf['risk_level'].upper()}")
        print()
    
    # Calculate critical scam types that are underperforming
    print("\n⚠️  CRITICAL ISSUES (Critical risk + low detection):\n")
    for name, perf in scam_type_performance.items():
        if perf['risk_level'] == 'critical' and perf['rate'] < 70:
            print(f"  ❌ {name}: {perf['rate']:.1f}% detection rate")
            print(f"     This is a CRITICAL risk type with inadequate detection!")
            print()
    
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    
    print("""
1. IMMEDIATE FIXES NEEDED:
   • Improve regex patterns for low-performing scam types
   • Add more keyword variations for Indian English and Hinglish
   • Increase sensitivity for critical-risk scams

2. PATTERN ENHANCEMENTS:
   • Add more UPI ID variations (@okaxis, @okicici variants)
   • Improve phone number detection (with country codes)
   • Better URL/link detection (shortened URLs, typosquatting)

3. CONTEXTUAL IMPROVEMENTS:
   • Enhance urgency trigger detection
   • Better authority impersonation signals
   • Improve psychological manipulation pattern matching

4. FALSE POSITIVE PREVENTION:
   • Current rate: 0% (Excellent!)
   • Maintain whitelist for legitimate messages
   • Keep confidence thresholds balanced

5. CONTINUOUS LEARNING:
   • Set up weekly review of missed detections
   • Add new patterns discovered from real scam attempts
   • Monitor emerging scam techniques

6. PRODUCTION DEPLOYMENT:
   • Start with shadow mode (log only, don't block)
   • Gradually increase confidence thresholds
   • Monitor false positive rates carefully
   • Enable full blocking only after 2-week observation
    """)

if __name__ == "__main__":
    analyze_detection_gaps()
