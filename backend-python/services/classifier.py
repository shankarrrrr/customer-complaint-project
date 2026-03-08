import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

CATEGORIES = ["ATM Failure", "UPI Failure", "Mobile App", "Loan", "Card", "Net Banking", "Other"]
PRODUCTS = ["Debit Card", "Credit Card", "UPI", "Loan", "Savings Account", "Current Account", "Fixed Deposit", "Other"]
SEVERITIES = ["Low", "Medium", "High", "Critical"]

def classify_complaint(raw_text: str) -> dict:
    """
    Use Gemini API to classify complaint and extract structured information
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""Analyze this customer complaint and extract structured information.

Complaint: "{raw_text}"

Extract and return ONLY a JSON object with these fields:
- category: one of {CATEGORIES}
- product: one of {PRODUCTS}
- severity: one of {SEVERITIES}
- language: detected language code (en, hi, mr, ta, te, bn, gu)
- department: which bank department should handle this (Cards, Loans, Digital Banking, Branch Operations, ATM Operations)

Return ONLY valid JSON, no other text."""

        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = json.loads(result_text)
        
        return result
        
    except Exception as e:
        print(f"Gemini classification error: {e}")
        # Fallback to keyword matching
        return fallback_classification(raw_text)

def fallback_classification(raw_text: str) -> dict:
    """
    Keyword-based fallback classification
    """
    text_lower = raw_text.lower()
    
    # Category detection
    category = "Other"
    if any(word in text_lower for word in ["atm", "cash", "withdrawal"]):
        category = "ATM Failure"
    elif any(word in text_lower for word in ["upi", "gpay", "phonepe", "paytm"]):
        category = "UPI Failure"
    elif any(word in text_lower for word in ["app", "mobile", "login"]):
        category = "Mobile App"
    elif any(word in text_lower for word in ["loan", "emi", "interest"]):
        category = "Loan"
    elif any(word in text_lower for word in ["card", "debit", "credit"]):
        category = "Card"
    elif any(word in text_lower for word in ["netbanking", "net banking", "online"]):
        category = "Net Banking"
    
    # Product detection
    product = "Other"
    if "debit" in text_lower:
        product = "Debit Card"
    elif "credit" in text_lower:
        product = "Credit Card"
    elif "upi" in text_lower:
        product = "UPI"
    elif "loan" in text_lower:
        product = "Loan"
    elif "savings" in text_lower:
        product = "Savings Account"
    
    # Severity detection
    severity = "Medium"
    if any(word in text_lower for word in ["urgent", "critical", "emergency", "fraud"]):
        severity = "Critical"
    elif any(word in text_lower for word in ["important", "serious", "problem"]):
        severity = "High"
    elif any(word in text_lower for word in ["minor", "small", "query"]):
        severity = "Low"
    
    # Department mapping
    department_map = {
        "ATM Failure": "ATM Operations",
        "UPI Failure": "Digital Banking",
        "Mobile App": "Digital Banking",
        "Loan": "Loans",
        "Card": "Cards",
        "Net Banking": "Digital Banking"
    }
    
    return {
        "category": category,
        "product": product,
        "severity": severity,
        "language": "en",
        "department": department_map.get(category, "Customer Service")
    }
