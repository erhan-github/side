import os
import asyncio
import traceback
from side.llm.client import LLMClient

async def debug():
    print("🔍 Initializing LLMClient...")
    client = LLMClient(preferred_provider="groq")
    
    print(f"📡 Selected Provider: {client.provider}")
    print(f"📡 API Key (First 10): {os.getenv('GROQ_API_KEY', 'MISSING')[:10]}...")
    
    prompt = [{"role": "user", "content": "Hello"}]
    system = "Be brief."
    
    try:
        print("🚀 Sending request to Groq...")
        response = await client.complete_async(prompt, system)
        print(f"✅ SUCCESS: {response}")
    except Exception as e:
        print("❌ FAILURE DETECTED")
        print(f"Error Type: {type(e)}")
        print(f"Error Message: {e}")
        print("\n--- FULL TRACEBACK ---")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug())
