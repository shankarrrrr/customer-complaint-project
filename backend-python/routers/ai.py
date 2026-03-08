from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.classifier import classify_complaint
from services.sentiment import analyze_sentiment
from services.summarizer import generate_summary
from services.draft_generator import generate_draft_response
from services.duplicate_detector import duplicate_detector

router = APIRouter()

class TextInput(BaseModel):
    text: str

class ClassifyRequest(BaseModel):
    text: str

class DraftRequest(BaseModel):
    complaint_text: str
    category: str
    customer_name: str = "Customer"

class SummarizeRequest(BaseModel):
    text: str
    category: str = None
    severity: str = None

@router.post("/classify")
async def classify_text(request: ClassifyRequest):
    """Classify complaint text using AI"""
    try:
        result = classify_complaint(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sentiment")
async def analyze_sentiment_endpoint(request: TextInput):
    """Analyze sentiment of text"""
    try:
        result = analyze_sentiment(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/summarize")
async def summarize_text(request: SummarizeRequest):
    """Generate AI summary"""
    try:
        summary = generate_summary(request.text, request.category, request.severity)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/draft")
async def generate_draft(request: DraftRequest):
    """Generate draft response"""
    try:
        draft = generate_draft_response(
            request.complaint_text,
            request.category,
            request.customer_name
        )
        return draft
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/find-similar")
async def find_similar_complaints(request: TextInput):
    """Find similar complaints using FAISS"""
    try:
        duplicates = duplicate_detector.find_duplicates(request.text)
        return {"similar_complaints": duplicates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
