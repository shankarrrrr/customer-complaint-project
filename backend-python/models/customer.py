from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200))
    phone = Column(String(20), unique=True, index=True)
    email = Column(String(200), nullable=True)
    account_last4 = Column(String(4))
    account_type = Column(String(50))  # Savings/Current/Loan
    tier = Column(String(20), default="standard")  # premium/standard
    region = Column(String(100))
    total_complaints = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
