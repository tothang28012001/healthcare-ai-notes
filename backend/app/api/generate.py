from fastapi import APIRouter, HTTPException
from app.services.ai_extraction import generate_notes

router = APIRouter()

@router.post("/generate-notes/{session_id}")
async def trigger_generation(session_id: str):
    try:
        result = generate_notes(session_id)
        return {
            "status": "success",
            "data": result
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found.")
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))