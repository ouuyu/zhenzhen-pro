"""
基本测试文件，用于验证应用程序的基本功能
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    """测试根路径是否可访问"""
    response = client.get("/")
    # 由于有Android限制中间件，这里应该返回403
    assert response.status_code == 403

def test_docs_accessible():
    """测试API文档是否可访问"""
    response = client.get("/docs")
    assert response.status_code == 200

def test_openapi_accessible():
    """测试OpenAPI规范是否可访问"""
    response = client.get("/openapi.json")
    assert response.status_code == 200

def test_app_creation():
    """测试应用程序是否能正确创建"""
    assert app is not None
    assert hasattr(app, 'routes')

def test_android_middleware():
    """测试Android中间件功能"""
    # 测试没有User-Agent的请求
    response = client.get("/api/v1/test", headers={})
    assert response.status_code == 403
    
    # 测试有Android User-Agent的请求
    response = client.get("/api/v1/test", headers={"User-Agent": "Android App"})
    # 这个路径不存在，但应该通过中间件检查
    assert response.status_code == 404  # 路径不存在，但通过了中间件

if __name__ == "__main__":
    pytest.main([__file__])
