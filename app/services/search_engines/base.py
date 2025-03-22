from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class SearchResult:
    """搜索结果数据结构"""
    
    def __init__(
        self,
        title: str,
        link: str,
        snippet: str,
        source: str,
        position: int = 0,
        additional_info: Optional[Dict[str, Any]] = None,
        is_from_cache: bool = False
    ):
        self.title = title
        self.link = link
        self.snippet = snippet
        self.source = source  # 搜索引擎名称
        self.position = position
        self.additional_info = additional_info or {}
        self.is_from_cache = is_from_cache
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "link": self.link,
            "snippet": self.snippet,
            "source": self.source,
            "position": self.position,
            "additional_info": self.additional_info,
            "is_from_cache": self.is_from_cache
        }


class BaseSearchEngine(ABC):
    """搜索引擎基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._name = self.__class__.__name__.lower().replace("searchengine", "")
    
    @property
    def name(self) -> str:
        return self._name
    
    @abstractmethod
    async def search(self, query: str, **kwargs) -> List[SearchResult]:
        """执行搜索操作"""
        pass
    
    @property
    @abstractmethod
    def is_available(self) -> bool:
        """检查搜索引擎是否可用"""
        pass 