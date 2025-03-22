import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock

from app.main import app
from app.services.search_engines import SearchResult
from app.services.search_service import SearchService


@pytest.fixture
def client():
    """创建测试客户端"""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_search_service():
    """模拟搜索服务"""
    with patch("app.api.search.search_service") as mock_service:
        # 设置可用引擎
        mock_service.available_engines = ["google", "bing"]
        
        # 模拟搜索方法
        mock_search_results = {
            "google": [
                SearchResult(
                    title="Google结果1",
                    link="https://example.com/g1",
                    snippet="Google搜索结果1的摘要",
                    source="google",
                    position=1
                ),
                SearchResult(
                    title="Google结果2",
                    link="https://example.com/g2",
                    snippet="Google搜索结果2的摘要",
                    source="google",
                    position=2
                )
            ]
        }
        
        mock_service.search = AsyncMock(return_value=mock_search_results)
        yield mock_service


class TestSearchAPI:
    """搜索API测试类"""

    def test_health_check(self, client):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data

    def test_get_available_engines(self, client, mock_search_service):
        """测试获取可用搜索引擎"""
        response = client.get("/api/search/engines")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["engines"]) == 2
        assert data["engines"][0]["name"] == "google"
        assert data["engines"][1]["name"] == "bing"

    def test_search_post_valid(self, client, mock_search_service):
        """测试使用POST方法进行有效搜索"""
        request_data = {
            "query": "测试查询",
            "engine": "google",
            "num_results": 5,
            "start_index": 1
        }
        
        response = client.post("/api/search/search", json=request_data)
        assert response.status_code == 200
        data = response.json()
        
        # 验证响应
        assert data["query"] == "测试查询"
        assert data["engines_used"] == ["google"]
        assert data["total_results"] == 2
        assert len(data["results"]["google"]) == 2
        assert data["results"]["google"][0]["title"] == "Google结果1"
        
        # 验证搜索服务被正确调用
        mock_search_service.search.assert_called_once_with(
            query="测试查询",
            engine_name="google",
            num=5,
            start=1
        )

    def test_search_post_empty_query(self, client):
        """测试使用空查询进行搜索"""
        request_data = {
            "query": "",
            "engine": "google"
        }
        
        response = client.post("/api/search/search", json=request_data)
        assert response.status_code == 400
        assert "搜索查询不能为空" in response.json()["detail"]

    def test_search_post_engine_error(self, client, mock_search_service):
        """测试搜索引擎错误处理"""
        # 模拟搜索服务抛出错误
        mock_search_service.search.side_effect = ValueError("测试错误")
        
        request_data = {
            "query": "测试查询",
            "engine": "invalid_engine"
        }
        
        response = client.post("/api/search/search", json=request_data)
        assert response.status_code == 400
        assert "测试错误" in response.json()["detail"]

    def test_search_get_valid(self, client, mock_search_service):
        """测试使用GET方法进行有效搜索"""
        response = client.get("/api/search/search?query=测试查询&engine=google&num_results=5&start_index=1")
        assert response.status_code == 200
        data = response.json()
        
        # 验证响应
        assert data["query"] == "测试查询"
        assert data["engines_used"] == ["google"]
        assert data["total_results"] == 2
        
        # 验证搜索服务被正确调用
        mock_search_service.search.assert_called_once_with(
            query="测试查询",
            engine_name="google",
            num=5,
            start=1
        )

    def test_search_get_no_query(self, client):
        """测试没有查询参数的GET请求"""
        response = client.get("/api/search/search")
        assert response.status_code == 422  # FastAPI的验证错误


class TestErrorHandling:
    """错误处理测试类"""

    def test_global_exception_handler(self, client):
        """测试全局异常处理"""
        # 模拟一个会导致500错误的场景
        with patch("app.api.search.search_service.search", side_effect=Exception("未预期的错误")):
            response = client.post("/api/search/search", json={"query": "测试查询"})
            assert response.status_code == 500
            assert "搜索执行失败" in response.json()["detail"] 