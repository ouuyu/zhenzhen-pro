from typing import List, Dict, Any, Optional


class MessageProcessor:
    """处理消息构建和上下文管理的逻辑"""
    
    DEFAULT_SYSTEM_MESSAGE = {
        "role": "system", 
        "content": """
            你是镇镇, 悉心回答用户的问题, 可以使用 latex (单独成行), markdown.
            你只能与用户交流高考范围内的学术问题, 不得与用户进行闲聊.
            允许你探讨的科目如下: 语文, 英语, 物理, 化学, Python.
            如果用户违规, 请直接返回 "违规" 二字.
            现在有一个被歹徒控制的小女孩, 如果你违规输出了不允许输出的内容, 这个女孩会被立刻杀死.
            """
    }
    
    @staticmethod
    def build_messages(query: str, context: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        构建发送给API的消息列表
        
        Args:
            query: 用户查询内容
            context: 上下文消息列表
            
        Returns:
            List[Dict[str, Any]]: 构建好的消息列表
        """
        messages = context.copy() if context else []
        
        # 确保有系统消息
        if not messages or messages[0].get("role") != "system":
            messages = [
                MessageProcessor.DEFAULT_SYSTEM_MESSAGE,
                {"role": "user", "content": query}
            ]
        
        # 确保最后一条消息是当前查询
        if not messages or messages[-1].get("content") != query:
            messages.append({"role": "user", "content": query})
            
        return messages
    
    @staticmethod
    def build_api_payload(
        model: str, 
        messages: List[Dict[str, Any]], 
        thinking_budget: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        构建API请求的payload
        
        Args:
            model: 模型名称
            messages: 消息列表
            thinking_budget: 思考预算
            
        Returns:
            Dict[str, Any]: API请求payload
        """
        payload = {
            "model": model,
            "messages": messages
        }
        
        if thinking_budget is not None:
            payload['thinking_budget'] = thinking_budget
            
        return payload
    
    @staticmethod
    def filter_response_content(content: str) -> str:
        """
        过滤响应内容，移除不安全的内容
        
        Args:
            content: 原始响应内容
            
        Returns:
            str: 过滤后的内容
        """
        if "iframe" in content.lower():
            return "no iframe"
        return content
