from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ComplaintBase(BaseModel):
    raw_text: str
    channel: str
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_account_last4: Optional[str] = None
    region: Optional[str] = None
    language: Optional[str] = "en"

class ComplaintCreate(ComplaintBase):
    pass

class ComplaintUpdate(BaseModel):
    status: Optional[str] = None
    assigned_agent_id: Optional[int] = None
    category: Optional[str] = None
    severity: Optional[str] = None

class ComplaintMessageCreate(BaseModel):
    sender: str
    message: str
    channel: str

class ComplaintMessageResponse(BaseModel):
    id: int
    complaint_id: int
    sender: str
    message: str
    channel: str
    timestamp: datetime
    is_read: bool
    
    class Config:
        from_attributes = True

class ComplaintResponse(BaseModel):
    id: int
    complaint_id: str
    channel: str
    raw_text: str
    customer_name: Optional[str]
    customer_phone: Optional[str]
    category: Optional[str]
    product: Optional[str]
    severity: Optional[str]
    sentiment: Optional[str]
    sentiment_score: Optional[float]
    priority_score: Optional[float]
    status: str
    assigned_agent_id: Optional[int]
    sla_deadline: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    language: Optional[str]
    ai_summary: Optional[str]
    region: Optional[str]
    department: Optional[str]
    is_duplicate: bool
    
    class Config:
        from_attributes = True

class AIClassificationResponse(BaseModel):
    category: str
    product: str
    severity: str
    language: str
    department: str

class DraftResponseModel(BaseModel):
    short_version: str
    long_version: str
