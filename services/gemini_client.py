import httpx
import xml.etree.ElementTree as ET
import html
import re


class ITHomeRSSReader:
    def __init__(self):
        self.rss_url = "https://www.ithome.com/rss"
        # 初始化HTTP客户端，设置超时
        self.client = httpx.Client(timeout=30.0)

    def get_latest_news_html(self, limit: int = 10) -> str:
        """
        获取IT之家最新新闻，返回HTML格式。
        
        Args:
            limit: 返回新闻条数，默认10条。
            
        Returns:
            str: 格式化的HTML内容。
        """
        try:
            # 获取RSS内容
            response = self.client.get(self.rss_url)
            response.raise_for_status()  # 检查HTTP响应状态
            
            # 解析XML
            root = ET.fromstring(response.content)
            
            # 查找所有item元素
            items = root.findall('.//item')
            
            if not items:
                return "未找到新闻内容。"
            
            # 限制返回条数
            items = items[:limit]
            
            # 构建HTML内容，外层div只保留最小样式
            html_content = '<div style="font-size:smaller;line-height:1.2;">'
            
            for i, item in enumerate(items, 1):
                # 安全获取元素文本，避免NoneType错误
                title_elem = item.find('title')
                link_elem = item.find('link')
                pub_date_elem = item.find('pubDate')
                description_elem = item.find('description')
                
                # 对标题进行HTML转义，防止XSS
                title = html.escape(title_elem.text if title_elem is not None and title_elem.text else "无标题")
                link = link_elem.text if link_elem is not None and link_elem.text else "#"
                pub_date = pub_date_elem.text if pub_date_elem is not None and pub_date_elem.text else "未知时间"
                description = description_elem.text if description_elem is not None and description_elem.text else ""
                
                # 清理描述内容：移除HTML标签，合并空白字符，然后进行HTML转义
                if description:
                    description = re.sub(r'<[^>]+>', '', description) # 移除所有HTML标签
                    description = re.sub(r'\s+', ' ', description).strip() # 合并多余空白并去除首尾空白
                    description = html.escape(description) # 对清理后的文本进行HTML转义
                
                # 尝试格式化发布时间，如果失败则使用原始字符串
                try:
                    time_match = re.search(r'\d{1,2} \w{3} \d{4} \d{2}:\d{2}:\d{2}', pub_date)
                    if time_match:
                        pub_date = time_match.group()
                except:
                    pass # 忽略时间解析错误
                
                # 处理可选的描述部分，避免f-string内嵌f-string的问题
                description_html = ""
                if description:
                    description_html = f'<div style="color:#888;font-size:0.85em;">{description}</div>'

                # 构建单个新闻条目的HTML，移除多余CSS和缩进。这里用括号包裹字符串，使其可以在多行编写，但实际是拼接成单行。
                news_item_html = (
                    f'<div style="margin-bottom:12px;padding:8px;border-left:2px solid #007acc;">'
                    f'<div style="font-weight:bold;margin-bottom:4px;">'
                    f'<a href="{link}" target="_blank" style="color:#007acc;text-decoration:none;">'
                    f'{i}. {title}</a></div>'
                    f'<div style="color:#666;font-size:0.9em;margin-bottom:4px;">{pub_date}</div>'
                    f'{description_html}' # 使用已生成的description_html
                    f'</div>'
                )
                html_content += news_item_html
            
            html_content += '</div>'
            
            return html_content
            
        except httpx.HTTPStatusError as e:
            # HTTP请求状态错误处理
            return f"获取RSS失败, 状态码: {e.response.status_code}. 详细信息: {e.response.text}"
        except httpx.RequestError as e:
            # HTTP请求网络错误处理
            return f"请求发送失败: {e}"
        except ET.ParseError as e:
            # XML解析错误处理
            return f"RSS解析失败: {e}"
        except Exception as e:
            # 其他未知错误处理
            return f"发生未知错误: {e}"

    def __del__(self):
        """清理资源，关闭HTTP客户端"""
        if hasattr(self, 'client'):
            self.client.close()


if __name__ == "__main__":
    reader = ITHomeRSSReader()
    news_html = reader.get_latest_news_html()
    print(news_html)