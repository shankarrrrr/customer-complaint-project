# Quick Start Guide

## Your Gemini API Key is Configured! ✅

API Key: `AIzaSyDk_5VqS3_I-hSeoqIOwoy49L5mOGZb6io`

## Option 1: Docker (Recommended - Currently Running)

Docker Compose is pulling images in the background. This will take a few minutes.

Once complete, the services will start automatically:
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- FastAPI: localhost:8000
- Node.js: localhost:3001
- Next.js: localhost:3000

**Check status:**
```bash
docker ps
```

**Once running, seed the database:**
```bash
docker-compose exec fastapi python seed_data.py
```

**Access the dashboard:**
http://localhost:3000

## Option 2: Local Setup (Faster for Development)

### Prerequisites
- ✅ Python 3.11.9 (Installed)
- ✅ Node.js 22.17.1 (Installed)
- ⚠️ PostgreSQL (Need to install/start)
- ⚠️ Redis (Need to install/start)

### Quick Local Setup

**1. Install PostgreSQL:**
```bash
# Download from: https://www.postgresql.org/download/windows/
# Or use Chocolatey:
choco install postgresql

# Start PostgreSQL service
# Check Windows Services or run:
net start postgresql-x64-15
```

**2. Install Redis:**
```bash
# Download from: https://github.com/microsoftarchive/redis/releases
# Or use Chocolatey:
choco install redis-64

# Start Redis
redis-server
```

**3. Create Database:**
```bash
# Open psql
psql -U postgres

# Create database
CREATE DATABASE complaints_db;
\q
```

**4. Install Python Dependencies:**
```bash
cd backend-python
python -m venv venv
venv\Scripts\activate
pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic python-dotenv google-generativeai
```

**5. Initialize Database & Seed Data:**
```bash
# Still in backend-python with venv activated
python -c "from database import init_db; init_db()"
python seed_data.py
```

**6. Start FastAPI Backend:**
```bash
# In backend-python
uvicorn main:app --reload --port 8000
```

**7. Start Node.js Backend (New Terminal):**
```bash
cd backend-node
npm install
npm run dev
```

**8. Start Frontend (New Terminal):**
```bash
cd frontend
npm install
npm run dev
```

**9. Open Dashboard:**
http://localhost:3000

## Option 3: Minimal Demo (No Database)

If you just want to test the AI features without full setup:

```bash
cd backend-python
python -m venv venv
venv\Scripts\activate
pip install fastapi uvicorn google-generativeai pydantic python-dotenv

# Create a test file
```

Create `test_ai.py`:
```python
import os
os.environ['GEMINI_API_KEY'] = 'AIzaSyDk_5VqS3_I-hSeoqIOwoy49L5mOGZb6io'

from services.classifier import classify_complaint

text = "My ATM card is stuck in the machine and money was debited"
result = classify_complaint(text)
print("Classification Result:")
print(result)
```

Run:
```bash
python test_ai.py
```

## Troubleshooting

### Docker is slow
- Docker is downloading ~500MB of images
- First time setup takes 5-10 minutes
- Check progress: `docker-compose logs -f`

### Port already in use
```bash
# Find process using port 3000
netstat -ano | findstr :3000
# Kill it
taskkill /PID <PID> /F
```

### PostgreSQL connection error
- Ensure PostgreSQL is running
- Check connection string in .env
- Default: `postgresql://postgres:postgres@localhost:5432/complaints_db`

### Redis connection error
- Ensure Redis is running
- Check: `redis-cli ping` (should return PONG)

## What's Next?

Once the system is running:

1. **Dashboard**: http://localhost:3000 - See 100 seeded complaints
2. **API Docs**: http://localhost:8000/docs - Test APIs interactively
3. **Test AI Classification**: 
   ```bash
   curl -X POST http://localhost:8000/api/ai/classify \
     -H "Content-Type: application/json" \
     -d '{"text": "UPI payment failed but money deducted"}'
   ```

## Current Status

✅ Gemini API Key configured  
✅ Environment files created  
✅ Python 3.11.9 detected  
✅ Node.js 22.17.1 detected  
🔄 Docker Compose pulling images...  

**Estimated time to ready**: 5-10 minutes (Docker) or 15 minutes (Local setup)
