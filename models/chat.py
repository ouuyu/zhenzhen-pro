from pydantic import BaseModel
from typing import Optional, Dict, Any

MODEL_MAPPING: Dict[str, Dict[str, Any]] = {
    "ds": {"model": "deepseek-ai/DeepSeek-V3", "deep_thinking": False},
    "gg": {"model": "gemini-2.0-flash", "deep_thinking": False},
    "gh": {"model": "gemini-2.5-flash", "deep_thinking": False},
    "lo": {"model": "Tongyi-Zhiwen/QwenLong-L1-32B", "deep_thinking": True},
    "bd": {"model": "baidu/ERNIE-4.5-300B-A47B", "deep_thinking": False}
}

DEFAULT_MODEL = "deepseek-ai/DeepSeek-V3"

class ChatMessageRequest(BaseModel):
    """聊天请求的模型"""
    query: str  # 用户查询内容
    model: Optional[str] = DEFAULT_MODEL  # 指定模型
    thinking_budget: Optional[int] = None

    def set_thinking_budget(self):
        model_key = self.model or DEFAULT_MODEL
        mapping = MODEL_MAPPING.get(model_key, {})
        if mapping.get("deep_thinking", False) and self.query.strip().lower().startswith(f"{model_key} thinking"):
            self.thinking_budget = 8192
        else:
            self.thinking_budget = 0