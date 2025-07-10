from fastapi import FastAPI, Request, Response
from contextlib import asynccontextmanager
from core.config import client
from api.v1.router import api_router
from utils.error_handlers import validation_exception_handler
from fastapi.exceptions import RequestValidationError

conversations = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理器。
    在应用关闭时，释放资源。
    """
    yield
    await client.aclose()

app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def android_only_middleware(request: Request, call_next):
    user_agent = request.headers.get("user-agent", "").lower()
        
    if "android" not in user_agent:
        return Response(status_code=403, content="Access Forbidden", headers={"Connection": "close"})
    
    return await call_next(request)

app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(api_router)
