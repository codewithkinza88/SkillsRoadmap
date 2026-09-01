import sys
print("Python version:", sys.version)

try:
    print("1. Loading dotenv...")
    from dotenv import load_dotenv
    import os
    load_dotenv()
    print("   ✅ dotenv loaded")
    
    print("2. Importing gradio...")
    import gradio as gr
    print("   ✅ gradio loaded")
    
    print("3. Importing OpenAI...")
    from openai import OpenAI
    print("   ✅ openai loaded")
    
    print("4. Creating OpenAI client...")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
    print("   ✅ OpenAI client created")
    
    print("\n5. Importing app...")
    import app
    print("   ✅ app imported successfully!")
    
except Exception as e:
    print(f"   ❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
