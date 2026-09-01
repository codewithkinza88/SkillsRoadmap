from dotenv import load_dotenv
import os
load_dotenv(override=True)
from openai import OpenAI

client = OpenAI(api_key=os.getenv('GROQ_API_KEY'), base_url='https://api.groq.com/openai/v1')

try:
    models = client.models.list()
    print("✅ Available Groq Models:")
    for model in models.data:
        print(f"  - {model.id}")
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTrying common models...")
    for model_name in ["llama-3.1-70b-versatile", "llama3-70b", "gemma-7b-it", "gemma2-9b-it"]:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": "hi"}],
                temperature=0.3,
                max_tokens=10
            )
            print(f"✅ {model_name} works!")
        except Exception as e:
            print(f"❌ {model_name}: {str(e)[:80]}")
