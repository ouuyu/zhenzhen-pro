# api/v1/endpoints/assets.py
from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()

@router.get("/logo-DCrHZW4w.png")
async def get_logo():
    # 返回logo图片
    return FileResponse("assets/logo.png")

@router.get("/mask-CxIUc4JG.png")
async def get_small_logo():
    # 返回小logo图片
    return FileResponse("assets/small.png")