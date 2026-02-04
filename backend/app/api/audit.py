import os
import json
from fastapi import APIRouter, HTTPException

router = APIRouter()

STORAGE_PATH = os.getenv("STORAGE_PATH", "./storage")
AUDIT_DIR = os.path.join(STORAGE_PATH, "audit")

@router.get("/audit/{session_id}")
async def get_audit_log(session_id: str):
    """
    Retrieves the full audit history for a specific session.
    Reads the .jsonl file line by line.
    """
    log_path = os.path.join(AUDIT_DIR, f"{session_id}.jsonl")
    
    if not os.path.exists(log_path):
        return {"session_id": session_id, "events": []}

    events = []
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    events.append(json.loads(line))
        
        return {
            "session_id": session_id,
            "events": events
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read audit log: {str(e)}")