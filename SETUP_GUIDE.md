# Quick Setup Guide

## Prerequisites Check

Before starting, ensure you have:
- ✅ Python 3.11+ installed
- ✅ Node.js 18+ installed
- ✅ PostgreSQL 15+ running
- ✅ Redis 7+ running
- ✅ Git installed
- ✅ Google Gemini API key (get from https://makersuite.google.com/app/apikey)

## Quick Start (5 minutes)

### Step 1: Clone Repository

```bash
git clone https://github.com/shankarrrrr/customer-complaint-project.git
cd customer-complaint-project
```

### Step 2: Environment Setup

Create `.env` file in project root:

```bash
# Copy example and edit
cp .env.example .env

# Edit .env and add your Gemini API key
# Minimum required:
GEMINI_API_KEY=your_actual_gemini_api_key_here
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/complaints_db
REDIS_URL=redis://localhost:6379
```

### Step 3: Start with Docker (Easiest)

```bash
# Start all services
docker-compose up -d

# Wait 30 seconds for services to start, then seed database
docker-compose exec fastapi python seed_data.py

# Access the application
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### Step 4: Manual Setup (Alternative)

If you prefer running services locally:

**Terminal 1 - PostgreSQL & Redis**
```bash
# Start PostgreSQL (if not running)
# Windows: Start PostgreSQL service from Services
# Mac: brew services start postgresql
# Linux: sudo systemctl start postgresql

# Start Redis
# Windows: redis-server
# Mac: brew services start redis
# Linux: sudo systemctl start redis
```

**Terminal 2 - FastAPI Backend**
```bash
cd backend-python
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Initialize database
python -c "from database import init_db; init_db()"

# Seed data
python seed_data.py

# Run FastAPI
uvicorn main:app --reload --port 8000
```

**Terminal 3 - Celery Worker**
```bash
cd backend-python
# Activate venv (same as above)
celery -A celery_worker worker --loglevel=info
```

**Terminal 4 - Node.js Backend**
```bash
cd backend-node
npm install
npm run dev
```

**Terminal 5 - Next.js Frontend**
```bash
cd frontend
npm install
npm run dev
```

## Verify Installation

1. Open http://localhost:3000 - You should see the dashboard
2. Open http://localhost:8000/docs - You should see FastAPI Swagger docs
3. Check that you see 100 seeded complaints in the dashboard

## Common Issues & Fixes

### Issue: "Module not found" errors in Python

```bash
cd backend-python
pip install -r requirements.txt --force-reinstall
```

### Issue: Database connection error

```bash
# Check PostgreSQL is running
# Windows: Check Services
# Mac/Linux: 
sudo systemctl status postgresql

# Create database manually if needed
psql -U postgres
CREATE DATABASE complaints_db;
\q
```

### Issue: Redis connection error

```bash
# Check Redis is running
redis-cli ping
# Should return: PONG

# If not running, start it
# Windows: redis-server
# Mac: brew services start redis
# Linux: sudo systemctl start redis
```

### Issue: Port already in use

```bash
# Find and kill process using port 3000
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:3000 | xargs kill -9
```

### Issue: Gemini API errors

- Verify your API key is correct in `.env`
- Check you have API quota remaining
- Ensure no extra spaces in the API key

## Testing the System

### Test 1: Create Complaint via API

```bash
curl -X POST http://localhost:8000/api/complaints/ \
  -H "Content-Type: application/json" \
  -d '{
    "raw_text": "ATM not dispensing cash but amount debited",
    "channel": "app",
    "customer_name": "Test User",
    "customer_phone": "+919876543210",
    "customer_account_last4": "1234",
    "region": "Mumbai"
  }'
```

### Test 2: AI Classification

```bash
curl -X POST http://localhost:8000/api/ai/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "My UPI payment failed but money was deducted"}'
```

### Test 3: Voice Transcription

```bash
# Upload an audio file
curl -X POST http://localhost:8000/api/voice/transcribe \
  -F "file=@path/to/audio.mp3"
```

## Next Steps

1. **Configure WhatsApp**: Get Twilio credentials and add to `.env`
2. **Configure Email**: Add IMAP credentials for email intake
3. **Customize**: Modify categories, SLA times, regions in seed_data.py
4. **Deploy**: Follow deployment guide for production setup

## Development Tips

- FastAPI auto-reloads on code changes
- Next.js auto-reloads on code changes
- Check logs in terminal for errors
- Use `/docs` endpoint to test APIs interactively
- WebSocket connects automatically when you open the dashboard

## Getting Help

- Check logs in each terminal window
- Review README.md for detailed documentation
- Check GitHub issues: https://github.com/shankarrrrr/customer-complaint-project/issues

## Success Checklist

- [ ] All services running without errors
- [ ] Dashboard loads at http://localhost:3000
- [ ] Can see 100 seeded complaints
- [ ] Can click on a complaint and see details
- [ ] Charts are rendering on dashboard
- [ ] Analytics page shows SLA data
- [ ] No console errors in browser

If all checked, you're ready to demo! 🎉
