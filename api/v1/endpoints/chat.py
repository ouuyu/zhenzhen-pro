# api/v1/endpoints/chat.py
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from core.config import ALLOWED_USERS
from models.chat import ChatMessageRequest
from services import gemini_client
from core.context import conversations

router = APIRouter()

def check_user_access(user_id: str):
    if user_id not in ALLOWED_USERS:
        raise HTTPException(status_code=403, detail="禁止访问")
    return user_id

@router.post("/pub/agent/users/{user_id}/chat/messages")
async def send_chat_message(
    message: ChatMessageRequest, 
    user_id: str = Depends(check_user_access), 
    conversationId: Optional[str] = None
):
    """
    接收用户消息, 调用Gemini服务, 并返回AI的回答。
    - `user_id`: 从路径中获取的用户ID, 通过依赖项进行验证。
    - `message`: 请求体, 包含查询、模型和thinking_budget。
    - `conversationId`: 可选的会话ID。
    """
    conv_id = conversationId or user_id
    
    # 初始化会话历史
    if conv_id not in conversations:
        conversations[conv_id] = []
    
    # 添加用户消息到历史记录
    conversations[conv_id].append({"role": "user", "content": message.query})
    
    # 获取最近的对话历史（不包括系统消息）
    context = [msg for msg in conversations[conv_id][-10:] if msg.get("role") != "system"]
    
    # 调用API获取响应
    response = await gemini_client.get_gemini_response(user_id, conv_id, message, context)
    
    # 添加助手回复到历史记录
    conversations[conv_id].append({"role": "assistant", "content": response.get("answer", "")})
    
    return response

@router.get("/pub/agent/users/{userId}/appId/{appId}/violation")
async def violation(userId: str, appId: str):
    """检查用户是否违规（禁言）"""
    res = {}
    if userId not in ALLOWED_USERS:
        res = {
            "muteEndTime": 1759333399999  # 设置一个未来的禁言时间戳
        }
    return res