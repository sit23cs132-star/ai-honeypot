"""Validate scam_case_library.json structure."""
import json

try:
    with open('scam_case_library.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("✓ JSON structure is VALID")
    print(f"\nLibrary Statistics:")
    print(f"  Version: {data['metadata']['version']}")
    print(f"  Total scam types: {len(data['scam_types'])}")
    print(f"  Total example messages: {sum(len(s['example_messages']) for s in data['scam_types'])}")
    print(f"  Total keywords: {sum(len(s['keywords']) for s in data['scam_types'])}")
    print(f"  Total regex patterns: {sum(len(s['regex_patterns']) for s in data['scam_types'])}")
    
    # Validate required fields
    required_fields = ['scam_type', 'category', 'risk_level', 'example_messages', 
                      'keywords', 'regex_patterns', 'intent_signals']
    
    print(f"\nValidating scam type structures...")
    issues = []
    for scam in data['scam_types']:
        for field in required_fields:
            if field not in scam:
                issues.append(f"Missing field '{field}' in {scam.get('scam_type', 'UNKNOWN')}")
    
    if issues:
        print("❌ Issues found:")
        for issue in issues:
            print(f"  • {issue}")
    else:
        print("✓ All scam types have required fields")
    
    print("\n" + "="*60)
    print("VALIDATION COMPLETE")
    print("="*60)
    
except json.JSONDecodeError as e:
    print(f"❌ JSON parsing error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
