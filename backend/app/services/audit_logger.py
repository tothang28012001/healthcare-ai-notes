import os
import json
import uuid
from datetime import datetime

# Configuration
STORAGE_PATH = os.getenv("STORAGE_PATH", "./storage")
AUDIT_DIR = os.path.join(STORAGE_PATH, "audit")

def log_event(session_id: str, event_type: str, actor: str, details: dict = None) -> None:
    """
    Appends an audit event to the session's audit log.
    Format: JSON Lines (one valid JSON object per line).
    """
    if details is None:
        details = {}

    # 1. Ensure Directory Exists
    os.makedirs(AUDIT_DIR, exist_ok=True)

    # 2. Construct Event Object
    event = {
        "event_id": str(uuid.uuid4()),
        "session_id": session_id,
        "event_type": event_type,
        "timestamp": datetime.now().isoformat(),
        "actor": actor,
        "details": details
    }

    # 3. Append to File (Immutable Log)
    log_path = os.path.join(AUDIT_DIR, f"{session_id}.jsonl")
    
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
    except Exception as e:
        print(f"❌ Critical Audit Error: Failed to log event {event_type} - {e}")