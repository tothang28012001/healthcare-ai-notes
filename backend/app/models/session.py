from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SessionCreate(BaseModel):
    clinician_id: str
    patient_id: Optional[str] = None

class SessionResponse(BaseModel):
    session_id: str
    created_at: datetime
    transcript_preview: Optional[str] = None
    status: str
