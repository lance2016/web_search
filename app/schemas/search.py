from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, HttpUrl


class SearchResultItem(BaseModel):
    """搜索结果项模型"""
    title: str
    link: str
    snippet: str
    source: str
    position: int
    additional_info: Dict[str, Any] = Field(default_factory=dict)
    is_from_cache: bool = Field(default=False, description="结果是否来自缓存")


class SearchRequest(BaseModel):
    """搜索请求模型"""
    query: str = Field(..., description="搜索查询关键词")
    engine: Optional[str] = Field(None, description="指定搜索引擎(可选)")
    num_results: Optional[int] = Field(10, ge=1, le=50, description="返回结果数量")
    start_index: Optional[int] = Field(1, ge=1, description="结果起始索引")
    use_cache: Optional[bool] = Field(True, description="是否使用缓存(如果缓存功能已启用)")


class SearchResponse(BaseModel):
    """搜索响应模型"""
    query: str
    engines_used: List[str]
    total_results: int
    results: Dict[str, List[SearchResultItem]]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    cache_info: Dict[str, Any] = Field(default_factory=dict, description="缓存相关信息")


class EngineInfo(BaseModel):
    """搜索引擎信息模型"""
    name: str
    is_available: bool
    description: Optional[str] = None


class AvailableEnginesResponse(BaseModel):
    """可用搜索引擎响应模型"""
    engines: List[EngineInfo]
    total: int 