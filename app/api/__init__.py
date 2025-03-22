from fastapi import APIRouter
from app.api.search import router as search_router
from app.api.cache import router as cache_router

api_router = APIRouter()

api_router.include_router(search_router, prefix="/search", tags=["search"])
api_router.include_router(cache_router, prefix="/cache", tags=["cache"])

# 添加更多路由器
# api_router.include_router(other_router, prefix="/other", tags=["other"]) 