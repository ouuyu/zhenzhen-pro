import hashlib
import time
from typing import Optional, List
from models.chat import ChatMessageRequest
from core.context import conversations
from .response_builder import build_response
from .model_handler import ModelHandler
from .message_processor import MessageProcessor
from .api_client import GeminiAPIClient
from .netease import NeteaseMusicPlayer

banned_time_schedule = [
    ("17:50", "21:30"),
    ("12:50", "13:30"),
    ("07:00", "11:50"),
    ("14:40", "16:10")
]

debug_password_md5 = "07794CCCB03C3EB315AAAA292E377A7F"

async def get_gemini_response(
    user_id: str,
    conversation_id: Optional[str],
    request_data: ChatMessageRequest,
    context: Optional[List[dict]] = None
) -> dict:
    query = request_data.query.strip()
    model = request_data.model or "default"

    if query.lower() == "list":
        return build_response(model, user_id, query, ModelHandler.generate_model_list_table(), conversation_id)

    query_parts = query.split()
    if query_parts and query_parts[0].startswith("test"):
        current_time = time.strftime("%H:%M")
        is_debug = hashlib.md5(query_parts[0].encode()).hexdigest() == debug_password_md5.lower()

        if any(start <= current_time <= end for start, end in banned_time_schedule) and not is_debug:
            return build_response(model, user_id, query, "禁止访问 " + current_time, conversation_id)

        if len(query_parts) > 1 and query_parts[1] == "wyy":
            if len(query_parts) > 2:
                player = NeteaseMusicPlayer()
                html_player = player.get_music_player_html(query_parts[2])
                return build_response(model, user_id, query, html_player, conversation_id, log_model=False)

    processed_query, parsed_model = ModelHandler.parse_model_prefix(query)
    if parsed_model:
        model = parsed_model
        query = processed_query

    messages = MessageProcessor.build_messages(query, context)
    payload = MessageProcessor.build_api_payload(model, messages, request_data.thinking_budget)

    api_client = GeminiAPIClient()
    success, content, error_detail = await api_client.call_chat_completion(payload)

    answer = MessageProcessor.filter_response_content(content) if success else content
    return build_response(model, user_id, query, answer, conversation_id)