import os
from typing import Dict, Any, Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """应用配置，从环境变量中读取"""
    
    # 应用设置
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    
    # Google Custom Search API
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    GOOGLE_CSE_ID: Optional[str] = os.getenv("GOOGLE_CSE_ID")
    
    # 缓存设置
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "True").lower() in ("true", "1", "t")
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))  # 默认缓存1小时
    
    class Config:
        env_file = ".env"


settings = Settings()


# 搜索引擎配置
SEARCH_ENGINES = {
    "google": {
        "is_enabled": bool(settings.GOOGLE_API_KEY and settings.GOOGLE_CSE_ID),
        "config": {
            "api_key": settings.GOOGLE_API_KEY,
            "cse_id": settings.GOOGLE_CSE_ID
        }
    }
    # 在此处添加更多搜索引擎配置
} 