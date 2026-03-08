"""
Quick test to verify Gemini API key works
"""
import os
os.environ['GEMINI_API_KEY'] = 'AIzaSyDk_5VqS3_I-hSeoqIOwoy49L5mOGZb6io'

try:
    import google.generativeai as genai
    
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-pro')
    
    print("🔑 Testing Gemini API Key...")
    print("=" * 50)
    
    # Test classification
    prompt = """Classify this banking complaint:
    "My ATM card is stuck in the machine and money was debited from my account"
    
    Return JSON with: category, severity, sentiment"""
    
    response = model.generate_content(prompt)
    
    print("✅ Gemini API Key is VALID!")
    print("\nTest Response:")
    print(response.text)
    print("=" * 50)
    print("\n✨ Your AI-powered complaint system is ready!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nPlease check:")
    print("1. Internet connection")
    print("2. API key is correct")
    print("3. Gemini API is enabled")
