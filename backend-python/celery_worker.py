from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv
from database import SessionLocal
from models import Complaint, ComplaintCluster
from services.root_cause import analyze_root_cause
from datetime import datetime, timedelta
import pytz

load_dotenv()

# Initialize Celery
celery_app = Celery(
    'complaint_worker',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Kolkata',
    enable_utc=True,
)

IST = pytz.timezone('Asia/Kolkata')

@celery_app.task(name='check_sla_breaches')
def check_sla_breaches():
    """
    Check for SLA breaches and near-breaches
    Runs every 5 minutes
    """
    db = SessionLocal()
    try:
        now = datetime.now(IST)
        
        # Find breached complaints
        breached = db.query(Complaint).filter(
            Complaint.sla_deadline < now,
            Complaint.status.in_(['pending', 'in_progress'])
        ).all()
        
        for complaint in breached:
            if complaint.status != 'escalated':
                complaint.status = 'escalated'
                print(f"⚠️ SLA BREACH: {complaint.complaint_id} - Auto-escalated")
        
        # Find near-breach (>80% SLA used)
        warning_threshold = now + timedelta(hours=12)
        near_breach = db.query(Complaint).filter(
            Complaint.sla_deadline < warning_threshold,
            Complaint.sla_deadline > now,
            Complaint.status.in_(['pending', 'in_progress'])
        ).all()
        
        for complaint in near_breach:
            print(f"⚠️ SLA WARNING: {complaint.complaint_id} - {complaint.sla_deadline}")
        
        db.commit()
        
        return {
            "breached": len(breached),
            "near_breach": len(near_breach),
            "timestamp": now.isoformat()
        }
        
    except Exception as e:
        db.rollback()
        print(f"Error in SLA check: {e}")
        return {"error": str(e)}
    finally:
        db.close()

@celery_app.task(name='run_root_cause_analysis')
def run_root_cause_analysis():
    """
    Analyze complaint clusters for root causes
    Runs every hour
    """
    db = SessionLocal()
    try:
        # Find clusters with 10+ complaints in last 24 hours
        yesterday = datetime.now(IST) - timedelta(hours=24)
        
        clusters = db.query(ComplaintCluster).filter(
            ComplaintCluster.total_count >= 10,
            ComplaintCluster.created_at >= yesterday
        ).all()
        
        analyzed = 0
        for cluster in clusters:
            if not cluster.root_cause:
                # Get complaint texts from cluster
                complaints = db.query(Complaint).filter(
                    Complaint.cluster_id == cluster.id
                ).limit(20).all()
                
                complaint_texts = [c.raw_text for c in complaints]
                
                # Run AI analysis
                root_cause = analyze_root_cause(
                    complaint_texts,
                    cluster.cluster_label,
                    cluster.region
                )
                
                cluster.root_cause = root_cause
                analyzed += 1
                print(f"✅ Root cause analyzed for cluster {cluster.id}")
        
        db.commit()
        
        return {
            "clusters_analyzed": analyzed,
            "timestamp": datetime.now(IST).isoformat()
        }
        
    except Exception as e:
        db.rollback()
        print(f"Error in root cause analysis: {e}")
        return {"error": str(e)}
    finally:
        db.close()

# Celery Beat Schedule
celery_app.conf.beat_schedule = {
    'check-sla-every-5-minutes': {
        'task': 'check_sla_breaches',
        'schedule': 300.0,  # 5 minutes
    },
    'root-cause-analysis-hourly': {
        'task': 'run_root_cause_analysis',
        'schedule': 3600.0,  # 1 hour
    },
}

if __name__ == '__main__':
    celery_app.start()
