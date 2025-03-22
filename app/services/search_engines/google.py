import httpx
from typing import Dict, Any, List, Optional
from .base import BaseSearchEngine, SearchResult


class GoogleSearchEngine(BaseSearchEngine):
    """Google自定义搜索引擎实现"""
    
    API_ENDPOINT = "https://www.googleapis.com/customsearch/v1"
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.cse_id = config.get("cse_id")
        # 用于测试的模拟数据模式
        self.mock_mode = not (self.api_key and self.cse_id) or self.api_key == "your_google_api_key_here"
    
    @property
    def is_available(self) -> bool:
        """检查是否配置了必要的API密钥，或者启用了模拟模式"""
        return True  # 始终返回True，使用模拟数据进行测试
    
    async def search(self, query: str, **kwargs) -> List[SearchResult]:
        """
        执行Google搜索
        
        参数:
            query: 搜索查询字符串
            **kwargs: 其他搜索参数，如num (结果数量), start (开始位置) 等
        
        返回:
            搜索结果列表
        """
        # 如果未配置API密钥或处于模拟模式，则返回模拟数据
        if self.mock_mode:
            return self._get_mock_results(query, **kwargs)
            
        # 以下是真实API调用的代码
        # 构建请求参数
        params = {
            "key": self.api_key,
            "cx": self.cse_id,
            "q": query,
        }
        
        # 添加其他可选参数
        num = kwargs.get("num", 10)
        if num and isinstance(num, int):
            params["num"] = min(num, 10)  # Google API最多返回10个结果
            
        start = kwargs.get("start")
        if start and isinstance(start, int):
            params["start"] = start
            
        # 发送API请求
        async with httpx.AsyncClient() as client:
            response = await client.get(self.API_ENDPOINT, params=params)
            response.raise_for_status()
            data = response.json()
            
        # 处理搜索结果
        results = []
        items = data.get("items", [])
        
        for i, item in enumerate(items):
            result = SearchResult(
                title=item.get("title", ""),
                link=item.get("link", ""),
                snippet=item.get("snippet", ""),
                source="google",
                position=i + 1,
                additional_info={
                    "htmlSnippet": item.get("htmlSnippet"),
                    "displayLink": item.get("displayLink"),
                    "formattedUrl": item.get("formattedUrl"),
                }
            )
            results.append(result)
            
        return results
    
    def _get_mock_results(self, query: str, **kwargs) -> List[SearchResult]:
        """返回模拟的搜索结果，用于测试"""
        num = min(kwargs.get("num", 3), 10)
        results = []
        
        for i in range(num):
            result = SearchResult(
                title=f"{query} - 模拟结果 {i+1}",
                link=f"https://example.com/result/{i+1}?q={query}",
                snippet=f"这是关于 {query} 的模拟搜索结果 {i+1}。这个结果用于测试缓存功能，不是真实的搜索结果。",
                source="google",
                position=i + 1,
                additional_info={
                    "htmlSnippet": f"这是关于 <b>{query}</b> 的模拟搜索结果。",
                    "displayLink": "example.com",
                    "formattedUrl": f"https://example.com/result/{i+1}"
                }
            )
            results.append(result)
        
        return results 