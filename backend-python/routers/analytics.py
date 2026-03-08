from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from database import get_db
from models import Complaint, ComplaintCluster, Agent
from datetime import datetime, timedelta
import pytz

router = APIRouter()
IST = pytz.timezone('Asia/Kolkata')

@router.get("/summary")
async def get_summary(db: Session = Depends(get_db)):
    """Get dashboard KPIs"""
    now = datetime.now(IST)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)
    
    total_today = db.query(Complaint).filter(Complaint.created_at >= today_start).count()
    total_week = db.query(Complaint).filter(Complaint.created_at >= week_start).count()
    
    pending = db.query(Complaint).filter(Complaint.status == "pending").count()
    in_progress = db.query(Complaint).filter(Complaint.status == "in_progress").count()
    resolved = db.query(Complaint).filter(Complaint.status == "resolved").count()
    escalated = db.query(Complaint).filter(Complaint.status == "escalated").count()
    
    # SLA breaches
    sla_breached = db.query(Complaint).filter(
        and_(
            Complaint.sla_deadline < now,
            Complaint.status != "resolved"
        )
    ).count()
    
    # Average resolution time (mock for now)
    avg_resolution_time = 24.5
    
    # Top category
    top_category = db.query(
        Complaint.category,
        func.count(Complaint.id).label('count')
    ).group_by(Complaint.category).order_by(func.count(Complaint.id).desc()).first()
    
    return {
        "total_today": total_today,
        "total_week": total_week,
        "pending": pending,
        "in_progress": in_progress,
        "resolved": resolved,
        "escalated": escalated,
        "sla_breached": sla_breached,
        "avg_resolution_time": avg_resolution_time,
        "top_category": top_category[0] if top_category else "N/A"
    }

@router.get("/trends")
async def get_trends(days: int = 30, db: Session = Depends(get_db)):
    """Get complaint trends over time"""
    now = datetime.now(IST)
    start_date = now - timedelta(days=days)
    
    # Daily complaint volume
    daily_counts = db.query(
        func.date(Complaint.created_at).label('date'),
        func.count(Complaint.id).label('count')
    ).filter(Complaint.created_at >= start_date).group_by(
        func.date(Complaint.created_at)
    ).all()
    
    # Category distribution
    category_dist = db.query(
        Complaint.category,
        func.count(Complaint.id).label('count')
    ).group_by(Complaint.category).all()
    
    # Channel distribution
    channel_dist = db.query(
        Complaint.channel,
        func.count(Complaint.id).label('count')
    ).group_by(Complaint.channel).all()
    
    return {
        "daily_volume": [{"date": str(d[0]), "count": d[1]} for d in daily_counts],
        "by_category": [{"category": c[0], "count": c[1]} for c in category_dist],
        "by_channel": [{"channel": c[0], "count": c[1]} for c in channel_dist]
    }

@router.get("/sla")
async def get_sla_performance(db: Session = Depends(get_db)):
    """Get SLA performance metrics"""
    now = datetime.now(IST)
    
    # SLA compliance by category
    categories = db.query(Complaint.category).distinct().all()
    sla_by_category = []
    
    for (category,) in categories:
        total = db.query(Complaint).filter(Complaint.category == category).count()
        breached = db.query(Complaint).filter(
            and_(
                Complaint.category == category,
                Complaint.sla_deadline < now,
                Complaint.status != "resolved"
            )
        ).count()
        
        compliance_rate = ((total - breached) / total * 100) if total > 0 else 100
        
        sla_by_category.append({
            "category": category,
            "total": total,
            "breached": breached,
            "compliance_rate": round(compliance_rate, 2)
        })
    
    # Near-breach complaints (>80% SLA used)
    near_breach = db.query(Complaint).filter(
        and_(
            Complaint.status != "resolved",
            Complaint.sla_deadline > now,
            Complaint.sla_deadline < now + timedelta(hours=12)
        )
    ).all()
    
    return {
        "by_category": sla_by_category,
        "near_breach_count": len(near_breach),
        "near_breach_complaints": [
            {
                "id": c.id,
                "complaint_id": c.complaint_id,
                "category": c.category,
                "sla_deadline": c.sla_deadline.isoformat()
            } for c in near_breach
        ]
    }

@router.get("/root-cause")
async def get_root_cause_insights(db: Session = Depends(get_db)):
    """Get AI-generated root cause insights"""
    clusters = db.query(ComplaintCluster).filter(
        ComplaintCluster.total_count >= 5
    ).order_by(ComplaintCluster.total_count.desc()).limit(10).all()
    
    insights = []
    for cluster in clusters:
        insights.append({
            "cluster_id": cluster.id,
            "label": cluster.cluster_label,
            "count": cluster.total_count,
            "region": cluster.region,
            "category": cluster.category,
            "root_cause": cluster.root_cause or "Analysis pending"
        })
    
    return {"insights": insights}
