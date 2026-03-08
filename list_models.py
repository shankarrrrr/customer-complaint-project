import os
os.environ['GEMINI_API_KEY'] = 'AIzaSyDk_5VqS3_I-hSeoqIOwoy49L5mOGZb6io'

import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("Available Gemini Models:")
print("=" * 60)

for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"✅ {m.name}")
        print(f"   Display Name: {m.display_name}")
        print(f"   Description: {m.description[:100]}...")
        print()
