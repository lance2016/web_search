from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from typing import Dict, Any

from app.api import api_router
from app.core.config import settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("web-search-api")

# 创建FastAPI应用
app = FastAPI(
    title="Web Search API",
    description="一个可扩展的Web搜索API，支持多种搜索引擎",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应指定允许的源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"全局异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误，请稍后再试"},
    )

# 注册API路由
app.include_router(api_router, prefix="/api")

# 健康检查端点
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    return {
        "status": "ok",
        "environment": settings.APP_ENV,
        "version": "0.1.0",
    }

# 主入口点
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG) 