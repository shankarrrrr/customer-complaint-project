from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Boolean, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from database import Base

class Complaint(Base):
    __tablename__ = "complaints"
    
    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(String(20), unique=True, index=True)  # CMP1042
    channel = Column(String(20))  # whatsapp/voice/email/app/branch
    raw_text = Column(Text)
    customer_name = Column(String(200))
    customer_phone = Column(String(20))
    customer_account_last4 = Column(String(4))
    category = Column(String(100))  # ATM Failure / UPI Failure / etc
    product = Column(String(100))  # Debit Card / Credit Card / etc
    severity = Column(String(20))  # Low / Medium / High / Critical
    sentiment = Column(String(20))  # Positive / Negative / Neutral
    sentiment_score = Column(Float)
    priority_score = Column(Float)
    status = Column(String(20), default="pending")  # pending/in_progress/resolved/escalated
    assigned_agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    sla_deadline = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    language = Column(String(20))
    ai_summary = Column(Text)
    region = Column(String(100))
    department = Column(String(100))
    customer_tier = Column(String(20))  # premium/standard
    is_regulatory = Column(Boolean, default=False)
    cluster_id = Column(Integer, ForeignKey("complaint_clusters.id"), nullable=True)
    is_duplicate = Column(Boolean, default=False)
    duplicate_of = Column(Integer, ForeignKey("complaints.id"), nullable=True)
    
    # Relationships
    messages = relationship("ComplaintMessage", back_populates="complaint", cascade="all, delete-orphan")
    agent = relationship("Agent", back_populates="complaints")
    cluster = relationship("ComplaintCluster", back_populates="complaints")
    audit_logs = relationship("AuditLog", back_populates="complaint", cascade="all, delete-orphan")


class ComplaintMessage(Base):
    __tablename__ = "complaint_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"))
    sender = Column(String(20))  # customer/agent/system/bot
    message = Column(Text)
    channel = Column(String(20))
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    
    complaint = relationship("Complaint", back_populates="messages")


class ComplaintCluster(Base):
    __tablename__ = "complaint_clusters"
    
    id = Column(Integer, primary_key=True, index=True)
    cluster_label = Column(String(200))
    complaint_ids = Column(ARRAY(Integer))
    total_count = Column(Integer, default=0)
    region = Column(String(100))
    category = Column(String(100))
    root_cause = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    complaints = relationship("Complaint", back_populates="cluster")
