from database import SessionLocal, init_db
from models import Complaint, Customer, Agent, SLAConfig, ComplaintMessage
from datetime import datetime, timedelta
import random
import pytz

IST = pytz.timezone('Asia/Kolkata')

# Sample data
REGIONS = ["Mumbai", "Delhi", "Bangalore", "Pune", "Chennai", "Hyderabad", "Kolkata", "Ahmedabad"]
CATEGORIES = ["ATM Failure", "UPI Failure", "Mobile App", "Loan", "Card", "Net Banking"]
CHANNELS = ["whatsapp", "voice", "email", "app", "branch"]
STATUSES = ["pending", "in_progress", "resolved", "escalated"]
SENTIMENTS = ["Positive", "Negative", "Neutral"]

SAMPLE_COMPLAINTS = [
    "ATM at Shivajinagar branch not dispensing cash but amount debited from account",
    "UPI payment failed but money deducted. Transaction ID: UPI123456789",
    "Unable to login to mobile banking app. Getting error 'Invalid credentials'",
    "EMI not reflecting in loan account despite payment made 5 days ago",
    "Credit card blocked without any notification. Need urgent resolution",
    "Net banking session timing out every 2 minutes. Cannot complete transactions",
    "Debit card declined at merchant despite sufficient balance",
    "Loan application pending for 15 days without any update",
    "Wrong charges applied on credit card statement. Need reversal",
    "ATM card stuck in machine at MG Road branch",
]

def seed_database():
    """Seed database with realistic dummy data"""
    init_db()
    db = SessionLocal()
    
    try:
        print("🌱 Seeding database...")
        
        # Create SLA configs
        sla_configs = [
            SLAConfig(category="ATM Failure", max_hours=24, escalation_threshold_hours=18),
            SLAConfig(category="UPI Failure", max_hours=12, escalation_threshold_hours=9),
            SLAConfig(category="Mobile App", max_hours=48, escalation_threshold_hours=36),
            SLAConfig(category="Loan", max_hours=72, escalation_threshold_hours=60),
            SLAConfig(category="Card", max_hours=24, escalation_threshold_hours=18),
            SLAConfig(category="Net Banking", max_hours=48, escalation_threshold_hours=36),
        ]
        db.add_all(sla_configs)
        db.commit()
        print("✅ SLA configs created")
        
        # Create agents
        agents = [
            Agent(name="Rajesh Kumar", email="rajesh@bank.com", department="ATM Operations", role="agent"),
            Agent(name="Priya Sharma", email="priya@bank.com", department="Digital Banking", role="agent"),
            Agent(name="Amit Patel", email="amit@bank.com", department="Cards", role="agent"),
            Agent(name="Sneha Reddy", email="sneha@bank.com", department="Loans", role="agent"),
            Agent(name="Vikram Singh", email="vikram@bank.com", department="Customer Service", role="manager"),
        ]
        db.add_all(agents)
        db.commit()
        print("✅ Agents created")
        
        # Create customers
        customers = []
        for i in range(50):
            customer = Customer(
                name=f"Customer {i+1}",
                phone=f"+919{random.randint(100000000, 999999999)}",
                email=f"customer{i+1}@example.com",
                account_last4=f"{random.randint(1000, 9999)}",
                account_type=random.choice(["Savings", "Current"]),
                tier=random.choice(["premium", "standard", "standard", "standard"]),
                region=random.choice(REGIONS),
                total_complaints=0
            )
            customers.append(customer)
        db.add_all(customers)
        db.commit()
        print("✅ Customers created")
        
        # Create complaints
        complaints = []
        now = datetime.now(IST)
        
        for i in range(100):
            customer = random.choice(customers)
            category = random.choice(CATEGORIES)
            severity = random.choice(["Low", "Medium", "High", "Critical"])
            sentiment = random.choice(SENTIMENTS)
            status = random.choice(STATUSES)
            channel = random.choice(CHANNELS)
            
            # Generate realistic complaint text
            base_complaint = random.choice(SAMPLE_COMPLAINTS)
            complaint_text = f"{base_complaint} Customer: {customer.name}, Account: XXXX{customer.account_last4}"
            
            # Random creation time in last 30 days
            days_ago = random.randint(0, 30)
            created_at = now - timedelta(days=days_ago, hours=random.randint(0, 23))
            
            # SLA deadline
            sla_config = next((s for s in sla_configs if s.category == category), None)
            sla_hours = sla_config.max_hours if sla_config else 48
            sla_deadline = created_at + timedelta(hours=sla_hours)
            
            complaint = Complaint(
                complaint_id=f"CMP{1000 + i + 1}",
                channel=channel,
                raw_text=complaint_text,
                customer_name=customer.name,
                customer_phone=customer.phone,
                customer_account_last4=customer.account_last4,
                category=category,
                product=random.choice(["Debit Card", "Credit Card", "UPI", "Loan", "Savings Account"]),
                severity=severity,
                sentiment=sentiment,
                sentiment_score=random.uniform(0.3, 0.9),
                priority_score=random.uniform(3.0, 9.5),
                status=status,
                assigned_agent_id=random.choice(agents).id if status != "pending" else None,
                sla_deadline=sla_deadline,
                created_at=created_at,
                updated_at=created_at,
                language="en",
                ai_summary=f"Customer reporting {category.lower()} issue. {severity} priority.",
                region=customer.region,
                department=random.choice(["ATM Operations", "Digital Banking", "Cards", "Loans"]),
                customer_tier=customer.tier,
                is_regulatory=severity == "Critical",
                is_duplicate=False
            )
            complaints.append(complaint)
            
            customer.total_complaints += 1
        
        db.add_all(complaints)
        db.commit()
        print("✅ 100 complaints created")
        
        # Create messages for some complaints
        for complaint in random.sample(complaints, 30):
            messages = [
                ComplaintMessage(
                    complaint_id=complaint.id,
                    sender="customer",
                    message=complaint.raw_text,
                    channel=complaint.channel,
                    timestamp=complaint.created_at
                ),
                ComplaintMessage(
                    complaint_id=complaint.id,
                    sender="bot",
                    message="Thank you for contacting us. Your complaint has been registered. Ticket ID: " + complaint.complaint_id,
                    channel=complaint.channel,
                    timestamp=complaint.created_at + timedelta(minutes=1)
                )
            ]
            
            if complaint.status != "pending":
                messages.append(
                    ComplaintMessage(
                        complaint_id=complaint.id,
                        sender="agent",
                        message="We are looking into your issue. Will update you shortly.",
                        channel=complaint.channel,
                        timestamp=complaint.created_at + timedelta(hours=2)
                    )
                )
            
            db.add_all(messages)
        
        db.commit()
        print("✅ Messages created")
        
        print("🎉 Database seeding completed!")
        print(f"   - {len(customers)} customers")
        print(f"   - {len(agents)} agents")
        print(f"   - {len(complaints)} complaints")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
