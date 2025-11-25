# app/routes/health.py
from fastapi import APIRouter
import os
import httpx

router = APIRouter()

# Brat agent backend URL – lazım olsa Render hostunu buradan dəyişə bilərsən
AGENT_BACKEND_URL = os.getenv(
    "AGENT_BACKEND_URL",
    "https://brat-agent-backend.onrender.com/health",
)


@router.get("/core")
async def core_health():
    """
    Monitor servisinin öz ürək döyüntüsü.
    """
    return {
        "status": "alive",
        "service": "monitor-service",
        "message": "Sərt disk nəfəs alır, sistem ritmi sabitdir ✨",
    }


@router.get("/agents")
async def agents_health():
    """
    Xarici servis(lər) üçün ümumi health-check.
    Hazırda yalnız Brat agent backend-i yoxlayırıq.
    """
    agent_status = {
        "status": "unknown",
        "http_status": None,
        "raw": None,
        "error": None,
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get(AGENT_BACKEND_URL)
            agent_status["http_status"] = res.status_code

            # JSON gələrsə saxlayırıq
            try:
                agent_status["raw"] = res.json()
            except Exception:
                agent_status["raw"] = res.text

            if res.status_code == 200:
                agent_status["status"] = "alive"
            elif 200 < res.status_code < 500:
                agent_status["status"] = "degraded"
            else:
                agent_status["status"] = "down"

    except Exception as e:
        agent_status["status"] = "down"
        agent_status["error"] = str(e)

    overall = "alive"
    if agent_status["status"] == "degraded":
        overall = "degraded"
    if agent_status["status"] == "down":
        overall = "down"

    return {
        "status": overall,
        "service": "agent-mesh",
        "brat_agent_backend": agent_status,
    }
