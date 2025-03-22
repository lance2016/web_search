import pytest
from unittest.mock import patch, MagicMock

from app.services.search_service import SearchService
from app.services.search_engines import BaseSearchEngine, SearchResult


class MockSearchEngine(BaseSearchEngine):
    """用于测试的搜索引擎模拟类"""
    
    def __init__(self, config, engine_name="mock", is_engine_available=True):
        # 首先保存我们自己的变量
        self._custom_name = engine_name
        self._is_available = is_engine_available
        self.search_called = False
        self.last_query = None
        self.last_kwargs = None
        
        # 然后调用父类初始化
        super().__init__(config)
        
        # 覆盖父类自动生成的_name
        self._name = self._custom_name
    
    @property
    def is_available(self):
        return self._is_available
    
    async def search(self, query, **kwargs):
        self.search_called = True
        self.last_query = query
        self.last_kwargs = kwargs
        result = SearchResult(
            title=f"Result for {query}",
            link=f"https://example.com/search?q={query}",
            snippet=f"This is a result for {query}",
            source=self.name,
            position=1
        )
        return [result]


@pytest.fixture
def mock_search_engines():
    """创建测试用的搜索引擎配置"""
    return {
        "google": {
            "is_enabled": True,
            "config": {"api_key": "test_key", "cse_id": "test_id"}
        },
        "disabled_engine": {
            "is_enabled": False,
            "config": {}
        }
    }


@pytest.fixture
def mock_engine_instances():
    """创建测试用的搜索引擎实例"""
    return {
        "google": MockSearchEngine({"api_key": "test_key", "cse_id": "test_id"}, "google"),
        "unavailable": MockSearchEngine({}, "unavailable", False)
    }


@pytest.fixture
def patch_engines(mock_search_engines, mock_engine_instances):
    """为测试打补丁"""
    with patch("app.services.search_service.SEARCH_ENGINES", mock_search_engines):
        with patch.object(SearchService, "_engine_classes") as mock_classes:
            # 设置_engine_classes，使其可以返回我们的模拟引擎
            mock_classes.__getitem__.side_effect = lambda name: lambda config: mock_engine_instances.get(name, MagicMock())
            yield


@pytest.fixture
def search_service(patch_engines):
    """创建测试用的搜索服务实例"""
    # 确保是新实例，避免测试间干扰
    SearchService._instance = None
    return SearchService()


class TestSearchService:
    """搜索服务测试类"""

    def test_singleton(self):
        """测试单例模式"""
        service1 = SearchService()
        service2 = SearchService()
        assert service1 is service2

    def test_load_engines(self, search_service, mock_search_engines):
        """测试加载搜索引擎"""
        # 只有启用的引擎应被加载
        assert "google" in search_service._engines
        assert "disabled_engine" not in search_service._engines

    def test_available_engines(self, search_service):
        """测试获取可用引擎"""
        engines = search_service.available_engines
        assert "google" in engines
        assert "unavailable" not in engines
        assert len(engines) == 1

    def test_get_engine(self, search_service, mock_engine_instances):
        """测试获取特定引擎"""
        engine = search_service.get_engine("google")
        assert engine is not None
        assert engine.name == "google"
        
        # 测试获取不存在的引擎
        engine = search_service.get_engine("non_existent")
        assert engine is None

    @pytest.mark.asyncio
    async def test_search_specific_engine(self, search_service, mock_engine_instances):
        """测试使用特定引擎搜索"""
        results = await search_service.search("测试查询", engine_name="google", num=5)
        
        # 验证结果
        assert "google" in results
        assert len(results["google"]) == 1
        assert results["google"][0].title == "Result for 测试查询"
        
        # 验证引擎被正确调用
        google_engine = mock_engine_instances["google"]
        assert google_engine.search_called
        assert google_engine.last_query == "测试查询"
        assert google_engine.last_kwargs.get("num") == 5

    @pytest.mark.asyncio
    async def test_search_invalid_engine(self, search_service):
        """测试使用无效引擎搜索"""
        with pytest.raises(ValueError, match="搜索引擎 'non_existent' 不可用或未配置"):
            await search_service.search("测试查询", engine_name="non_existent")

    @pytest.mark.asyncio
    async def test_search_all_engines(self, search_service, mock_engine_instances):
        """测试使用所有引擎搜索"""
        results = await search_service.search("测试查询")
        
        # 只有可用的引擎应返回结果
        assert "google" in results
        assert len(results) == 1  # 只有google是可用的

    @pytest.mark.asyncio
    async def test_search_engine_exception(self, search_service, mock_engine_instances):
        """测试引擎抛出异常的情况"""
        # 修改引擎使其抛出异常
        google_engine = mock_engine_instances["google"]
        google_engine.search = MagicMock(side_effect=Exception("测试异常"))
        
        # 搜索应该继续执行而不抛出异常
        results = await search_service.search("测试查询")
        
        # 结果应该为空列表而不是None
        assert "google" in results
        assert results["google"] == [] 