from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200))
    email = Column(String(200), unique=True, index=True)
    department = Column(String(100))
    role = Column(String(50))  # agent/manager/admin
    complaints_assigned = Column(Integer, default=0)
    avg_resolution_time = Column(Float, default=0.0)  # in hours
    created_at = Column(DateTime, default=datetime.utcnow)
    
    complaints = relationship("Complaint", back_populates="agent")
