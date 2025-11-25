from fastapi import APIRouter

router = APIRouter()

@router.get("/core")
def core_health():
    return {
        "status": "alive",
        "service": "monitor-service",
        "message": "Core system heartbeat OK"
    }
