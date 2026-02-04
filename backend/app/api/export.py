import os
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse # <--- NEW IMPORT
from app.services.pdf_export import generate_pdf

router = APIRouter()

STORAGE_PATH = os.getenv("STORAGE_PATH", "./storage")
EXPORTS_DIR = os.path.join(STORAGE_PATH, "exports")

@router.post("/export/{session_id}")
async def export_notes(session_id: str):
    """
    Generates the PDF and saves it to the server.
    """
    try:
        file_path = generate_pdf(session_id)
        return {
            "status": "success",
            "file_path": file_path,
            "exported_at": datetime.now().isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

# --- NEW DOWNLOAD ENDPOINT ---
@router.get("/export/{session_id}/download")
async def download_pdf(session_id: str):
    """
    Streams the PDF file to the client browser.
    """
    # 1. Define the path
    filename = f"{session_id}.pdf"
    file_path = os.path.join(EXPORTS_DIR, filename)

    # 2. Check if it exists (if not, try to generate it on the fly)
    if not os.path.exists(file_path):
        try:
            # Try to generate it now
            generate_pdf(session_id)
        except Exception:
            raise HTTPException(status_code=404, detail="PDF not found. Please approve the note first.")

    # 3. Return the file stream
    return FileResponse(
        path=file_path,
        filename=f"Medical_Note_{session_id}.pdf",
        media_type='application/pdf'
    )