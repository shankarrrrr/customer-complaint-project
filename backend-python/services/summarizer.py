import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_summary(raw_text: str, category: str = None, severity: str = None) -> str:
    """
    Generate AI summary of complaint using Gemini
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        context = ""
        if category:
            context += f"Category: {category}. "
        if severity:
            context += f"Severity: {severity}. "
        
        prompt = f"""Summarize this customer complaint in 2-3 concise sentences for a bank agent.
{context}

Complaint: "{raw_text}"

Include:
1. What happened
2. What the customer wants
3. Urgency level

Keep it professional and factual."""

        response = model.generate_content(prompt)
        summary = response.text.strip()
        
        return summary
        
    except Exception as e:
        print(f"Summary generation error: {e}")
        # Fallback: truncate original text
        return raw_text[:200] + "..." if len(raw_text) > 200 else raw_text
