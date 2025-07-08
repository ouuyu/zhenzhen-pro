import time
import secrets
from uuid import uuid4
from fastapi import HTTPException
from typing import Optional, List
from core.config import client, BASE_URL, API_KEY
from models.chat import ChatMessageRequest, MODEL_MAPPING
from core.context import conversations


def build_response(
    model, user_id, query, answer, conversation_id=None, warning=False
):
    answer += "\n\n `model: " + model + "` | `conversationId: " + (conversation_id or "none") + "`"
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

async def get_gemini_response(user_id: str, conversation_id: Optional[str], request_data: ChatMessageRequest, context: List[dict] = None):
    """
    调用Gemini API并返回处理后的响应
    """
    query = request_data.query
    model = request_data.model
    used_model_name = None

    if query.strip().lower() == "list":
        table = "| 简称 | 模型 | 深度思考 |\n|------|----------|--------------|\n"
        for k, v in MODEL_MAPPING.items():
            model_name = v["model"] if isinstance(v, dict) else v
            deep_thinking = v.get("deep_thinking", False) if isinstance(v, dict) else False
            table += f"| {k} | {model_name} | {'是' if deep_thinking else '否'} |\n"
        answer = f"当前支持的模型映射表如下：\n\n{table}"
        return build_response(model, user_id, query, answer, conversation_id)

    for prefix, full_model in MODEL_MAPPING.items():
        if query.lower().startswith(f"{prefix}"):
            remain = query[len(prefix):]
            if remain and remain[0] in [":", " "]:
                remain = remain[1:].strip()
            else:
                remain = remain.strip()
            if remain.lower().startswith("thinking"):
                remain = remain[len("thinking"):].strip()
            query = remain
            model = full_model["model"] if isinstance(full_model, dict) else full_model
            break

    messages = context.copy() if context else []
    if not messages or messages[0].get("role") != "system":
        messages = [
            {
                "role": "system", 
                "content": "你是镇镇, 悉心回答用户的问题, 可以使用 latex (单独成行), markdown."
            },
            {"role": "user", "content": query}
        ]
    if not messages or messages[-1].get("content") != query:
        messages.append({"role": "user", "content": query})
    payload = {
        "model": model,
        "messages": messages
    }

    if request_data.thinking_budget is not None:
        payload['thinking_budget'] = request_data.thinking_budget

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = await client.post(f"{BASE_URL}/chat/completions", json=payload, headers=headers)
        response.raise_for_status()

        response_data = response.json()
        answer = response_data.get("choices", [{}])[0].get("message", {}).get("content", "failed to get datas")

        if "iframe" in answer.lower():
            answer = "no iframe"

        return build_response(model, user_id, query, answer, conversation_id)
    except Exception as e:
        error_detail = ""
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = f"\n\n后端返回: {e.response.text}"
            except Exception:
                pass
        answer = f"[错误] {str(e)}{error_detail}"
        return build_response(model, user_id, query, answer, conversation_id)