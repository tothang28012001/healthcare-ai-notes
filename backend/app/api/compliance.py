from fastapi import APIRouter
import os

router = APIRouter()

@router.get("/compliance/status")
async def get_compliance_status():
    """
    Returns the status of technical safeguards for audit/demo purposes.
    """
    return {
        "encryption_at_rest": True,
        "algorithm": "AES-128 (Fernet)",
        "audit_logging": True,
        "access_control": "Network-level (Localhost/VPN)",
        "human_in_the_loop": "Enforced",
        "data_retention_policy": {
            "audio": os.getenv("AUDIO_RETENTION_DAYS", "1") + " days",
            "transcripts": os.getenv("TRANSCRIPT_RETENTION_DAYS", "7") + " days"
        },
        "disclaimer": "This system provides technical safeguards but is not a substitute for organizational HIPAA/PIPEDA compliance."
    }