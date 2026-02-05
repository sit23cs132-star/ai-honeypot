"""Test client for the honey-pot API."""
import requests
import json
from typing import Dict, List


class HoneyPotClient:
    """Client for testing the honey-pot API."""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = "honeypot-secure-key-2026"):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def analyze_message(
        self,
        conversation_id: str,
        message: str,
        conversation_history: List[Dict] = None
    ) -> Dict:
        """Send a message for analysis."""
        url = f"{self.base_url}/api/analyze"
        
        payload = {
            "conversation_id": conversation_id,
            "message": message,
            "conversation_history": conversation_history or []
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def health_check(self) -> Dict:
        """Check API health."""
        url = f"{self.base_url}/health"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()


def run_sample_scam_conversation():
    """Run a sample scam conversation for testing."""
    client = HoneyPotClient()
    
    # Test conversation scenarios
    scenarios = [
        {
            "name": "Prize Scam",
            "messages": [
                "Congratulations! You've won $10,000 in our lucky draw!",
                "To claim your prize, please provide your bank account details.",
                "We need your account number and UPI ID to transfer the money.",
                "Please hurry, the offer expires in 24 hours!"
            ]
        },
        {
            "name": "Tech Support Scam",
            "messages": [
                "This is Microsoft Tech Support. Your computer has been infected with a virus.",
                "We need immediate access to fix the issue.",
                "Please click this link to download our security tool: http://fake-microsoft.com/fix",
                "Call us at +1-800-FAKE-TECH for immediate assistance."
            ]
        },
        {
            "name": "Investment Scam",
            "messages": [
                "Invest in cryptocurrency and earn 300% returns in just 30 days!",
                "Join thousands of successful investors today.",
                "Send Bitcoin to our wallet: 1FakeAddress123xyz",
                "Limited spots available - act now!"
            ]
        }
    ]
    
    print("=" * 60)
    print("AGENTIC HONEY-POT TEST CLIENT")
    print("=" * 60)
    
    # Health check first
    print("\n[Health Check]")
    try:
        health = client.health_check()
        print(f"✓ API Status: {health['status']}")
        print(f"✓ AI Provider: {health['ai_provider']}")
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return
    
    # Test each scenario
    for scenario in scenarios:
        print(f"\n\n{'=' * 60}")
        print(f"SCENARIO: {scenario['name']}")
        print(f"{'=' * 60}\n")
        
        conversation_id = f"test_{scenario['name'].lower().replace(' ', '_')}"
        conversation_history = []
        
        for i, message in enumerate(scenario['messages'], 1):
            print(f"\n[Turn {i}] Scammer: {message}")
            
            try:
                result = client.analyze_message(
                    conversation_id=conversation_id,
                    message=message,
                    conversation_history=conversation_history
                )
                
                print(f"\n[Agent Response]: {result['response']}")
                print(f"\nScam Detected: {result['scam_detected']}")
                print(f"Confidence: {result['confidence_score']:.2%}")
                print(f"Turn Count: {result['turn_count']}")
                print(f"Engagement Active: {result['engagement_active']}")
                
                # Show extracted intelligence if any
                intel = result['extracted_intelligence']
                if any([intel['bank_accounts'], intel['upi_ids'], intel['phishing_urls'], 
                       intel['phone_numbers'], intel['email_addresses']]):
                    print(f"\n📊 Extracted Intelligence:")
                    if intel['bank_accounts']:
                        print(f"  💳 Bank Accounts: {', '.join(intel['bank_accounts'])}")
                    if intel['upi_ids']:
                        print(f"  💰 UPI IDs: {', '.join(intel['upi_ids'])}")
                    if intel['phishing_urls']:
                        print(f"  🔗 URLs: {', '.join(intel['phishing_urls'])}")
                    if intel['phone_numbers']:
                        print(f"  📞 Phone Numbers: {', '.join(intel['phone_numbers'])}")
                    if intel['email_addresses']:
                        print(f"  📧 Emails: {', '.join(intel['email_addresses'])}")
                    if intel['scam_indicators']:
                        print(f"  ⚠️  Indicators: {', '.join(intel['scam_indicators'][:3])}")
                
                # Update conversation history
                conversation_history.append({"role": "scammer", "message": message})
                conversation_history.append({"role": "agent", "message": result['response']})
                
            except Exception as e:
                print(f"✗ Error: {e}")
                break
    
    print(f"\n\n{'=' * 60}")
    print("TEST COMPLETED")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    run_sample_scam_conversation()
