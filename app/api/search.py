from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Optional

from app.schemas.search import (
    SearchRequest, 
    SearchResponse, 
    SearchResultItem, 
    AvailableEnginesResponse,
    EngineInfo
)
from app.services.search_service import search_service
from app.services.search_engines import SearchResult
from app.services.cache_service import cache_service
from app.core.config import settings

router = APIRouter()


@router.get("/engines", response_model=AvailableEnginesResponse)
async def get_available_engines():
    """获取所有可用的搜索引擎"""
    engines = []
    available = search_service.available_engines
    
    engine_descriptions = {
        "google": "Google自定义搜索引擎"
        # 添加其他引擎的描述
    }
    
    for engine_name in available:
        engines.append(EngineInfo(
            name=engine_name,
            is_available=True,
            description=engine_descriptions.get(engine_name)
        ))
    
    return AvailableEnginesResponse(
        engines=engines,
        total=len(engines)
    )


@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """执行搜索查询"""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="搜索查询不能为空")
    
    # 读取请求中的缓存设置
    original_cache_setting = settings.CACHE_ENABLED
    if settings.CACHE_ENABLED and not request.use_cache:
        # 临时禁用缓存
        settings.CACHE_ENABLED = False
    
    cache_used = settings.CACHE_ENABLED
    
    # 记录缓存统计前的状态
    cache_hits_before = cache_service.stats["hits"] if cache_used else 0
    
    # 执行搜索
    try:
        search_results = await search_service.search(
            query=request.query,
            engine_name=request.engine,
            num=request.num_results,
            start=request.start_index
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索执行失败: {str(e)}")
    finally:
        # 恢复原始缓存设置
        settings.CACHE_ENABLED = original_cache_setting
    
    # 获取缓存命中信息
    cache_hits_after = cache_service.stats["hits"] if cache_used else 0
    cache_hit = cache_hits_after > cache_hits_before
    
    # 格式化结果
    formatted_results: Dict[str, List[SearchResultItem]] = {}
    total_count = 0
    cache_result_count = 0
    
    for engine_name, results in search_results.items():
        formatted_results[engine_name] = []
        for result in results:
            if result.is_from_cache:
                cache_result_count += 1
                
            formatted_results[engine_name].append(
                SearchResultItem(
                    title=result.title,
                    link=result.link,
                    snippet=result.snippet,
                    source=result.source,
                    position=result.position,
                    additional_info=result.additional_info,
                    is_from_cache=result.is_from_cache
                )
            )
        total_count += len(results)
    
    # 准备缓存信息
    cache_info = {
        "enabled": cache_used,
        "used": cache_hit,
        "cache_result_count": cache_result_count,
        "cache_result_percentage": f"{(cache_result_count / total_count * 100) if total_count > 0 else 0:.2f}%"
    }
    
    return SearchResponse(
        query=request.query,
        engines_used=list(search_results.keys()),
        total_results=total_count,
        results=formatted_results,
        metadata={
            "request_params": {
                "num_results": request.num_results,
                "start_index": request.start_index,
                "use_cache": request.use_cache
            }
        },
        cache_info=cache_info
    )


@router.get("/search", response_model=SearchResponse)
async def search_get(
    query: str = Query(..., description="搜索查询关键词"),
    engine: Optional[str] = Query(None, description="指定搜索引擎(可选)"),
    num_results: Optional[int] = Query(10, ge=1, le=50, description="返回结果数量"),
    start_index: Optional[int] = Query(1, ge=1, description="结果起始索引"),
    use_cache: bool = Query(True, description="是否使用缓存")
):
    """通过GET请求执行搜索查询"""
    request = SearchRequest(
        query=query,
        engine=engine,
        num_results=num_results,
        start_index=start_index,
        use_cache=use_cache
    )
    return await search(request) 