from typing import Dict, Any, Tuple
from core.config import client, BASE_URL, API_KEY


class GeminiAPIClient:
    """处理与Gemini API的通信逻辑"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.api_key = API_KEY
        self.client = client
    
    def _build_headers(self) -> Dict[str, str]:
        """
        构建API请求头
        
        Returns:
            Dict[str, str]: 请求头字典
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def call_chat_completion(self, payload: Dict[str, Any]) -> Tuple[bool, str, str]:
        """
        调用聊天完成API
        
        Args:
            payload: API请求载荷
            
        Returns:
            Tuple[bool, str, str]: (是否成功, 响应内容或错误信息, 错误详情)
        """
        headers = self._build_headers()
        
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions", 
                json=payload, 
                headers=headers
            )
            response.raise_for_status()
            
            response_data = response.json()
            content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "failed to get datas")
            
            return True, content, ""
            
        except Exception as e:
            error_detail = ""
            if hasattr(e, 'response') and e.response is not None: # type: ignore
                try:
                    error_detail = f"\n\n后端返回: {e.response.text}" # type: ignore
                except Exception:
                    pass
            
            error_message = f"[错误] {str(e)}{error_detail}"
            return False, error_message, error_detail
