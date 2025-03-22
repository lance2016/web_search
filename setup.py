from setuptools import setup, find_packages

setup(
    name="web-search-api",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.100.0",
        "uvicorn>=0.22.0",
        "python-dotenv>=1.0.0",
        "httpx>=0.24.1",
        "pydantic>=2.0.3",
        "pydantic-settings>=2.0.3",
        "python-multipart>=0.0.6",
    ],
) 