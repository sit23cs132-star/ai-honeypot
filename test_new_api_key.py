"""Test new OpenAI API key to verify it has credits."""
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

async def test_openai_api():
    from utils.ai_client import AIClient
    
    api_key = os.getenv("OPENAI_API_KEY", "")
    
    print("="*70)
    print("TESTING NEW OPENAI API KEY")
    print("="*70)
    print(f"\nAPI Key: {api_key[:20]}...{api_key[-10:]}")
    print(f"Model: {os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')}")
    
    try:
        client = AIClient()
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'API key is working!' if you can read this."}
        ]
        
        print(f"\nSending test request to OpenAI...")
        
        response = await client.generate_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=50
        )
        
        print(f"\n✅ SUCCESS! OpenAI API is working!")
        print(f"Response: {response}")
        print(f"\n🎉 The new API key has credits and is ready to use!")
        print(f"\nYou can now update this key on Render to enable AI-powered responses.")
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ FAILED! OpenAI API test failed!")
        print(f"Error: {error_msg}")
        
        if "429" in error_msg or "quota" in error_msg.lower():
            print(f"\n⚠️  This API key also has no credits (Error 429).")
            print(f"The contextual fallback system will continue to work.")
        elif "401" in error_msg or "invalid" in error_msg.lower():
            print(f"\n⚠️  This API key might be invalid or expired.")
        else:
            print(f"\n⚠️  Unknown error occurred.")
        
        return False

# Run the test
if __name__ == "__main__":
    result = asyncio.run(test_openai_api())
    
    print(f"\n{'='*70}")
    if result:
        print("RESULT: ✅ New API key is ready for deployment!")
    else:
        print("RESULT: ❌ New API key has issues. Check error above.")
    print("="*70)
