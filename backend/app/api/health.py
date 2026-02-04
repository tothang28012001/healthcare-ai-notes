from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "phase": "1 (Scaffolding)",
        "service": "Healthcare AI Notes"
    }
