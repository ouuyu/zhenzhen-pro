import httpx
import xml.etree.ElementTree as ET
from typing import List, Dict
import html
from datetime import datetime
import re


class ITHomeRSSReader:
    def __init__(self):
        self.rss_url = "https://www.ithome.com/rss"
        self.client = httpx.Client(timeout=30.0)

    def get_latest_news_html(self, limit: int = 10) -> str:
        """
        获取IT之家最新新闻，返回HTML格式
        
        Args:
            limit: 返回新闻条数，默认10条
            
        Returns:
            str: 格式化的HTML内容
        """
        try:
            # 获取RSS内容
            response = self.client.get(self.rss_url)
            response.raise_for_status()
            
            # 解析XML
            root = ET.fromstring(response.content)
            
            # 查找所有item元素
            items = root.findall('.//item')
            
            if not items:
                return "未找到新闻内容。"
            
            # 限制返回条数
            items = items[:limit]
            
            # 构建HTML内容
            html_content = '<div style="font-size: smaller; line-height: 1.2;">\n'
            
            for i, item in enumerate(items, 1):
                title_elem = item.find('title')
                link_elem = item.find('link')
                pub_date_elem = item.find('pubDate')
                description_elem = item.find('description')
                
                title = html.escape(title_elem.text or "无标题" if title_elem is not None else "无标题")
                link = link_elem.text if link_elem is not None else "#"
                pub_date = pub_date_elem.text if pub_date_elem is not None else "未知时间"
                description = description_elem.text if description_elem is not None else ""
                
                # 清理描述内容，移除HTML标签，显示全文
                if description:
                    # 简单的HTML标签清理
                    import re
                    description = re.sub(r'<[^>]+>', '', description)
                    # 移除多余的空白字符和换行符
                    description = re.sub(r'\s+', ' ', description).strip()
                    description = html.escape(description)
                
                # 格式化发布时间（简化显示）
                try:
                    # 尝试解析时间格式，如果失败就使用原始字符串
                    if pub_date:
                        time_match = re.search(r'\d{1,2} \w{3} \d{4} \d{2}:\d{2}:\d{2}', pub_date)
                        if time_match:
                            pub_date = time_match.group()
                except:
                    pass
                
                html_content += f'''
                <div style="margin-bottom: 12px; padding: 8px; border-left: 2px solid #007acc;">
                    <div style="font-weight: bold; margin-bottom: 4px;">
                        <a href="{link}" target="_blank" style="color: #007acc; text-decoration: none;">
                            {i}. {title}
                        </a>
                    </div>
                    <div style="color: #666; font-size: 0.9em; margin-bottom: 4px;">
                        {pub_date}
                    </div>
                    {f'<div style="color: #888; font-size: 0.85em;">{description}</div>' if description else ''}
                </div>
                '''
            
            html_content += '</div>'
            
            return html_content
            
        except httpx.HTTPStatusError as e:
            return f"获取RSS失败, 状态码: {e.response.status_code}. 详细信息: {e.response.text}"
        except httpx.RequestError as e:
            return f"请求发送失败: {e}"
        except ET.ParseError as e:
            return f"RSS解析失败: {e}"
        except Exception as e:
            return f"发生未知错误: {e}"

    def __del__(self):
        """清理资源"""
        if hasattr(self, 'client'):
            self.client.close()


if __name__ == "__main__":
    reader = ITHomeRSSReader()
    news_html = reader.get_latest_news_html()
    print(news_html)
