# utils/error_handlers.py
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Any

class CustomErrorDetail(BaseModel):
    loc: List[Any] = Field(..., title="Location")
    msg: str = Field(..., title="Message")
    type: str = Field(..., title="Error Type")

class CustomErrorResponse(BaseModel):
    code: int = 422
    message: str = "请求参数验证失败"
    errors: List[CustomErrorDetail]

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理 Pydantic 的请求验证错误"""
    formatted_errors = [
        CustomErrorDetail(loc=list(error["loc"]), msg=error["msg"], type=error["type"])
        for error in exc.errors()
    ]
    custom_response = CustomErrorResponse(errors=formatted_errors)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=custom_response.model_dump()
    )