from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.services.transcription import transcribe_audio
from app.services.audit_logger import log_event

router = APIRouter()

@router.post("/transcribe/{session_id}")
async def trigger_transcription(session_id: str):
    """
    Triggers speech-to-text for a specific session.
    """
    try:
        # Call the service
        result = await transcribe_audio(session_id)
        log_event(session_id, "TRANSCRIPTION_COMPLETED", "system", {
            "model": result.get("model", "whisper")
        })
        
        return {
            "status": "success",
            "data": result
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Audio file not found. Please upload first.")
    
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")