import os
import uuid
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from app.services.audit_logger import log_event
from app.services.security import secure_write_bytes # <--- Import Security

router = APIRouter()

STORAGE_PATH = os.getenv("STORAGE_PATH", "./storage")
AUDIO_DIR = os.path.join(STORAGE_PATH, "audio")
MAX_FILE_SIZE_MB = 20

@router.post("/upload-audio")
async def upload_audio(
    audio: UploadFile = File(...),
    consent: bool = Form(...) # <--- MANDATORY CONSENT
):
    """
    Receives audio, enforces consent, and encrypts storage.
    """
    # 1. Enforce Consent
    if not consent:
        raise HTTPException(status_code=400, detail="Patient consent is required to process audio.")

    # 2. Validation
    # FIX: Handle case where content_type might be missing (None)
    content_type = audio.content_type or ""
    
    if not content_type.startswith("audio/"):
        # Fallback: Check extension if MIME type is missing/generic
        allowed_exts = [".mp3", ".wav", ".webm", ".m4a"]
        filename = audio.filename or ""
        ext = os.path.splitext(filename)[1].lower()
        
        if ext not in allowed_exts:
            raise HTTPException(status_code=400, detail=f"Invalid file type: {content_type}. Allowed: audio/* or .mp3/.wav/.webm")

    # 3. Setup Session
    session_id = str(uuid.uuid4())
    file_extension = audio.filename.split(".")[-1] if "." in audio.filename else "wav"
    filename = f"{session_id}.{file_extension}"
    file_path = os.path.join(AUDIO_DIR, filename)
    os.makedirs(AUDIO_DIR, exist_ok=True)

    # 4. Secure Save (Read into memory -> Encrypt -> Write)
    # Note: For massive files, we'd stream-encrypt. For <20MB, memory is fine.
    try:
        content = await audio.read()
        if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large.")
        
        secure_write_bytes(file_path, content) # <--- ENCRYPTED WRITE

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Save error: {e}")

    # 5. Log Audit Event
    log_event(session_id, "AUDIO_UPLOADED", "system", {
        "consent_obtained": True,
        "encryption_enabled": True
    })

    return {
        "session_id": session_id,
        "filename": filename,
        "status": "uploaded",
        "security": "encrypted"
    }