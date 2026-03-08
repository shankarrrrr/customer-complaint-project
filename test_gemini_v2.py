"""
Test Gemini API with updated package
"""
import os
os.environ['GEMINI_API_KEY'] = 'AIzaSyDk_5VqS3_I-hSeoqIOwoy49L5mOGZb6io'

try:
    # Try the new package first
    try:
        from google import genai
        from google.genai import types
        
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        
        print("🔑 Testing Gemini API Key (New SDK)...")
        print("=" * 50)
        
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents='Classify this banking complaint: "My ATM card is stuck" Return JSON with category and severity'
        )
        
        print("✅ Gemini API Key is VALID!")
        print("\nTest Response:")
        print(response.text)
        
    except ImportError:
        # Fallback to old package
        import google.generativeai as genai
        
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        
        # List available models
        print("🔍 Checking available models...")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"  - {m.name}")
        
        # Try with gemini-1.0-pro
        model = genai.GenerativeModel('gemini-1.0-pro')
        
        print("\n🔑 Testing Gemini API Key...")
        print("=" * 50)
        
        response = model.generate_content(
            'Classify this banking complaint: "My ATM card is stuck" Return JSON with category and severity'
        )
        
        print("✅ Gemini API Key is VALID!")
        print("\nTest Response:")
        print(response.text)
    
    print("=" * 50)
    print("\n✨ Your AI-powered complaint system is ready!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check internet connection")
    print("2. Verify API key is correct")
    print("3. Ensure Gemini API is enabled in Google Cloud Console")
    print("4. Try: pip install --upgrade google-generativeai")
