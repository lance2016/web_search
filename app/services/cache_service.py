import time
from typing import Dict, Any, Optional, Tuple, List
import hashlib
import json

from app.core.config import settings


class CacheService:
    """
    缓存服务，用于缓存搜索结果
    提供内存缓存功能，支持过期机制
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CacheService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        # 缓存存储: {缓存键: (过期时间, 缓存内容)}
        self._cache: Dict[str, Tuple[float, Any]] = {}
        # 缓存统计信息
        self._stats = {
            "hits": 0,
            "misses": 0,
            "expirations": 0
        }
    
    def _generate_key(self, query: str, engine: Optional[str], params: Dict[str, Any]) -> str:
        """
        生成缓存键
        使用查询、引擎和其他参数的组合生成唯一的缓存键
        """
        key_data = {
            "query": query,
            "engine": engine,
            "params": params
        }
        # 转换为JSON并计算哈希值
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode('utf-8')).hexdigest()
    
    def get(self, query: str, engine: Optional[str] = None, **params) -> Optional[Any]:
        """
        获取缓存内容
        
        参数:
            query: 搜索查询
            engine: 搜索引擎名称
            **params: 其他搜索参数
        
        返回:
            缓存内容，如果不存在或已过期则返回None
        """
        cache_key = self._generate_key(query, engine, params)
        
        if cache_key in self._cache:
            expire_time, content = self._cache[cache_key]
            current_time = time.time()
            
            # 检查是否过期
            if current_time < expire_time:
                self._stats["hits"] += 1
                return content
            else:
                # 删除过期内容
                del self._cache[cache_key]
                self._stats["expirations"] += 1
        
        self._stats["misses"] += 1
        return None
    
    def set(self, query: str, content: Any, ttl: int = None, engine: Optional[str] = None, **params) -> None:
        """
        设置缓存内容
        
        参数:
            query: 搜索查询
            content: 要缓存的内容
            ttl: 缓存生存时间(秒)，如果为None则使用默认值
            engine: 搜索引擎名称
            **params: 其他搜索参数
        """
        if ttl is None:
            ttl = settings.CACHE_TTL  # 从配置读取默认TTL
        
        cache_key = self._generate_key(query, engine, params)
        expire_time = time.time() + ttl
        self._cache[cache_key] = (expire_time, content)
    
    def clear(self) -> None:
        """清空所有缓存"""
        self._cache.clear()
        
    def clear_expired(self) -> int:
        """
        清除所有过期的缓存项
        
        返回:
            清除的缓存项数量
        """
        current_time = time.time()
        expired_keys = [
            key for key, (expire_time, _) in self._cache.items()
            if current_time >= expire_time
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        self._stats["expirations"] += len(expired_keys)
        return len(expired_keys)
    
    @property
    def stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total_requests) * 100 if total_requests > 0 else 0
        
        return {
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "expirations": self._stats["expirations"],
            "items_count": len(self._cache),
            "hit_rate": f"{hit_rate:.2f}%"
        }


# 创建缓存服务实例
cache_service = CacheService() 