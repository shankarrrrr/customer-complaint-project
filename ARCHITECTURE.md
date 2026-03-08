# System Architecture

## Overview

The Unified Customer Complaint Communication Dashboard is built using a microservices architecture with three main components:

1. **Frontend (Next.js)** - User interface and real-time updates
2. **Backend Python (FastAPI)** - AI/NLP processing and data management
3. **Backend Node.js (Express)** - Webhooks and WebSocket server

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND LAYER                          │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Next.js 14 (App Router)                     │  │
│  │  - Dashboard UI                                          │  │
│  │  - Complaint Management                                  │  │
│  │  - Analytics & Reports                                   │  │
│  │  - Real-time WebSocket Client                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                    │
│                            │ HTTP/WS                            │
└────────────────────────────┼────────────────────────────────────┘
                             │
        ┌────────────────────┴────────────────────┐
        │                                         │
        ▼                                         ▼
┌──────────────────┐                    ┌──────────────────┐
│  Node.js Backend │                    │  FastAPI Backend │
│                  │                    │                  │
│  - WebSocket     │◄───────────────────┤  - REST APIs     │
│  - WhatsApp      │    Event Emit      │  - AI Services   │
│  - Email Intake  │                    │  - Data Layer    │
│  - Real-time     │                    │  - Celery Tasks  │
└────────┬─────────┘                    └────────┬─────────┘
         │                                       │
         │                                       │
         ▼                                       ▼
┌──────────────────┐                    ┌──────────────────┐
│      Redis       │                    │   PostgreSQL     │
│                  │                    │                  │
│  - Cache         │                    │  - Complaints    │
│  - Task Queue    │                    │  - Customers     │
│  - Sessions      │                    │  - Agents        │
└──────────────────┘                    │  - Audit Logs    │
                                        └──────────────────┘
                                                 │
                                                 │
                                        ┌────────▼─────────┐
                                        │   FAISS Index    │
                                        │                  │
                                        │  - Embeddings    │
                                        │  - Similarity    │
                                        └──────────────────┘
```

## Component Details

### 1. Frontend (Next.js 14)

**Technology Stack:**
- Next.js 14 with App Router
- Tailwind CSS + shadcn/ui
- Recharts for data visualization
- Socket.IO client for real-time updates
- Zustand for state management
- Axios for HTTP requests

**Key Features:**
- Server-side rendering for performance
- Real-time dashboard updates
- Responsive design (mobile + desktop)
- Component-based architecture
- Type-safe API calls

**Pages:**
- `/dashboard` - Main KPI dashboard
- `/complaints` - Complaint list with filters
- `/complaints/[id]` - 360° complaint view
- `/analytics` - Advanced analytics and insights
- `/settings` - System configuration

### 2. Backend Python (FastAPI)

**Technology Stack:**
- FastAPI for REST APIs
- SQLAlchemy ORM
- PostgreSQL database
- Celery for background tasks
- Redis for caching and task queue

**AI/ML Services:**
- **Google Gemini API** - Classification, summarization, draft generation
- **Sentence Transformers** - Text embeddings (all-MiniLM-L6-v2)
- **FAISS** - Vector similarity search
- **OpenAI Whisper** - Speech-to-text (multilingual)
- **Transformers** - Sentiment analysis (DistilBERT)
- **spaCy** - Named entity recognition

**API Endpoints:**

```
Complaints:
  POST   /api/complaints/              Create complaint
  GET    /api/complaints/              List complaints (filtered)
  GET    /api/complaints/{id}          Get complaint details
  PATCH  /api/complaints/{id}          Update complaint
  GET    /api/complaints/{id}/messages Get messages
  POST   /api/complaints/{id}/messages Add message
  POST   /api/complaints/{id}/escalate Escalate complaint

AI:
  POST   /api/ai/classify              Classify text
  POST   /api/ai/sentiment             Analyze sentiment
  POST   /api/ai/summarize             Generate summary
  POST   /api/ai/draft                 Generate draft response
  POST   /api/ai/find-similar          Find similar complaints

Analytics:
  GET    /api/analytics/summary        Dashboard KPIs
  GET    /api/analytics/trends         Trend data
  GET    /api/analytics/sla            SLA performance
  GET    /api/analytics/root-cause     Root cause insights

Voice:
  POST   /api/voice/transcribe         Transcribe audio
```

**Background Tasks (Celery):**
- SLA breach monitoring (every 5 minutes)
- Root cause analysis (every hour)
- Email polling (every 60 seconds)
- Notification dispatch

### 3. Backend Node.js (Express)

**Technology Stack:**
- Express.js
- Socket.IO server
- Twilio SDK for WhatsApp
- IMAP for email intake

**Responsibilities:**
- WebSocket server for real-time updates
- WhatsApp webhook handler
- Email complaint intake
- Event broadcasting to frontend

**WebSocket Events:**
```javascript
// Emitted by server
'new_complaint'      - New complaint created
'complaint_update'   - Complaint status changed
'sla_alert'          - SLA breach warning
'new_message'        - New message in thread

// Received from client
'join_complaint'     - Subscribe to complaint updates
'leave_complaint'    - Unsubscribe from complaint
```

### 4. Database Schema

**PostgreSQL Tables:**

```sql
complaints
  - id (PK)
  - complaint_id (unique, e.g., CMP1042)
  - channel (whatsapp/voice/email/app/branch)
  - raw_text
  - customer_name, customer_phone, customer_account_last4
  - category, product, severity
  - sentiment, sentiment_score
  - priority_score
  - status (pending/in_progress/resolved/escalated)
  - assigned_agent_id (FK)
  - sla_deadline
  - created_at, updated_at
  - language, ai_summary
  - region, department
  - customer_tier, is_regulatory
  - is_duplicate, duplicate_of (FK)
  - cluster_id (FK)

complaint_messages
  - id (PK)
  - complaint_id (FK)
  - sender (customer/agent/system/bot)
  - message
  - channel
  - timestamp
  - is_read

customers
  - id (PK)
  - name, phone (unique), email
  - account_last4, account_type
  - tier (premium/standard)
  - region
  - total_complaints
  - created_at

agents
  - id (PK)
  - name, email (unique)
  - department
  - role (agent/manager/admin)
  - complaints_assigned
  - avg_resolution_time
  - created_at

complaint_clusters
  - id (PK)
  - cluster_label
  - complaint_ids (array)
  - total_count
  - region, category
  - root_cause
  - created_at

sla_configs
  - id (PK)
  - category (unique)
  - max_hours
  - escalation_threshold_hours

audit_logs
  - id (PK)
  - complaint_id (FK)
  - action
  - performed_by
  - timestamp
  - notes
```

## Data Flow

### 1. Complaint Creation Flow

```
Customer → Channel (WhatsApp/Voice/Email/App/Branch)
    ↓
Node.js Webhook / FastAPI Endpoint
    ↓
AI Classification Pipeline:
  1. Gemini API → Extract category, product, severity, language
  2. Sentiment Analysis → Detect emotion
  3. FAISS Search → Find duplicates
  4. Priority Calculation → Score 0-10
  5. Summary Generation → AI summary
    ↓
Save to PostgreSQL
    ↓
Add to FAISS Index
    ↓
Emit WebSocket Event → Frontend Updates
    ↓
Create Audit Log
```

### 2. AI Copilot Flow

```
Agent Opens Complaint Detail Page
    ↓
Frontend Requests AI Features:
  1. Draft Response → Gemini API
  2. Similar Cases → FAISS Search
  3. Recommendations → Rule Engine
    ↓
Display in Right Panel
    ↓
Agent Clicks "Use This Draft"
    ↓
Populate Reply Box
    ↓
Agent Sends Message
    ↓
Save to Database
    ↓
Emit WebSocket Event
    ↓
Customer Receives Response
```

### 3. SLA Monitoring Flow

```
Celery Worker (Every 5 minutes)
    ↓
Query Complaints WHERE status != 'resolved'
    ↓
Calculate Time Elapsed vs SLA Deadline
    ↓
If > 100%:
  - Mark as BREACHED
  - Auto-escalate to Manager
  - Emit SLA Alert Event
    ↓
If > 80%:
  - Send WARNING Notification
  - Emit Near-Breach Event
    ↓
Update Database
    ↓
Frontend Shows Red Alert
```

## Security Considerations

1. **Authentication & Authorization:**
   - JWT tokens for API authentication
   - Role-based access control (agent/manager/admin)
   - Session management via Redis

2. **Data Protection:**
   - All PII encrypted at rest
   - HTTPS/TLS for data in transit
   - Environment variables for secrets
   - No hardcoded credentials

3. **API Security:**
   - CORS configuration
   - Rate limiting
   - Input validation (Pydantic schemas)
   - SQL injection prevention (ORM)

4. **Compliance:**
   - GDPR-compliant data handling
   - Audit trail for all actions
   - Data retention policies
   - Right to be forgotten support

## Scalability

**Horizontal Scaling:**
- FastAPI: Multiple workers via Gunicorn
- Node.js: PM2 cluster mode
- Celery: Multiple workers
- PostgreSQL: Read replicas
- Redis: Redis Cluster

**Performance Optimizations:**
- Database indexing on frequently queried fields
- Redis caching for hot data
- FAISS index for fast similarity search
- Lazy loading of AI models
- Connection pooling

**Monitoring:**
- Application logs (structured JSON)
- Performance metrics (response times)
- Error tracking (Sentry integration ready)
- Database query performance
- WebSocket connection health

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Load Balancer (Nginx)                │
└────────────┬────────────────────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌─────────┐      ┌─────────┐
│ Next.js │      │ Next.js │
│ Server  │      │ Server  │
└─────────┘      └─────────┘
    │                 │
    └────────┬────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌─────────┐      ┌─────────┐
│ FastAPI │      │ FastAPI │
│ Worker  │      │ Worker  │
└─────────┘      └─────────┘
    │                 │
    └────────┬────────┘
             │
             ▼
    ┌────────────────┐
    │   PostgreSQL   │
    │   (Primary)    │
    └────────────────┘
             │
             ▼
    ┌────────────────┐
    │   PostgreSQL   │
    │   (Replica)    │
    └────────────────┘
```

## Technology Choices Rationale

1. **Next.js 14**: Server-side rendering, excellent DX, built-in optimization
2. **FastAPI**: High performance, async support, automatic API docs
3. **PostgreSQL**: ACID compliance, JSON support, mature ecosystem
4. **Redis**: Fast caching, pub/sub, task queue support
5. **Gemini API**: Cost-effective, high-quality NLP, structured output
6. **FAISS**: Fastest vector similarity search, production-ready
7. **Whisper**: Best open-source speech-to-text, multilingual
8. **Socket.IO**: Reliable WebSocket with fallbacks, easy to use

## Future Enhancements

1. **Mobile App**: React Native app for agents
2. **Advanced Analytics**: Predictive SLA breach detection
3. **Multi-tenancy**: Support multiple bank branches
4. **Chatbot**: AI-powered customer self-service
5. **Integration Hub**: Connect to CRM, ticketing systems
6. **Voice Bot**: IVR integration for automated complaint filing
7. **Blockchain**: Immutable audit trail
8. **ML Model Training**: Custom classification models
