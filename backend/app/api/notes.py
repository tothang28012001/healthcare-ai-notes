import os
import shutil # Still needed for path operations, though backup logic changes
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.audit_logger import log_event
from app.services.security import secure_read_json, secure_write_json # <--- SECURE WRAPPERS
import glob

router = APIRouter()

STORAGE_PATH = os.getenv("STORAGE_PATH", "./storage")
NOTES_DIR = os.path.join(STORAGE_PATH, "notes")

class NoteUpdate(BaseModel):
    chief_complaint: Optional[str] = None
    symptoms: Optional[List[str]] = []
    duration: Optional[str] = None
    medical_history: Optional[List[str]] = []
    medications_mentioned: Optional[List[str]] = []
    assessment: Optional[str] = None
    plan: Optional[List[str]] = []
    follow_up: Optional[str] = None

@router.get("/notes/{session_id}")
async def get_note(session_id: str):
    file_path = os.path.join(NOTES_DIR, f"{session_id}.json")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Note not found")
    try:
        # Decrypt on read
        data = secure_read_json(file_path) # <--- SECURE READ
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/notes/{session_id}")
async def update_note(session_id: str, updates: NoteUpdate):
    """
    Updates note content AND creates a version history backup.
    """
    file_path = os.path.join(NOTES_DIR, f"{session_id}.json")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Note not found")

    try:
        # 1. Secure Read
        current_data = secure_read_json(file_path) # <--- SECURE READ

        if current_data.get("status") == "approved":
            raise HTTPException(status_code=400, detail="Cannot edit approved notes.")

        # 2. Handle Versioning (Backup current state)
        # For encryption, we can't just shutil.copy() if we want the backup to be secure too (it already is if source is), 
        # but logically it's cleaner to read -> write backup.
        current_version = current_data.get("version", 1)
        backup_filename = f"{session_id}_v{current_version}.json"
        backup_path = os.path.join(NOTES_DIR, backup_filename)
        
        # Write encrypted backup
        secure_write_json(backup_path, current_data) # <--- SECURE BACKUP

        # 3. Prepare New Data
        update_data = updates.model_dump(exclude_unset=True)
        current_data.update(update_data)
        
        # Increment version
        new_version = current_version + 1
        current_data["version"] = new_version
        current_data["updated_at"] = datetime.now().isoformat()

        # 4. Secure Write
        secure_write_json(file_path, current_data) # <--- SECURE WRITE

        # 5. Log Audit Event
        log_event(session_id, "NOTES_EDITED", "human", {
            "previous_version": current_version,
            "new_version": new_version,
            "fields_changed": list(update_data.keys())
        })

        return {"status": "success", "data": current_data}

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/notes/{session_id}/approve")
async def approve_note(session_id: str):
    file_path = os.path.join(NOTES_DIR, f"{session_id}.json")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Note not found")

    try:
        # Secure Read
        current_data = secure_read_json(file_path) # <--- SECURE READ

        current_data["status"] = "approved"
        current_data["review_required"] = False
        current_data["approved_at"] = datetime.now().isoformat()
        current_data["updated_at"] = datetime.now().isoformat()

        # Secure Write
        secure_write_json(file_path, current_data) # <--- SECURE WRITE

        # Log Audit Event
        log_event(session_id, "NOTES_APPROVED", "human", {
            "version_approved": current_data.get("version", 1)
        })

        return {"status": "success", "data": current_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/sessions")
async def list_sessions():
    """
    Scans the notes directory and returns a summary list of all sessions.
    Used for the Frontend Dashboard.
    """
    sessions = []
    
    # Pattern to find all JSON files
    search_pattern = os.path.join(NOTES_DIR, "*.json")
    files = glob.glob(search_pattern)
    
    # Sort by modification time (newest first)
    files.sort(key=os.path.getmtime, reverse=True)
    
    for file_path in files:
        try:
            # We use secure_read_json if you have Phase 9 encryption, 
            # otherwise standard json.load
            # Assuming Phase 9 setup:
            from app.services.security import secure_read_json
            data = secure_read_json(file_path)
            
            # Create a summary object (lightweight)
            sessions.append({
                "session_id": data.get("session_id"),
                "created_at": data.get("created_at", "Unknown"),
                "chief_complaint": data.get("chief_complaint", "Unspecified"),
                "status": data.get("status", "draft"),
                "preview": f"{len(data.get('symptoms', []))} symptoms identified"
            })
        except Exception as e:
            print(f"Error reading session file {file_path}: {e}")
            continue
            
    return {"count": len(sessions), "sessions": sessions}