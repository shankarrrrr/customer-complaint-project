import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_draft_response(complaint_text: str, category: str, customer_name: str = "Customer") -> dict:
    """
    Generate draft response using Gemini API
    Returns both short (SMS/WhatsApp) and long (Email) versions
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""You are a professional bank customer service agent. Generate TWO response drafts for this complaint:

Complaint Category: {category}
Customer Name: {customer_name}
Complaint: "{complaint_text}"

Generate:
1. SHORT VERSION (for SMS/WhatsApp, max 160 characters): Brief acknowledgment with ticket number placeholder and timeline
2. LONG VERSION (for Email, 3-4 paragraphs): Professional, empathetic, detailed response with resolution steps

Use professional banking tone. Include:
- Acknowledgment and apology
- Understanding of the issue
- Resolution steps
- Timeline (24-48 hours typical)
- Contact information placeholder

Format as JSON:
{{"short_version": "...", "long_version": "..."}}"""

        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Extract JSON
        import json
        import re
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = json.loads(result_text)
        
        return result
        
    except Exception as e:
        print(f"Draft generation error: {e}")
        # Fallback templates
        return {
            "short_version": f"Dear {customer_name}, we've received your complaint. Our team is working on it. You'll hear from us within 24-48 hours. Ref: [TICKET_ID]",
            "long_version": f"""Dear {customer_name},

Thank you for bringing this matter to our attention. We sincerely apologize for the inconvenience you've experienced with {category}.

We have registered your complaint and our specialized team is currently investigating the issue. We understand how important this is to you and are committed to resolving it at the earliest.

You can expect an update from us within 24-48 hours. If you need immediate assistance, please contact our customer care at 1800-XXX-XXXX.

Thank you for your patience and for banking with us.

Best regards,
Customer Service Team"""
        }
