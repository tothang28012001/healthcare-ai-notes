from fastapi import APIRouter, HTTPException
from app.services.transcript_cleaner import clean_transcript
from app.services.audit_logger import log_event

router = APIRouter()

@router.post("/clean-transcript/{session_id}")
async def trigger_cleaning(session_id: str):
    """
    Triggers cleaning. 
    Updates the existing {session_id}.json file with a 'cleaned_text' field.
    Returns the FULL data object so you can verify the results immediately.
    """
    try:
        updated_data = clean_transcript(session_id)
        log_event(session_id, "TRANSCRIPT_CLEANED", "system")
        
        return {
            "status": "success",
            "session_id": session_id,
            "data": updated_data  # <--- Now returns the FULL content, no truncation
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Transcript not found.")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleaning failed: {str(e)}")