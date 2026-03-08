# Unified Customer Complaint Communication Dashboard

AI-powered complaint management system for banking institutions with multi-channel intake, intelligent classification, and real-time analytics.

## Features

- **Multi-Channel Intake**: WhatsApp, Voice, Email, Mobile App, Branch
- **AI-Powered Classification**: Auto-categorize complaints using Google Gemini
- **Sentiment Analysis**: Real-time emotion detection
- **Duplicate Detection**: FAISS-based semantic similarity matching
- **Priority Scoring**: Intelligent complaint prioritization
- **SLA Monitoring**: Automated breach detection and escalation
- **Real-Time Updates**: WebSocket-based live dashboard
- **Voice Transcription**: Multilingual support with Whisper
- **Root Cause Analysis**: AI-driven pattern detection
- **360° Complaint View**: Complete customer interaction history
- **AI Copilot**: Draft responses, recommendations, similar cases

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Next.js    │────▶│   FastAPI    │────▶│ PostgreSQL  │
│  Frontend   │     │  (AI Layer)  │     │  Database   │
└─────────────┘     └──────────────┘     └─────────────┘
       │                    │                     │
       │                    │                     │
       ▼                    ▼                     ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Socket.IO  │     │    Celery    │     │    Redis    │
│  (Node.js)  │     │   Workers    │     │   Cache     │
└─────────────┘     └──────────────┘     └─────────────┘
       │                    │
       │                    │
       ▼                    ▼
┌─────────────┐     ┌──────────────┐
│  WhatsApp   │     │    FAISS     │
│   Webhook   │     │  Vector DB   │
└─────────────┘     └──────────────┘
```

## Tech Stack

### Frontend
- Next.js 14 (App Router)
- Tailwind CSS + shadcn/ui
- Recharts
- Socket.IO Client
- Zustand

### Backend
- FastAPI (Python) - AI/NLP
- Node.js + Express - Webhooks/WebSocket
- PostgreSQL - Primary database
- Redis - Cache & task queue
- FAISS - Vector similarity search

### AI/ML
- Google Gemini API - Classification, summarization, drafts
- Sentence Transformers - Embeddings
- OpenAI Whisper - Speech-to-text
- Transformers - Sentiment analysis
- spaCy - NER

### Integrations
- Twilio WhatsApp Business API
- IMAP Email Polling

## Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (recommended)

### Environment Variables

Create `.env` file in project root:

```bash
# Gemini AI
GEMINI_API_KEY=your_gemini_api_key

# Twilio WhatsApp
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/complaints_db

# Redis
REDIS_URL=redis://localhost:6379

# Email IMAP
IMAP_HOST=imap.gmail.com
IMAP_PORT=993
IMAP_USER=complaints@yourbank.com
IMAP_PASSWORD=your_password

# API URLs
FASTAPI_URL=http://localhost:8000
NODE_API_URL=http://localhost:3001
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=http://localhost:3001
```

### Installation

#### Option 1: Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/shankarrrrr/customer-complaint-project.git
cd customer-complaint-project

# Start all services
docker-compose up -d

# Seed database
docker-compose exec fastapi python seed_data.py

# Access services
# Frontend: http://localhost:3000
# FastAPI: http://localhost:8000/docs
# Node.js: http://localhost:3001
```

#### Option 2: Manual Setup

**Backend (Python)**
```bash
cd backend-python
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Initialize database
python -c "from database import init_db; init_db()"

# Seed data
python seed_data.py

# Run FastAPI
uvicorn main:app --reload --port 8000

# Run Celery worker (separate terminal)
celery -A celery_worker worker --loglevel=info
```

**Backend (Node.js)**
```bash
cd backend-node
npm install
npm run dev
```

**Frontend (Next.js)**
```bash
cd frontend
npm install
npm run dev
```

## API Documentation

### FastAPI Endpoints

**Complaints**
- `POST /api/complaints/` - Create complaint
- `GET /api/complaints/` - List complaints (with filters)
- `GET /api/complaints/{id}` - Get complaint details
- `PATCH /api/complaints/{id}` - Update complaint
- `GET /api/complaints/{id}/messages` - Get messages
- `POST /api/complaints/{id}/messages` - Add message
- `POST /api/complaints/{id}/escalate` - Escalate complaint

**AI**
- `POST /api/ai/classify` - Classify text
- `POST /api/ai/sentiment` - Analyze sentiment
- `POST /api/ai/summarize` - Generate summary
- `POST /api/ai/draft` - Generate draft response
- `POST /api/ai/find-similar` - Find similar complaints

**Analytics**
- `GET /api/analytics/summary` - Dashboard KPIs
- `GET /api/analytics/trends` - Trend data
- `GET /api/analytics/sla` - SLA performance
- `GET /api/analytics/root-cause` - Root cause insights

**Voice**
- `POST /api/voice/transcribe` - Transcribe audio file

### Node.js Endpoints

- `POST /webhook/whatsapp` - Twilio WhatsApp webhook
- `POST /webhook/email` - Email complaint intake
- `GET /health` - Health check

## WhatsApp Bot Usage

Send message to configured WhatsApp number:

```
User: My ATM card is stuck in the machine
Bot: 📝 Thank you. Please provide the last 4 digits of your account number:
User: 1234
Bot: 📸 You can send a screenshot (optional) or type "skip" to continue:
User: skip
Bot: ✅ Complaint Summary
     Issue: My ATM card is stuck in the machine
     Account: XXXX1234
     Type "confirm" to submit or "cancel" to restart.
User: confirm
Bot: 🎉 Complaint Registered
     Ticket ID: CMP1042
     Category: ATM Failure
     Priority: High
     We'll resolve this within 24 hours.
```

**Commands:**
- `status CMP1042` - Check complaint status
- `help` - Show help menu
- `cancel` - Cancel current operation

## Voice Complaint

Upload audio file (mp3/wav/ogg) to `/api/voice/transcribe`:

```bash
curl -X POST http://localhost:8000/api/voice/transcribe \
  -F "file=@complaint.mp3"
```

Response includes:
- Transcript (original language)
- Detected language
- English translation
- AI classification
- Sentiment analysis

## Development

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

### Testing

```bash
# Python tests
pytest

# Node.js tests
npm test
```

## Deployment

### Production Checklist

- [ ] Set strong JWT_SECRET
- [ ] Configure production database
- [ ] Set up Redis cluster
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Set up monitoring (Sentry, DataDog)
- [ ] Configure backup strategy
- [ ] Set up CI/CD pipeline
- [ ] Enable rate limiting
- [ ] Configure CDN for frontend

## License

MIT

## Contributors

- Shankar ([@shankarrrrr](https://github.com/shankarrrrr))

## Support

For issues and questions, please open a GitHub issue.
