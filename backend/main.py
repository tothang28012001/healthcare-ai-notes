import os
import time
from pathlib import Path
from dotenv import load_dotenv

# 1. Load Environment
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# --- HARDENING: CHECK CRITICAL CONFIG ---
if not os.getenv("STORAGE_ENCRYPTION_KEY"):
    print("❌ FATAL: STORAGE_ENCRYPTION_KEY is missing.")
    print("   Run: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'")
    exit(1)
if not os.getenv("AI_API_KEY"):
    print("❌ FATAL: AI_API_KEY is missing.")
    exit(1)

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

# Import Routers
from app.api import health, upload, transcription, clean, extract, notes, export, audit, compliance
from app.services.data_retention import enforce_retention_policies

app = FastAPI(title="Healthcare AI Notes API")

# --- HARDENING: RATE LIMITING (Memory-based) ---
# Very basic denial-of-service protection
request_counts = {}

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    now = int(time.time())
    
    # Key: IP_timestamp (1 second window)
    key = f"{client_ip}_{now}"
    request_counts[key] = request_counts.get(key, 0) + 1
    
    if request_counts[key] > 20: # Max 20 req/sec per IP
        return Response(content="Rate limit exceeded", status_code=429)
    
    # Cleanup old keys occasionally (simplified)
    if len(request_counts) > 1000:
        request_counts.clear()
        
    response = await call_next(request)
    return response

# Configure CORS (Restrictive)
app.add_middleware(
    CORSMiddleware,
    # Allow ANY URL ending in .vercel.app
    allow_origin_regex="https://.*\.vercel\.app", 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(health.router)
app.include_router(upload.router)
app.include_router(transcription.router)
app.include_router(clean.router)
app.include_router(extract.router)
app.include_router(notes.router)
app.include_router(export.router)
app.include_router(audit.router)
app.include_router(compliance.router) # <--- Compliance Status

@app.on_event("startup")
async def startup_event():
    # Trigger retention policy on startup
    cleaned = enforce_retention_policies()
    print(f"🔒 Security: Encryption enabled.")
    print(f"🧹 Retention: Cleaned {cleaned} expired files.")

@app.get("/")
async def root():
    return {"message": "Healthcare AI Notes Backend is Running"}