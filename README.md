# Web 搜索 API

一个基于 FastAPI 实现的可扩展 Web 搜索 API 服务，支持多种搜索引擎集成。本项目采用架构师视角进行设计，确保了良好的可扩展性、可维护性和高性能。

## 功能特点

- **模块化设计**：采用清晰的目录结构和模块划分，易于扩展新的搜索引擎
- **高性能异步架构**：基于 FastAPI 和 Python 异步特性构建
- **可扩展性**：当前支持 Google Custom Search API，设计上支持轻松集成其他搜索引擎
- **智能缓存机制**：内置缓存系统，减少重复请求，提高响应速度，降低API调用成本
- **架构师友好**：遵循 SOLID 原则，采用依赖注入、工厂模式和单例模式等设计模式
- **环境变量配置**：通过环境变量进行配置，支持多环境部署
- **完整的 API 文档**：自动生成的 Swagger UI 文档，方便开发和测试

## 系统架构

项目采用分层架构设计：

```
app/
├── api/                # API 层 - 处理 HTTP 请求和响应
├── core/               # 核心层 - 配置和共享功能
├── schemas/            # 数据模型层 - 请求和响应的数据结构
└── services/           # 服务层 - 业务逻辑
    └── search_engines/ # 搜索引擎实现
```

## 系统要求

- Python 3.8+
- FastAPI 0.100.0+
- 依赖项：详见 `requirements.txt`

## 安装部署

### 环境准备

1. 克隆仓库：

```bash
git clone https://github.com/yourusername/web-search-api.git
cd web-search-api
```

2. 创建并激活虚拟环境：

```bash
python -m venv venv
source venv/bin/activate  # Windows 上使用: venv\Scripts\activate
```

3. 安装依赖：

```bash
pip install -r requirements.txt
```

### 配置

1. 创建环境变量文件：

```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，设置必要的环境变量：

```
# Google Custom Search API配置
GOOGLE_API_KEY=your_google_api_key_here  # 从 Google Cloud Console 获取
GOOGLE_CSE_ID=your_google_custom_search_engine_id_here  # 从 Google Programmable Search Engine 获取

# 应用配置
APP_ENV=development  # 环境：development, testing, production
DEBUG=True  # 开发模式设为 True，生产环境设为 False

# 缓存配置
CACHE_ENABLED=True  # 是否启用缓存功能
CACHE_TTL=3600  # 缓存生存时间(秒)，默认1小时
```

### 运行

启动开发服务器：

```bash
python run.py
```

或使用 uvicorn 直接启动：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API 文档

启动服务后，访问以下 URL 查看 API 文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API 端点

### 健康检查

```
GET /health
```

返回服务器状态和版本信息。

### 获取可用搜索引擎

```
GET /api/search/engines
```

返回所有可用的搜索引擎列表。

### 执行搜索 (POST)

```
POST /api/search/search
```

请求体示例：

```json
{
  "query": "FastAPI Python",
  "engine": "google",
  "num_results": 10,
  "start_index": 1,
  "use_cache": true
}
```

### 执行搜索 (GET)

```
GET /api/search/search?query=FastAPI+Python&engine=google&num_results=10&start_index=1&use_cache=true
```

### 缓存管理

#### 获取缓存统计信息

```
GET /api/cache/stats
```

返回缓存的使用情况和命中率等统计信息。

#### 清空缓存

```
POST /api/cache/clear
```

清空所有缓存数据。

#### 清除过期缓存

```
POST /api/cache/clear-expired
```

仅清除已过期的缓存数据。

## 验证 API

以下是一些可用于验证 API 正常工作的 curl 命令：

### 验证健康检查

```bash
curl -X GET "http://localhost:8000/health"
```

预期输出：
```json
{
  "status": "ok",
  "environment": "development",
  "version": "0.1.0"
}
```

### 获取可用搜索引擎

```bash
curl -X GET "http://localhost:8000/api/search/engines"
```

预期输出：
```json
{
  "engines": [
    {
      "name": "google",
      "is_available": true,
      "description": "Google自定义搜索引擎"
    }
  ],
  "total": 1
}
```

### 执行搜索查询

```bash
curl -X GET "http://localhost:8000/api/search/search?query=FastAPI%20Python&engine=google&num_results=5"
```

### 获取缓存统计

```bash
curl -X GET "http://localhost:8000/api/cache/stats"
```

### 清空缓存

```bash
curl -X POST "http://localhost:8000/api/cache/clear"
```

## 缓存系统

本系统实现了一个内存缓存机制，可以有效减少对外部API的重复调用，提高响应速度并降低成本。

### 缓存特性

- **自动缓存**：搜索结果会自动缓存
- **TTL机制**：支持配置缓存生存时间
- **缓存标识**：API响应中包含缓存状态，可以区分结果是来自缓存还是实时查询
- **缓存统计**：提供命中率、缓存项数量等统计信息
- **按需禁用**：可以在请求级别控制是否使用缓存

### 缓存配置

在`.env`文件中配置缓存参数：

```
CACHE_ENABLED=True  # 是否启用缓存
CACHE_TTL=3600  # 缓存生存时间(秒)
```

### 缓存控制

每个搜索请求可以控制是否使用缓存：

```json
{
  "query": "搜索词",
  "use_cache": false  // 禁用该请求的缓存
}
```

或在GET请求中：

```
GET /api/search/search?query=搜索词&use_cache=false
```

## 如何扩展

### 添加新的搜索引擎

1. 在 `app/services/search_engines` 目录下创建新的搜索引擎类：

```python
from .base import BaseSearchEngine, SearchResult

class NewSearchEngine(BaseSearchEngine):
    """新搜索引擎实现"""
    
    def __init__(self, config):
        super().__init__(config)
        # 初始化特定配置
        
    @property
    def is_available(self) -> bool:
        # 检查配置是否有效
        
    async def search(self, query, **kwargs):
        # 实现搜索逻辑
        # 返回 List[SearchResult]
```

2. 在 `app/services/search_engines/__init__.py` 中注册新引擎：

```python
from .new_engine import NewSearchEngine
__all__ = [..., "NewSearchEngine"]
```

3. 在 `app/core/config.py` 中添加新引擎配置：

```python
SEARCH_ENGINES = {
    ...,
    "new_engine": {
        "is_enabled": True,
        "config": {
            # 引擎特定配置
        }
    }
}
```

4. 在 `app/services/search_service.py` 中注册引擎类：

```python
self._engine_classes = {
    ...,
    "new_engine": NewSearchEngine
}
```

5. 在 `app/api/search.py` 中添加引擎描述：

```python
engine_descriptions = {
    ...,
    "new_engine": "新搜索引擎描述"
}
```

## 架构设计原则

本项目遵循以下架构设计原则：

1. **单一职责原则 (SRP)**：每个模块、类和函数都有一个明确的责任
2. **开闭原则 (OCP)**：系统设计允许添加新功能而无需修改现有代码
3. **依赖倒置原则 (DIP)**：高级模块不依赖低级模块的具体实现
4. **接口隔离原则 (ISP)**：客户端不应依赖它不使用的接口

## 错误处理

系统实现了全局异常处理，包括：

- 400 错误：无效的请求参数
- 500 错误：服务器内部错误

所有异常都会被记录到日志中，并返回友好的错误消息。

## 贡献指南

1. Fork 仓库
2. 创建特性分支: `git checkout -b feature/your-feature`
3. 提交更改: `git commit -am 'Add some feature'`
4. 推送到分支: `git push origin feature/your-feature`
5. 提交 Pull Request

## 许可证

MIT 许可证 - 详见 LICENSE 文件
