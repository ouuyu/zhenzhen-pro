from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import Response, JSONResponse
from core.config import client, PROXY_URL
import httpx

router = APIRouter()

@router.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_requests(request: Request, full_path: str):
    """将所有不匹配的请求代理到目标URL"""
    url = f"{PROXY_URL}/{full_path}"
    headers = dict(request.headers)
    headers.pop("host", None)
    data = await request.body()
    
    try:
        # 根据请求方法发送代理请求
        if request.method == "GET":
            response = await client.get(url, headers=headers, params=request.query_params)
        elif request.method == "POST":
            response = await client.post(url, headers=headers, content=data)
        elif request.method == "PUT":
            response = await client.put(url, headers=headers, content=data)
        elif request.method == "DELETE":
            response = await client.delete(url, headers=headers, content=data)
        else:
            raise HTTPException(status_code=405, detail="Method Not Allowed")

        # 根据响应内容类型返回不同类型的Response
        if "application/json" in response.headers.get("Content-Type", ""):
            return JSONResponse(status_code=response.status_code, content=response.json())
        else:
            return Response(status_code=response.status_code, content=response.content, media_type=response.headers.get('Content-Type'))
            
    except httpx.HTTPStatusError as e:
        # 处理HTTP状态错误
        return Response(status_code=e.response.status_code, content=e.response.content)
    except Exception as e:
        # 处理其他异常
        raise HTTPException(status_code=500, detail=f"代理时发生错误: {str(e)}")