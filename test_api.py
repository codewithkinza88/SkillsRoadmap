from dotenv import load_dotenv
import os

# Fresh load with new key
load_dotenv(override=True)
from openai import OpenAI

client = OpenAI(api_key=os.getenv('GROQ_API_KEY'), base_url='https://api.groq.com/openai/v1')

try:
    print("Testing API connection...")
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Say hello in one word"}],
        temperature=0.3
    )
    print("✅ API Call Success!")
    print("Response:", response.choices[0].message.content)
except Exception as e:
    print(f"❌ API Error: {type(e).__name__}: {e}")
