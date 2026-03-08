from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Complaint, ComplaintMessage, Customer, Agent, AuditLog, SLAConfig
from schemas.complaint import ComplaintCreate, ComplaintResponse, ComplaintUpdate, ComplaintMessageCreate, ComplaintMessageResponse
from services.classifier import classify_complaint
from services.sentiment import analyze_sentiment, calculate_priority_score
from services.duplicate_detector import duplicate_detector
from services.summarizer import generate_summary
from datetime import datetime, timedelta
from typing import List, Optional
import pytz

router = APIRouter()

IST = pytz.timezone('Asia/Kolkata')

def generate_complaint_id(db: Session) -> str:
    """Generate unique complaint ID in format CMP1042"""
    last_complaint = db.query(Complaint).order_by(Complaint.id.desc()).first()
    if last_complaint and last_complaint.complaint_id:
        last_num = int(last_complaint.complaint_id.replace("CMP", ""))
        new_num = last_num + 1
    else:
        new_num = 1001
    return f"CMP{new_num}"

def calculate_sla_deadline(category: str, db: Session) -> datetime:
    """Calculate SLA deadline based on category"""
    sla_config = db.query(SLAConfig).filter(SLAConfig.category == category).first()
    hours = sla_config.max_hours if sla_config else 48  # Default 48 hours
    return datetime.now(IST) + timedelta(hours=hours)

@router.post("/", response_model=ComplaintResponse)
async def create_complaint(complaint: ComplaintCreate, db: Session = Depends(get_db)):
    """Create new complaint with AI processing"""
    try:
        # Generate complaint ID
        complaint_id = generate_complaint_id(db)
        
        # AI Classification
        classification = classify_complaint(complaint.raw_text)
        
        # Sentiment Analysis
        sentiment_data = analyze_sentiment(complaint.raw_text)
        
        # Check for duplicates
        duplicates = duplicate_detector.find_duplicates(complaint.raw_text)
        is_duplicate = len(duplicates) > 0
        duplicate_of = duplicates[0]["complaint_id"] if is_duplicate else None
        
        # Get or create customer
        customer = None
        if complaint.customer_phone:
            customer = db.query(Customer).filter(Customer.phone == complaint.customer_phone).first()
            if not customer:
                customer = Customer(
                    name=complaint.customer_name or "Unknown",
                    phone=complaint.customer_phone,
                    account_last4=complaint.customer_account_last4 or "0000",
                    account_type="Savings",
                    tier="standard",
                    region=complaint.region or "Unknown"
                )
                db.add(customer)
                db.commit()
        
        # Calculate priority score
        customer_tier = customer.tier if customer else "standard"
        is_regulatory = classification.get("severity") == "Critical"
        priority_score = calculate_priority_score(
            classification["severity"],
            sentiment_data["sentiment_score"],
            customer_tier,
            is_regulatory
        )
        
        # Generate AI summary
        ai_summary = generate_summary(
            complaint.raw_text,
            classification["category"],
            classification["severity"]
        )
        
        # Calculate SLA deadline
        sla_deadline = calculate_sla_deadline(classification["category"], db)
        
        # Create complaint
        db_complaint = Complaint(
            complaint_id=complaint_id,
            channel=complaint.channel,
            raw_text=complaint.raw_text,
            customer_name=complaint.customer_name,
            customer_phone=complaint.customer_phone,
            customer_account_last4=complaint.customer_account_last4,
            category=classification["category"],
            product=classification["product"],
            severity=classification["severity"],
            sentiment=sentiment_data["sentiment"],
            sentiment_score=sentiment_data["sentiment_score"],
            priority_score=priority_score,
            status="pending",
            language=classification.get("language", "en"),
            ai_summary=ai_summary,
            region=complaint.region,
            department=classification.get("department"),
            customer_tier=customer_tier,
            is_regulatory=is_regulatory,
            is_duplicate=is_duplicate,
            duplicate_of=duplicate_of,
            sla_deadline=sla_deadline
        )
        
        db.add(db_complaint)
        db.commit()
        db.refresh(db_complaint)
        
        # Add to FAISS index
        duplicate_detector.add_complaint(db_complaint.id, complaint.raw_text)
        
        # Create initial message
        initial_message = ComplaintMessage(
            complaint_id=db_complaint.id,
            sender="customer",
            message=complaint.raw_text,
            channel=complaint.channel
        )
        db.add(initial_message)
        
        # Create audit log
        audit_log = AuditLog(
            complaint_id=db_complaint.id,
            action="created",
            performed_by="system",
            notes=f"Complaint created via {complaint.channel}"
        )
        db.add(audit_log)
        
        db.commit()
        
        return db_complaint
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating complaint: {str(e)}")

@router.get("/", response_model=List[ComplaintResponse])
async def list_complaints(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    category: Optional[str] = None,
    severity: Optional[str] = None,
    channel: Optional[str] = None,
    region: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List complaints with filters"""
    query = db.query(Complaint)
    
    if status:
        query = query.filter(Complaint.status == status)
    if category:
        query = query.filter(Complaint.category == category)
    if severity:
        query = query.filter(Complaint.severity == severity)
    if channel:
        query = query.filter(Complaint.channel == channel)
    if region:
        query = query.filter(Complaint.region == region)
    
    complaints = query.order_by(Complaint.created_at.desc()).offset(skip).limit(limit).all()
    return complaints

@router.get("/{complaint_id}", response_model=ComplaintResponse)
async def get_complaint(complaint_id: int, db: Session = Depends(get_db)):
    """Get single complaint by ID"""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint

@router.patch("/{complaint_id}", response_model=ComplaintResponse)
async def update_complaint(
    complaint_id: int,
    update: ComplaintUpdate,
    db: Session = Depends(get_db)
):
    """Update complaint status or assignment"""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    if update.status:
        old_status = complaint.status
        complaint.status = update.status
        audit_log = AuditLog(
            complaint_id=complaint_id,
            action=f"status_changed",
            performed_by="agent",
            notes=f"Status changed from {old_status} to {update.status}"
        )
        db.add(audit_log)
    
    if update.assigned_agent_id:
        complaint.assigned_agent_id = update.assigned_agent_id
        audit_log = AuditLog(
            complaint_id=complaint_id,
            action="assigned",
            performed_by="system",
            notes=f"Assigned to agent ID {update.assigned_agent_id}"
        )
        db.add(audit_log)
    
    db.commit()
    db.refresh(complaint)
    return complaint

@router.get("/{complaint_id}/messages", response_model=List[ComplaintMessageResponse])
async def get_complaint_messages(complaint_id: int, db: Session = Depends(get_db)):
    """Get all messages for a complaint"""
    messages = db.query(ComplaintMessage).filter(
        ComplaintMessage.complaint_id == complaint_id
    ).order_by(ComplaintMessage.timestamp.asc()).all()
    return messages

@router.post("/{complaint_id}/messages", response_model=ComplaintMessageResponse)
async def add_complaint_message(
    complaint_id: int,
    message: ComplaintMessageCreate,
    db: Session = Depends(get_db)
):
    """Add message to complaint thread"""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    db_message = ComplaintMessage(
        complaint_id=complaint_id,
        sender=message.sender,
        message=message.message,
        channel=message.channel
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

@router.post("/{complaint_id}/escalate")
async def escalate_complaint(complaint_id: int, db: Session = Depends(get_db)):
    """Escalate complaint to manager"""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    complaint.status = "escalated"
    complaint.severity = "Critical"
    
    audit_log = AuditLog(
        complaint_id=complaint_id,
        action="escalated",
        performed_by="system",
        notes="Complaint escalated to manager"
    )
    db.add(audit_log)
    
    db.commit()
    return {"message": "Complaint escalated successfully"}
