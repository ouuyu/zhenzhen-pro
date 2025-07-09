import time
from typing import Optional, List
from models.chat import ChatMessageRequest
from core.context import conversations
from .response_builder import build_response
from .model_handler import ModelHandler
from .message_processor import MessageProcessor
from .api_client import GeminiAPIClient
from .netease import NeteaseMusicPlayer

# 禁止访问时间表
banned_time_schedule = [
    ("17:50", "21:30"),
    ("12:50", "13:30")
]

async def get_gemini_response(
    user_id: str,
    conversation_id: Optional[str],
    request_data: ChatMessageRequest,
    context: Optional[List[dict]] = None
) -> dict:
    """
    调用Gemini API并返回处理后的响应

    Args:
        user_id: 用户ID
        conversation_id: 对话ID
        request_data: 聊天请求数据
        context: 上下文消息列表

    Returns:
        dict: 格式化的响应数据
    """
    query = request_data.query
    model = request_data.model or "default"

    # 处理模型列表查询
    if query.strip().lower() == "list":
        answer = ModelHandler.generate_model_list_table()
        return build_response(model, user_id, query, answer, conversation_id)

    # 处理当前时间与禁止时间
    if query.strip().lower()[0] == "test":
        current_time = time.strftime("%H:%M")
        for start, end in banned_time_schedule:
            if start <= current_time <= end:
                return build_response(model, user_id, query, "当前禁止访问", conversation_id)
        if query.strip().lower()[1] == "wyy":
            player = NeteaseMusicPlayer()
            search_term = query.strip().lower()[2:].join(' ')
            html_player = player.get_music_player_html(search_term)
            return build_response(model, user_id, query, html_player, conversation_id)

    # 解析模型前缀
    processed_query, parsed_model = ModelHandler.parse_model_prefix(query)
    if parsed_model:
        model = parsed_model
        query = processed_query

    # 构建消息
    messages = MessageProcessor.build_messages(query, context)

    # 构建API载荷
    payload = MessageProcessor.build_api_payload(model, messages, request_data.thinking_budget)

    # 调用API
    api_client = GeminiAPIClient()
    success, content, error_detail = await api_client.call_chat_completion(payload)

    if success:
        # 过滤响应内容
        answer = MessageProcessor.filter_response_content(content)
        return build_response(model, user_id, query, answer, conversation_id)
    else:
        return build_response(model, user_id, query, content, conversation_id)