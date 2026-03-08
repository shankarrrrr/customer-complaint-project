import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_root_cause(complaints: list, cluster_label: str, region: str = None) -> str:
    """
    Analyze multiple similar complaints to identify root cause
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Prepare complaint summaries
        complaint_texts = "\n".join([f"- {c}" for c in complaints[:20]])  # Limit to 20
        
        context = f"Region: {region}. " if region else ""
        
        prompt = f"""Analyze these {len(complaints)} similar customer complaints from a bank and identify the probable root cause.

{context}Cluster: {cluster_label}

Complaints:
{complaint_texts}

Provide:
1. Probable root cause (1-2 sentences)
2. Recommended system action to prevent future occurrences
3. Urgency level (Low/Medium/High/Critical)

Be specific and actionable."""

        response = model.generate_content(prompt)
        analysis = response.text.strip()
        
        return analysis
        
    except Exception as e:
        print(f"Root cause analysis error: {e}")
        return f"Pattern detected: {len(complaints)} similar complaints in cluster '{cluster_label}'. Manual investigation recommended."
