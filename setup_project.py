import os

# Define the full directory structure and file contents
project_structure = {
    # -------------------------------------------------------------------------
    # ROOT FILES
    # -------------------------------------------------------------------------
    ".gitignore": """# Python
__pycache__/
*.py[cod]
venv/
.env

# Node
node_modules/
.next/
out/
build/
.DS_Store

# Storage
storage/audio/*
storage/transcripts/*
storage/notes/*
!storage/**/.gitkeep
""",

    ".env.example": """# Backend Configuration
AI_API_KEY=your_api_key_here
STORAGE_PATH=./storage

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
""",

    "README.md": """# Healthcare AI Notes - MVP (Phase 1)

## Project Overview
A web-based system to record audio, transcribe speech, and extract structured healthcare notes using AI.

**Phase 1 Status:** Project setup and scaffolding only.

## Setup
1. Backend:
   cd backend
   python -m venv venv
   source venv/bin/activate  # or venv\\Scripts\\activate on Windows
   pip install -r requirements.txt
   uvicorn main:app --reload

2. Frontend:
   cd frontend
   npm install
   npm run dev
""",

    # -------------------------------------------------------------------------
    # BACKEND
    # -------------------------------------------------------------------------
    "backend/requirements.txt": """fastapi==0.109.0
uvicorn==0.27.0
python-dotenv==1.0.1
pydantic==2.6.0
python-multipart==0.0.9
""",

    "backend/main.py": """import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.api import health

load_dotenv()

app = FastAPI(title="Healthcare AI Notes API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)

@app.get("/")
async def root():
    return {"message": "Healthcare AI Notes Backend is Running"}
""",

    "backend/app/api/health.py": """from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "phase": "1 (Scaffolding)",
        "service": "Healthcare AI Notes"
    }
""",

    "backend/app/services/transcription.py": """async def transcribe_audio(file_path: str) -> str:
    print(f"Phase 1 Mock: Transcribing {file_path}")
    return "This is a placeholder transcript for Phase 1."
""",

    "backend/app/services/ai_extraction.py": """def extract_medical_notes(transcript: str, prompt_template: str) -> dict:
    print("Phase 1 Mock: Extracting notes via AI")
    return {
        "patient_summary": "Placeholder patient summary",
        "key_findings": ["Placeholder finding 1", "Placeholder finding 2"]
    }
""",

    "backend/app/services/storage.py": """import os

def save_file(file_obj, destination: str) -> bool:
    try:
        print(f"Phase 1 Mock: Saving file to {destination}")
        return True
    except Exception as e:
        print(f"Error saving file: {e}")
        return False

def load_file(file_path: str):
    pass
""",

    "backend/app/models/session.py": """from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SessionCreate(BaseModel):
    clinician_id: str
    patient_id: Optional[str] = None

class SessionResponse(BaseModel):
    session_id: str
    created_at: datetime
    transcript_preview: Optional[str] = None
    status: str
""",

    "backend/app/prompts/medical_extraction.txt": """SYSTEM PROMPT PLACEHOLDER

Role: Medical Scribe
Task: Extract structured notes (SOAP format) from the provided transcript.
""",

    # -------------------------------------------------------------------------
    # FRONTEND
    # -------------------------------------------------------------------------
    "frontend/package.json": """{
  "name": "healthcare-ai-notes-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.1.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/node": "^20.11.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "typescript": "^5.3.0"
  }
}
""",

    "frontend/tsconfig.json": """{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
""",

    "frontend/next.config.js": """/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
};

module.exports = nextConfig;
""",

    "frontend/src/pages/index.tsx": """import React, { useEffect, useState } from 'react';
import RecorderPlaceholder from '@/components/RecorderPlaceholder';

export default function Home() {
  const [status, setStatus] = useState<string>('Initializing...');
  const [backendHealth, setBackendHealth] = useState<string>('Checking backend...');

  useEffect(() => {
    setStatus('Phase 1 Setup Complete');
    fetch('http://localhost:8000/health')
      .then(res => res.json())
      .then(data => setBackendHealth(`Backend: ${data.status}`))
      .catch(() => setBackendHealth('Backend: Unreachable (Is it running?)'));
  }, []);

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif', maxWidth: '800px', margin: '0 auto' }}>
      <h1>Healthcare AI Documentation</h1>
      <div style={{ margin: '20px 0', padding: '15px', background: '#f0f0f0', borderRadius: '8px' }}>
        <h3>System Status</h3>
        <p><strong>Frontend:</strong> {status}</p>
        <p><strong>API Connection:</strong> {backendHealth}</p>
      </div>
      <hr />
      <section style={{ marginTop: '30px' }}>
        <h2>Session Recording</h2>
        <RecorderPlaceholder />
      </section>
    </div>
  );
}
""",

    "frontend/src/components/RecorderPlaceholder.tsx": """import React from 'react';

const RecorderPlaceholder: React.FC = () => {
  return (
    <div style={{ 
      border: '2px dashed #ccc', 
      padding: '40px', 
      textAlign: 'center', 
      borderRadius: '10px',
      backgroundColor: '#fafafa'
    }}>
      <div style={{ fontSize: '3rem', marginBottom: '10px' }}>🎙️</div>
      <h3>Audio Recorder Placeholder</h3>
      <p>Clicking "Record" will trigger audio capture in Phase 2.</p>
      <div style={{ marginTop: '20px' }}>
        <button disabled style={{ padding: '10px 20px', fontSize: '1rem', cursor: 'not-allowed' }}>
          Start Recording (Disabled)
        </button>
      </div>
    </div>
  );
};

export default RecorderPlaceholder;
"""
}

def create_project():
    print("🚀 Starting Project Scaffolding...")
    
    # 1. Create Directories
    directories = [
        "frontend/src/pages",
        "frontend/src/components",
        "backend/app/api",
        "backend/app/services",
        "backend/app/prompts",
        "backend/app/models",
        "storage/audio",
        "storage/transcripts",
        "storage/notes"
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        # Create a .gitkeep to ensure empty storage folders are tracked if needed
        if "storage" in directory:
            with open(os.path.join(directory, ".gitkeep"), "w") as f:
                pass

    # 2. Create Files
    for path, content in project_structure.items():
        # Ensure parent directory exists (just in case)
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Created: {path}")

    print("\n🎉 Scaffolding Complete!")
    print("\nNext Steps:")
    print("1. Open two terminals.")
    print("2. Terminal 1 (Backend):")
    print("   cd backend")
    print("   python -m venv venv")
    print("   source venv/bin/activate (or venv\\Scripts\\activate on Windows)")
    print("   pip install -r requirements.txt")
    print("   uvicorn main:app --reload")
    print("\n3. Terminal 2 (Frontend):")
    print("   cd frontend")
    print("   npm install")
    print("   npm run dev")

if __name__ == "__main__":
    create_project()