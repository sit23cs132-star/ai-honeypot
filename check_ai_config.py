"""Check AI configuration and API connectivity."""
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

print("="*70)
print("AI CONFIGURATION DIAGNOSTIC")
print("="*70)

# Check environment variables
print("\n[1] Environment Variables")
print("-"*70)
api_key = os.getenv("API_KEY", "")
ai_provider = os.getenv("AI_PROVIDER", "")
openai_key = os.getenv("OPENAI_API_KEY", "")
anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")

print(f"API_KEY: {'✅ Set' if api_key else '❌ Missing'}")
print(f"AI_PROVIDER: {ai_provider if ai_provider else '❌ Not set'}")
print(f"OPENAI_API_KEY: {'✅ Set (' + openai_key[:10] + '...)' if openai_key and len(openai_key) > 10 else '❌ Missing or invalid'}")
print(f"ANTHROPIC_API_KEY: {'✅ Set (' + anthropic_key[:10] + '...)' if anthropic_key and len(anthropic_key) > 10 else '❌ Missing'}")

# Check which provider should be used
print(f"\n[2] AI Provider Configuration")
print("-"*70)
if ai_provider == "openai":
    if openai_key and len(openai_key) > 20:
        print("✅ OpenAI configured correctly")
        test_provider = "openai"
    else:
        print("❌ OpenAI selected but API key missing or invalid!")
        print("   Set OPENAI_API_KEY in your .env file")
        test_provider = None
elif ai_provider == "anthropic":
    if anthropic_key and len(anthropic_key) > 20:
        print("✅ Anthropic configured correctly")
        test_provider = "anthropic"
    else:
        print("❌ Anthropic selected but API key missing!")
        print("   Set ANTHROPIC_API_KEY in your .env file")
        test_provider = None
else:
    print("❌ AI_PROVIDER not set or invalid")
    print("   Set AI_PROVIDER=openai or AI_PROVIDER=anthropic")
    test_provider = None

# Test AI connectivity
if test_provider:
    print(f"\n[3] Testing {test_provider.upper()} API Connectivity")
    print("-"*70)
    
    async def test_ai():
        try:
            from utils.ai_client import AIClient
            client = AIClient()
            
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'API is working!' if you can read this."}
            ]
            
            response = await client.generate_completion(
                messages=messages,
                temperature=0.7,
                max_tokens=50
            )
            
            print(f"✅ AI API is responding!")
            print(f"   Response: {response[:100]}")
            return True
            
        except Exception as e:
            print(f"❌ AI API test failed!")
            print(f"   Error: {str(e)}")
            return False
    
    # Run async test
    result = asyncio.run(test_ai())
    
    if not result:
        print("\n📋 TROUBLESHOOTING:")
        if test_provider == "openai":
            print("1. Verify your OpenAI API key at https://platform.openai.com/api-keys")
            print("2. Check if you have credits/billing enabled")
            print("3. Try regenerating your API key")
        elif test_provider == "anthropic":
            print("1. Verify your Anthropic API key at https://console.anthropic.com/")
            print("2. Check if your key has the correct permissions")
            print("3. Ensure you have API access enabled")
else:
    print("\n❌ Cannot test AI connectivity - configuration issues")
    print("\n📋 REQUIRED ACTIONS:")
    print("1. Copy .env.example to .env")
    print("2. Set AI_PROVIDER=openai (or anthropic)")
    print("3. Add your API key:")
    print("   - For OpenAI: OPENAI_API_KEY=sk-...")
    print("   - For Anthropic: ANTHROPIC_API_KEY=sk-ant-...")

print("\n" + "="*70)
print("DIAGNOSTIC COMPLETE")
print("="*70)

if test_provider and api_key:
    print("\n✅ Configuration looks good!")
    print("   If you're still seeing repeated responses, it may be due to:")
    print("   - API rate limits")
    print("   - Network connectivity issues")
    print("   - Insufficient API credits")
else:
    print("\n⚠️  Please fix the configuration issues above")
