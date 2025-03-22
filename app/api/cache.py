from fastapi import APIRouter, HTTPException, Response
from typing import Dict, Any

from app.services.cache_service import cache_service
from app.core.config import settings

router = APIRouter()


@router.get("/stats")
async def get_cache_stats() -> Dict[str, Any]:
    """获取缓存统计信息"""
    if not settings.CACHE_ENABLED:
        return {"status": "disabled", "message": "缓存功能已禁用"}
    
    return {
        "status": "enabled",
        "stats": cache_service.stats
    }


@router.post("/clear")
async def clear_cache() -> Dict[str, Any]:
    """清空缓存"""
    if not settings.CACHE_ENABLED:
        raise HTTPException(status_code=400, detail="缓存功能已禁用")
    
    cache_service.clear()
    return {"status": "success", "message": "缓存已清空"}


@router.post("/clear-expired")
async def clear_expired_cache() -> Dict[str, Any]:
    """清除过期缓存"""
    if not settings.CACHE_ENABLED:
        raise HTTPException(status_code=400, detail="缓存功能已禁用")
    
    cleared_count = cache_service.clear_expired()
    return {
        "status": "success", 
        "message": f"已清除 {cleared_count} 个过期缓存项", 
        "cleared_count": cleared_count
    } 