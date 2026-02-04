import os
import re
from app.services.security import secure_read_json, secure_write_json # <--- SECURE IMPORTS

# Configuration
STORAGE_PATH = os.getenv("STORAGE_PATH", "./storage")
TRANSCRIPT_DIR = os.path.join(STORAGE_PATH, "transcripts")

def clean_transcript(session_id: str) -> dict:
    """
    Loads the raw transcript JSON (decrypted), cleans the text, 
    and saves it back (encrypted).
    """
    # 1. Load Raw Transcript JSON
    file_path = os.path.join(TRANSCRIPT_DIR, f"{session_id}.json")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Transcript JSON not found for session {session_id}")
        
    # --- FIX: USE SECURE READ ---
    data = secure_read_json(file_path)

    # 2. Get Raw Text
    raw_text = data.get("text", "")
    if not raw_text:
        return data

    # 3. Apply Cleaning Rules
    clean_text = raw_text
    
    # Rule A: Remove filler words
    fillers = [r"um", r"uh", r"mm-hmm", r"ahh", r"huh"]
    for filler in fillers:
        clean_text = re.sub(rf"\b{filler}\b", "", clean_text, flags=re.IGNORECASE)

    # Rule B: Specific phrase cleanup
    clean_text = re.sub(r",?\s*\byou know\b,?", "", clean_text, flags=re.IGNORECASE)
    clean_text = re.sub(r",?\s*\blike\b,\s*", " ", clean_text, flags=re.IGNORECASE)

    # Rule C: Remove repetitions
    clean_text = re.sub(r"\b(\w+)\s+\1\b", r"\1", clean_text, flags=re.IGNORECASE)

    # Rule D: Normalize whitespace
    clean_text = re.sub(r"\s+", " ", clean_text).strip()

    # Rule E: Sentence spacing
    clean_text = re.sub(r"([.?!])([A-Z])", r"\1 \2", clean_text)

    # 4. Update the Data Object
    data["cleaned_text"] = f"Doctor (Heuristic): {clean_text}"
    data["is_cleaned"] = True
    
    # 5. Overwrite the existing JSON file (Securely)
    # --- FIX: USE SECURE WRITE ---
    secure_write_json(file_path, data)

    return data