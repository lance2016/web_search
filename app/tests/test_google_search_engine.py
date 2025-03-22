import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.search_engines.google import GoogleSearchEngine
from app.services.search_engines.base import SearchResult


@pytest.fixture
def google_config():
    """提供测试用的Google搜索引擎配置"""
    return {
        "api_key": "test_api_key",
        "cse_id": "test_cse_id"
    }


@pytest.fixture
def google_engine(google_config):
    """创建Google搜索引擎实例"""
    return GoogleSearchEngine(google_config)


class TestGoogleSearchEngine:
    """Google搜索引擎测试类"""

    def test_init(self, google_engine, google_config):
        """测试初始化"""
        assert google_engine.api_key == google_config["api_key"]
        assert google_engine.cse_id == google_config["cse_id"]
        assert google_engine.name == "google"

    def test_is_available(self, google_engine):
        """测试可用性检查"""
        assert google_engine.is_available is True

        # 测试缺少配置时
        engine_no_api_key = GoogleSearchEngine({"cse_id": "test_cse_id"})
        assert engine_no_api_key.is_available is False

        engine_no_cse_id = GoogleSearchEngine({"api_key": "test_api_key"})
        assert engine_no_cse_id.is_available is False

        engine_empty_config = GoogleSearchEngine({})
        assert engine_empty_config.is_available is False

    @pytest.mark.asyncio
    async def test_search_validation(self, google_engine):
        """测试搜索参数验证"""
        with pytest.raises(ValueError, match="Google搜索引擎未正确配置API密钥"):
            engine_no_config = GoogleSearchEngine({})
            await engine_no_config.search("test query")

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.get")
    async def test_search_success(self, mock_get, google_engine):
        """测试搜索成功场景"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {
                    "title": "测试标题1",
                    "link": "https://example.com/1",
                    "snippet": "测试摘要1",
                    "htmlSnippet": "<b>测试摘要1</b>",
                    "displayLink": "example.com",
                    "formattedUrl": "https://example.com/1"
                },
                {
                    "title": "测试标题2",
                    "link": "https://example.com/2",
                    "snippet": "测试摘要2",
                    "htmlSnippet": "<b>测试摘要2</b>",
                    "displayLink": "example.com",
                    "formattedUrl": "https://example.com/2"
                }
            ]
        }
        
        mock_get.return_value = mock_response

        # 执行搜索
        results = await google_engine.search("测试查询", num=2)

        # 验证结果
        assert len(results) == 2
        assert isinstance(results[0], SearchResult)
        assert results[0].title == "测试标题1"
        assert results[0].link == "https://example.com/1"
        assert results[0].snippet == "测试摘要1"
        assert results[0].source == "google"
        assert results[0].position == 1
        
        # 验证API调用参数
        mock_get.assert_called_once()
        call_args = mock_get.call_args[1]
        assert call_args["params"]["key"] == "test_api_key"
        assert call_args["params"]["cx"] == "test_cse_id"
        assert call_args["params"]["q"] == "测试查询"
        assert call_args["params"]["num"] == 2

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.get")
    async def test_search_no_results(self, mock_get, google_engine):
        """测试没有搜索结果的情况"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {}  # 没有items字段
        
        mock_get.return_value = mock_response

        # 执行搜索
        results = await google_engine.search("无结果查询")

        # 验证结果
        assert len(results) == 0

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.get")
    async def test_search_with_parameters(self, mock_get, google_engine):
        """测试带有额外参数的搜索"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"items": []}
        
        mock_get.return_value = mock_response

        # 执行搜索
        await google_engine.search("测试查询", num=5, start=11)

        # 验证API调用参数
        mock_get.assert_called_once()
        call_args = mock_get.call_args[1]
        assert call_args["params"]["num"] == 5
        assert call_args["params"]["start"] == 11 