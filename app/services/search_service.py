from typing import Dict, Any, List, Optional, Type
from app.core.config import SEARCH_ENGINES, settings
from app.services.search_engines import BaseSearchEngine, SearchResult, GoogleSearchEngine
from app.services.cache_service import cache_service


class SearchService:
    """
    搜索服务，负责管理和使用不同的搜索引擎。
    设计为单例模式，以便在应用程序中共享。
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SearchService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self._engines: Dict[str, BaseSearchEngine] = {}
        self._engine_classes = {
            "google": GoogleSearchEngine
            # 在此处添加其他搜索引擎
        }
        
        # 初始化配置的搜索引擎
        self._load_engines()
    
    def _load_engines(self):
        """加载配置中启用的搜索引擎"""
        for engine_name, engine_config in SEARCH_ENGINES.items():
            if engine_config.get("is_enabled", False) and engine_name in self._engine_classes:
                engine_class = self._engine_classes[engine_name]
                engine = engine_class(engine_config.get("config", {}))
                if engine.is_available:
                    self._engines[engine_name] = engine
    
    @property
    def available_engines(self) -> List[str]:
        """获取所有可用的搜索引擎名称"""
        return list(self._engines.keys())
    
    def get_engine(self, name: str) -> Optional[BaseSearchEngine]:
        """获取指定名称的搜索引擎实例"""
        return self._engines.get(name)
    
    async def search(self, query: str, engine_name: Optional[str] = None, **kwargs) -> Dict[str, List[SearchResult]]:
        """
        使用指定搜索引擎或所有可用引擎执行搜索
        
        参数:
            query: 搜索查询
            engine_name: 指定搜索引擎名称(可选)
            **kwargs: 传递给搜索引擎的其他参数
            
        返回:
            搜索结果字典，键为引擎名称，值为搜索结果列表
        """
        results = {}
        
        # 检查是否启用缓存
        use_cache = settings.CACHE_ENABLED
        
        if engine_name:
            # 使用指定的搜索引擎
            engine = self.get_engine(engine_name)
            if not engine:
                raise ValueError(f"搜索引擎 '{engine_name}' 不可用或未配置")
            
            # 尝试从缓存获取结果
            if use_cache:
                cached_results = cache_service.get(query, engine_name, **kwargs)
                if cached_results is not None:
                    # 标记结果来自缓存
                    for result in cached_results:
                        result.is_from_cache = True
                    return {engine_name: cached_results}
            
            # 执行搜索
            engine_results = await engine.search(query, **kwargs)
            results[engine_name] = engine_results
            
            # 缓存结果
            if use_cache:
                cache_service.set(query, engine_results, engine=engine_name, **kwargs)
        else:
            # 使用所有可用的搜索引擎
            for name, engine in self._engines.items():
                try:
                    # 尝试从缓存获取结果
                    engine_results = []
                    if use_cache:
                        cached_results = cache_service.get(query, name, **kwargs)
                        if cached_results is not None:
                            # 标记结果来自缓存
                            for result in cached_results:
                                result.is_from_cache = True
                            results[name] = cached_results
                            continue
                    
                    # 执行搜索
                    engine_results = await engine.search(query, **kwargs)
                    results[name] = engine_results
                    
                    # 缓存结果
                    if use_cache:
                        cache_service.set(query, engine_results, engine=name, **kwargs)
                    
                except Exception as e:
                    # 记录错误但继续处理其他引擎
                    results[name] = []
                    print(f"搜索引擎 {name} 出错: {str(e)}")
        
        return results


# 创建搜索服务实例
search_service = SearchService() 