from sqlalchemy import Column, Integer, String, Float
from database import Base

class SLAConfig(Base):
    __tablename__ = "sla_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), unique=True, index=True)
    max_hours = Column(Float)  # Maximum hours to resolve
    escalation_threshold_hours = Column(Float)  # When to escalate
