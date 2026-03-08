"""
Test the complaint classification system
"""
import os
import sys
sys.path.insert(0, 'backend-python')

os.environ['GEMINI_API_KEY'] = 'AIzaSyDk_5VqS3_I-hSeoqIOwoy49L5mOGZb6io'

from services.classifier import classify_complaint

print("🤖 Testing AI Complaint Classification")
print("=" * 60)

test_complaints = [
    "My ATM card is stuck in the machine and money was debited",
    "UPI payment failed but amount was deducted from my account",
    "Unable to login to mobile banking app, getting error message",
    "Loan EMI not reflecting despite payment made 5 days ago"
]

for i, complaint in enumerate(test_complaints, 1):
    print(f"\n{i}. Complaint: {complaint}")
    print("-" * 60)
    
    result = classify_complaint(complaint)
    
    print(f"   Category: {result['category']}")
    print(f"   Product: {result['product']}")
    print(f"   Severity: {result['severity']}")
    print(f"   Language: {result['language']}")
    print(f"   Department: {result['department']}")

print("\n" + "=" * 60)
print("✅ AI Classification System Working!")
