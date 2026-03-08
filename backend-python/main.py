from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routers import complaints, ai, analytics, voice
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Customer Complaint API",
    description="AI-powered complaint management system",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
async def startup_event():
    init_db()
    print("✅ Database initialized")

# Include routers
app.include_router(complaints.router, prefix="/api/complaints", tags=["Complaints"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(voice.router, prefix="/api/voice", tags=["Voice"])

@app.get("/")
async def root():
    return {
        "message": "Customer Complaint API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
