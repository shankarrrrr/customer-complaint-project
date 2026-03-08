@echo off
echo ========================================
echo Customer Complaint Dashboard - Local Setup
echo ========================================
echo.

echo Step 1: Setting up Python backend...
cd backend-python
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install -q fastapi uvicorn sqlalchemy psycopg2-binary pydantic python-dotenv google-generativeai sentence-transformers faiss-cpu transformers torch spacy python-multipart aiofiles httpx celery redis

echo.
echo Step 2: Installing Node.js dependencies...
cd ..\backend-node
call npm install

cd ..\frontend
call npm install

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To run the application:
echo 1. Start PostgreSQL and Redis
echo 2. Run: python backend-python\seed_data.py
echo 3. Run: uvicorn main:app --reload (in backend-python)
echo 4. Run: npm run dev (in backend-node)
echo 5. Run: npm run dev (in frontend)
echo.
pause
