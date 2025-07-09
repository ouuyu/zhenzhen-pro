from typing import Tuple, Optional
from models.chat import MODEL_MAPPING


class ModelHandler:
    """处理模型相关的逻辑"""
    
    @staticmethod
    def generate_model_list_table() -> str:
        """
        生成模型列表的表格格式
        
        Returns:
            str: 格式化的模型列表表格
        """
        table = "| 简称 | 模型 | 深度思考 |\n|------|----------|--------------|\n"
        for k, v in MODEL_MAPPING.items():
            model_name = v["model"] if isinstance(v, dict) else v
            deep_thinking = v.get("deep_thinking", False) if isinstance(v, dict) else False
            table += f"| {k} | {model_name} | {'是' if deep_thinking else '否'} |\n"
        return f"当前支持的模型映射表如下：\n\n{table}"
    
    @staticmethod
    def parse_model_prefix(query: str) -> Tuple[str, str]:
        """
        解析查询中的模型前缀，返回处理后的查询和模型
        
        Args:
            query: 原始查询字符串
            
        Returns:
            Tuple[str, str]: (处理后的查询, 模型名称)
        """
        original_query = query
        model = ""
        
        for prefix, full_model in MODEL_MAPPING.items():
            if query.lower().startswith(f"{prefix}"):
                remain = query[len(prefix):]
                if remain and remain[0] in [":", " "]:
                    remain = remain[1:].strip()
                else:
                    remain = remain.strip()
                    
                # 处理 thinking 关键词
                if remain.lower().startswith("thinking"):
                    remain = remain[len("thinking"):].strip()
                    
                query = remain
                model = full_model["model"] if isinstance(full_model, dict) else full_model
                break
        
        return query, model
    
    @staticmethod
    def should_use_thinking_budget(query: str, model_key: str) -> bool:
        """
        判断是否应该使用思考预算
        
        Args:
            query: 查询内容
            model_key: 模型键名
            
        Returns:
            bool: 是否使用思考预算
        """
        mapping = MODEL_MAPPING.get(model_key, {})
        if isinstance(mapping, dict) and mapping.get("deep_thinking", False):
            return query.strip().lower().startswith(f"{model_key} thinking")
        return False
