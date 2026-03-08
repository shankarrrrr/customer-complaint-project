# 🚀 START THE PROJECT NOW!

## ✅ Good News!

Your Gemini API key is working perfectly! I've tested it and the AI classification is functioning correctly.

## 🎯 Quick Start (Choose One Option)

### Option 1: Use Existing PostgreSQL (FASTEST - 5 minutes)

I detected you already have PostgreSQL running on port 5432. Let's use it!

**Step 1: Create the database**
```bash
# Open a new terminal and run:
psql -U postgres -h localhost

# In psql, run:
CREATE DATABASE complaints_db;
\q
```

**Step 2: Install Python dependencies**
```bash
cd backend-python
python -m venv venv
venv\Scripts\activate
pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic python-dotenv google-generativeai sentence-transformers faiss-cpu celery redis
```

**Step 3: Initialize database and seed data**
```bash
# Still in backend-python with venv activated
python -c "from database import init_db; init_db()"
python seed_data.py
```

**Step 4: Start FastAPI (Terminal 1)**
```bash
cd backend-python
venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

**Step 5: Start Node.js backend (Terminal 2)**
```bash
cd backend-node
npm install
npm run dev
```

**Step 6: Start Frontend (Terminal 3)**
```bash
cd frontend
npm install
npm run dev
```

**Step 7: Open your browser**
```
http://localhost:3000
```

### Option 2: Wait for Docker (10-15 minutes)

Docker Compose is currently building images. Once complete:

```bash
# Check if containers are running
docker ps

# Seed the database
docker-compose exec fastapi python seed_data.py

# Access dashboard
open http://localhost:3000
```

## 🧪 Test AI Features Right Now!

You can test the AI classification immediately:

```bash
python test_classification.py
```

This will show you:
- ✅ ATM Failure detection
- ✅ UPI Failure classification
- ✅ Mobile App issues
- ✅ Loan complaints
- ✅ Automatic severity assignment
- ✅ Department routing

## 📊 What You'll See

Once running, you'll have:

1. **Dashboard** (http://localhost:3000)
   - 100 seeded complaints
   - Real-time KPI cards
   - Interactive charts
   - Channel distribution

2. **Complaints List** (/complaints)
   - Searchable table
   - Color-coded sentiment
   - Priority scores
   - Status filters

3. **360° Complaint View** (/complaints/[id])
   - Customer information
   - Communication timeline
   - AI Copilot with:
     - Auto-generated summary
     - Draft responses (short & long)
     - Similar past cases
     - Recommended actions

4. **Analytics** (/analytics)
   - SLA performance
   - Root cause insights
   - Near-breach alerts

5. **API Documentation** (http://localhost:8000/docs)
   - Interactive API testing
   - All endpoints documented
   - Try AI classification live

## 🔧 Troubleshooting

### PostgreSQL Connection Error
```bash
# Check if PostgreSQL is running
psql -U postgres -h localhost

# If password error, update .env:
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/complaints_db
```

### Port 3000 Already in Use
```bash
# Find and kill the process
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### Redis Not Running
```bash
# Install Redis (if not installed)
# Download from: https://github.com/microsoftarchive/redis/releases

# Start Redis
redis-server

# Or skip Redis for now - the app will work without real-time features
```

## 📝 Current Status

✅ Gemini API Key: WORKING  
✅ AI Classification: TESTED & WORKING  
✅ Python 3.11.9: INSTALLED  
✅ Node.js 22.17.1: INSTALLED  
✅ PostgreSQL: DETECTED (port 5432)  
🔄 Docker: Building images...  

## 🎬 Next Steps

1. Choose Option 1 (fastest) or wait for Docker
2. Follow the steps above
3. Open http://localhost:3000
4. See 100 complaints with AI classification
5. Click on any complaint to see the AI Copilot in action!

## 💡 Pro Tips

- The AI classification happens automatically for every new complaint
- Try creating a new complaint via API to see real-time updates
- Check the API docs at /docs to test endpoints interactively
- All AI features work offline after initial model download

## 🆘 Need Help?

If you encounter any issues:
1. Check the terminal output for error messages
2. Verify all services are running (FastAPI, Node.js, Frontend)
3. Ensure PostgreSQL is accessible
4. Check that port 8000, 3000, and 3001 are available

**Ready to start? Pick Option 1 above and let's go! 🚀**
