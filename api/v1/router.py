# api/v1/router.py
from fastapi import APIRouter
from api.v1.endpoints import chat, assets, proxy

api_router = APIRouter()

# 包含不同模块的路由
api_router.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
api_router.include_router(assets.router, prefix="/assets", tags=["Assets"])
# 注意：代理路由应该在最后，因为它匹配所有路径
api_router.include_router(proxy.router, tags=["Proxy"])