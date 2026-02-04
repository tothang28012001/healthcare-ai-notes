import os
import json
import glob
from datetime import datetime
from groq import Groq
from app.services.audit_logger import log_event
from app.services.security import secure_read_bytes  # <--- NEW IMPORT

# Configuration
STORAGE_PATH = os.getenv("STORAGE_PATH", "./storage")
AUDIO_DIR = os.path.join(STORAGE_PATH, "audio")
TRANSCRIPT_DIR = os.path.join(STORAGE_PATH, "transcripts")

# Initialize Groq Client
client = Groq(api_key=os.environ.get("AI_API_KEY"))

async def transcribe_audio(session_id: str) -> dict:
    """
    Locates encrypted audio for the session, decrypts it in memory,
    transcribes it using Whisper, and saves the result.
    """
    # 1. Find the audio file (we don't know the extension yet)
    search_pattern = os.path.join(AUDIO_DIR, f"{session_id}.*")
    files = glob.glob(search_pattern)
    
    if not files:
        raise FileNotFoundError(f"No audio file found for session {session_id}")
    
    audio_file_path = files[0]
    filename = os.path.basename(audio_file_path)

    # 2. Call Groq Whisper API
    try:
        print(f"🎤 Decrypting & Sending {filename} to Groq Whisper...")
        
        # --- FIX: DECRYPT BEFORE SENDING ---
        # We read the encrypted file into memory and decrypt it
        decrypted_audio_bytes = secure_read_bytes(audio_file_path)

        # We pass the decrypted bytes directly to the API
        transcription = client.audio.transcriptions.create(
            file=(filename, decrypted_audio_bytes), # (filename, file_content_bytes)
            model="whisper-large-v3",
            response_format="json",
            language="en",
            temperature=0.0
        )
        
        transcript_text = transcription.text

    except Exception as e:
        print(f"❌ Groq API Error: {e}")
        raise RuntimeError(f"Transcription failed: {str(e)}")

    # 3. Construct Transcript Object
    transcript_data = {
        "session_id": session_id,
        "text": transcript_text,
        "language": "en",
        "created_at": datetime.now().isoformat(),
        "status": "completed",
        "model": "whisper-large-v3"
    }

    # 4. Save to Storage (Securely)
    # Note: Transcripts contain PHI, so we should encrypt them too if we want full security.
    # But for Phase 9, we updated 'upload' and 'notes', let's ensure transcripts use secure save if possible.
    # For now, we use standard JSON dump to match previous phases, 
    # OR you can use secure_write_json if you updated that everywhere.
    # To keep it simple and working with Phase 3 code:
    
    from app.services.security import secure_write_json
    
    os.makedirs(TRANSCRIPT_DIR, exist_ok=True)
    save_path = os.path.join(TRANSCRIPT_DIR, f"{session_id}.json")
    
    secure_write_json(save_path, transcript_data) # Encrypted Save
    
    return transcript_data