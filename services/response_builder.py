import time
import secrets
from uuid import uuid4
from typing import Optional


def build_response(
    model: str, 
    user_id: str, 
    query: str, 
    answer: str, 
    conversation_id: Optional[str] = None, 
    warning: bool = False
) -> dict:
    """
    构建标准化的响应格式
    
    Args:
        model: 使用的模型名称
        user_id: 用户ID
        query: 用户查询内容
        answer: 回答内容
        conversation_id: 对话ID, 如果为None则生成新的
        warning: 是否包含警告信息
        
    Returns:
        dict: 格式化的响应数据
    """
    answer += f"\n\n `model: {model}` | `conversationId: {conversation_id or 'none'}`"
    
    return {
        "type": "json",
        "messageId": str(uuid4()),
        "conversationId": conversation_id or secrets.token_hex(12),
        "appId": "6837b25503c5c1219b17565e",
        "model": model,
        "modelProvider": "zhenhai",
        "userId": user_id,
        "answer": answer,
        "createdDate": int(time.time()),
        "query": query,
        "warning": warning
    }
