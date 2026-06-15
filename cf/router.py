from fastapi import APIRouter, HTTPException
from cf.recommendation_pipeline import generate_production_payload
import time

router = APIRouter(prefix="/api/cf")

_cache = {}
CACHE_TTL = 3600

def get_payload(handle):
    now = time.time()
    if handle in _cache:
        data, fetched_at = _cache[handle]
        if now - fetched_at < CACHE_TTL:
            return data
    data = generate_production_payload(handle)
    _cache[handle] = (data, now)
    return data

@router.get("/profile/{cf_handle}")
def get_profile(cf_handle: str):
    try:
        data = get_payload(cf_handle)
        return data["mastery_endpoint_preview"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommend/{cf_handle}")
def get_recommendations(cf_handle: str):
    try:
        data = get_payload(cf_handle)
        return {
            "username": cf_handle,
            "recommendations": data["recommendations"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))