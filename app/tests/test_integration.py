import os
import pytest
import requests
import subprocess
import time
import signal
from fastapi.testclient import TestClient
from dotenv import load_dotenv

# 确保加载测试环境变量
load_dotenv(".env.test")

# 导入应用实例
from app.main import app

# 创建测试客户端
client = TestClient(app)


# 检查是否有有效的Google API配置
has_google_credentials = (
    os.getenv("GOOGLE_API_KEY") and 
    os.getenv("GOOGLE_CSE_ID") and
    os.getenv("GOOGLE_API_KEY") != "your_actual_google_api_key"
)


class TestAPI:
    """API集成测试"""

    def test_health_endpoint(self):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "environment" in data
        assert data["environment"] == "testing"

    def test_available_engines(self):
        """测试获取可用搜索引擎"""
        response = client.get("/api/search/engines")
        assert response.status_code == 200
        data = response.json()
        
        # 检查引擎数量
        if has_google_credentials:
            assert data["total"] >= 1
            assert any(engine["name"] == "google" for engine in data["engines"])
        else:
            # 如果没有配置Google API密钥，可能没有可用引擎
            print("警告: 没有配置Google API密钥，引擎列表可能为空")


@pytest.mark.skipif(not has_google_credentials, reason="需要有效的Google API密钥")
class TestGoogleSearch:
    """Google搜索集成测试，仅在配置了API密钥时运行"""

    def test_google_search_get(self):
        """测试GET方法搜索"""
        response = client.get("/api/search/search?query=python+fastapi&engine=google&num_results=3")
        assert response.status_code == 200
        data = response.json()
        
        # 验证基础字段
        assert data["query"] == "python fastapi"
        assert "google" in data["engines_used"]
        assert data["total_results"] > 0
        
        # 验证结果内容
        assert "google" in data["results"]
        assert len(data["results"]["google"]) > 0
        
        # 验证第一个结果的结构
        first_result = data["results"]["google"][0]
        assert "title" in first_result
        assert "link" in first_result
        assert "snippet" in first_result
        assert first_result["source"] == "google"
        
        # 验证结果内容相关性
        assert "python" in (first_result["title"].lower() + first_result["snippet"].lower())
        
    def test_google_search_post(self):
        """测试POST方法搜索"""
        request_data = {
            "query": "machine learning tutorial",
            "engine": "google",
            "num_results": 5,
            "start_index": 1
        }
        
        response = client.post("/api/search/search", json=request_data)
        assert response.status_code == 200
        data = response.json()
        
        # 验证基础字段
        assert data["query"] == "machine learning tutorial"
        assert "google" in data["engines_used"]
        assert data["total_results"] > 0
        
        # 验证结果内容
        assert "google" in data["results"]
        assert len(data["results"]["google"]) > 0
        
        # 验证搜索结果相关性
        for result in data["results"]["google"]:
            content = (result["title"] + result["snippet"]).lower()
            assert "machine learning" in content or "ml" in content or "tutorial" in content

    def test_empty_query(self):
        """测试空查询处理"""
        response = client.post("/api/search/search", json={"query": "", "engine": "google"})
        assert response.status_code == 400
        assert "搜索查询不能为空" in response.json()["detail"]

    def test_invalid_engine(self):
        """测试无效引擎处理"""
        response = client.post("/api/search/search", json={"query": "test query", "engine": "invalid_engine"})
        assert response.status_code == 400
        assert "不可用或未配置" in response.json()["detail"]


@pytest.mark.skipif(not has_google_credentials, reason="需要有效的Google API密钥")
class TestServerIntegration:
    """服务器集成测试"""
    
    server_process = None
    
    @classmethod
    def setup_class(cls):
        """启动服务器进程"""
        # 使用随机端口避免冲突
        cls.port = 8787
        cls.base_url = f"http://localhost:{cls.port}"
        
        # 启动服务器进程
        cmd = ["python", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(cls.port)]
        cls.server_process = subprocess.Popen(cmd)
        
        # 等待服务器启动
        max_retries = 5
        for i in range(max_retries):
            try:
                response = requests.get(f"{cls.base_url}/health")
                if response.status_code == 200:
                    break
            except requests.exceptions.ConnectionError:
                pass
            time.sleep(1)
    
    @classmethod
    def teardown_class(cls):
        """关闭服务器进程"""
        if cls.server_process:
            cls.server_process.send_signal(signal.SIGINT)
            cls.server_process.wait()
    
    def test_live_server_search(self):
        """测试实际运行的服务器搜索功能"""
        search_url = f"{self.base_url}/api/search/search"
        params = {
            "query": "weather forecast",
            "engine": "google",
            "num_results": 3
        }
        
        response = requests.get(search_url, params=params)
        assert response.status_code == 200
        data = response.json()
        
        assert "google" in data["results"]
        assert len(data["results"]["google"]) > 0 