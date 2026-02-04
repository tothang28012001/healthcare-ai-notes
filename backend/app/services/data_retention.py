import os
import time
from app.services.audit_logger import log_event

STORAGE_PATH = os.getenv("STORAGE_PATH", "./storage")
IS_DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

# Retention Settings
if IS_DEMO_MODE:
    print("⚠️  DEMO MODE ACTIVE: Aggressive 15-minute cleanup enabled.")
    RETENTION_SECONDS = 15 * 60 # 15 Minutes
else:
    RETENTION_SECONDS = 24 * 60 * 60 # 24 Hours default

POLICIES = ["audio", "transcripts", "notes", "exports"]

def enforce_retention_policies():
    """
    Deletes files older than the retention limit.
    """
    cleaned_count = 0
    cutoff_time = time.time() - RETENTION_SECONDS
    
    for folder in POLICIES:
        dir_path = os.path.join(STORAGE_PATH, folder)
        if not os.path.exists(dir_path):
            continue
            
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            if not os.path.isfile(file_path): continue
                
            if os.path.getmtime(file_path) < cutoff_time:
                try:
                    os.remove(file_path)
                    cleaned_count += 1
                except Exception as e:
                    print(f"Error cleaning {filename}: {e}")

    if cleaned_count > 0:
        print(f"🧹 Cleanup: Removed {cleaned_count} expired files.")
    
    return cleaned_count