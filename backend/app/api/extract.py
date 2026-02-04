from fastapi import APIRouter, HTTPException
from app.services.ai_extraction import extract_medical_notes
from app.services.audit_logger import log_event

router = APIRouter()

@router.post("/extract-notes/{session_id}")
async def trigger_extraction(session_id: str):
    """
    Generates a structured medical draft from the cleaned transcript.
    """
    try:
        notes = await extract_medical_notes(session_id)

        log_event(session_id, "NOTES_GENERATED", "system", {
            "model": "llama-3.3-70b"
        })
        
        return {
            "status": "success",
            "session_id": session_id,
            "data": notes
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Transcript not found. Please transcribe and clean first.")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")