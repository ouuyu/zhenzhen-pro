import httpx
import xml.etree.ElementTree as ET
import html
import re


class ITHomeRSSReader:
    def __init__(self):
        # IT之家RSS订阅地址
        self.rss_url = "https://www.ithome.com/rss"
        # 初始化HTTP客户端，设置超时时间为30秒
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
            # 发起HTTP GET请求获取RSS内容
            response = self.client.get(self.rss_url)
            # 检查HTTP响应状态，如果不是2xx则抛出异常
            response.raise_for_status()

            # 解析XML内容
            root = ET.fromstring(response.content)

            # 查找所有item元素（新闻条目）
            items = root.findall('.//item')

            # 如果没有找到新闻内容，返回提示信息
            if not items:
                return "未找到新闻内容。"

            # 限制返回的新闻条数
            items = items[:limit]

            # 构建HTML内容的起始部分，设置最小字体和行高，颜色调整为更淡的灰色
            html_content = '<div style="font-size:smaller;line-height:1.2;color:#555;">'

            # 遍历每个新闻条目
            for i, item in enumerate(items, 1):
                # 安全获取标题元素文本，并进行HTML转义
                title_elem = item.find('title')
                title = html.escape(title_elem.text if title_elem is not None and title_elem.text else "无标题")

                # 安全获取链接元素文本
                link_elem = item.find('link')
                link = link_elem.text if link_elem is not None and link_elem.text else "#"

                # 安全获取发布日期元素文本
                pub_date_elem = item.find('pubDate')
                pub_date = pub_date_elem.text if pub_date_elem is not None and pub_date_elem.text else "未知时间"

                # 安全获取描述元素文本
                description_elem = item.find('description')
                description = description_elem.text if description_elem is not None and description_elem.text else ""

                # 清理描述内容：
                # 1. 移除所有HTML标签
                description = re.sub(r'<[^>]+>', '', description)
                # 2. 将HTML实体（如&nbsp;）解码为实际字符
                description = html.unescape(description)
                # 3. 将连续的空白字符（包括换行符）替换为单个空格，并去除首尾空白
                description = re.sub(r'\s+', ' ', description).strip()
                # 4. 对清理后的文本进行HTML转义，防止XSS
                description = html.escape(description)

                # 尝试格式化发布时间，提取日期和时间部分
                try:
                    time_match = re.search(r'\d{1,2} \w{3} \d{4} \d{2}:\d{2}:\d{2}', pub_date)
                    if time_match:
                        pub_date = time_match.group()
                except:
                    pass  # 忽略时间解析错误，使用原始字符串

                # 处理可选的描述部分，如果描述不为空则生成对应的HTML
                description_html = ""
                if description:
                    # 描述字体颜色调整为更浅的灰色
                    description_html = f'<div style="color:#777;font-size:0.85em;">{description}</div>'

                # 构建单个新闻条目的HTML
                news_item_html = (
                    # 边框颜色调整为更淡的蓝色
                    f'<div style="margin-bottom:12px;padding:8px;border-left:2px solid #66b3e6;">'
                    f'<div style="font-weight:bold;margin-bottom:4px;">'
                    # 链接颜色调整为更淡的蓝色
                    f'<a href="{link}" target="_blank" style="color:#66b3e6;text-decoration:none;">'
                    f'{i}. {title}</a></div>'
                    # 发布时间颜色调整为稍深的灰色
                    f'<div style="color:#888;font-size:0.9em;margin-bottom:4px;">{pub_date}</div>'
                    f'{description_html}'  # 插入已生成的描述HTML
                    f'</div>'
                )
                html_content += news_item_html

            # HTML内容的结束部分
            html_content += '</div>'

            return html_content

        except httpx.HTTPStatusError as e:
            # 处理HTTP请求状态错误
            return f"获取RSS失败, 状态码: {e.response.status_code}. 详细信息: {e.response.text}"
        except httpx.RequestError as e:
            # 处理HTTP请求网络错误
            return f"请求发送失败: {e}"
        except ET.ParseError as e:
            # 处理XML解析错误
            return f"RSS解析失败: {e}"
        except Exception as e:
            # 处理其他未知错误
            return f"发生未知错误: {e}"

    def __del__(self):
        """清理资源，关闭HTTP客户端"""
        # 确保client属性存在才关闭
        if hasattr(self, 'client'):
            self.client.close()


if __name__ == "__main__":
    reader = ITHomeRSSReader()
    # 获取最新的10条新闻的HTML格式内容
    news_html = reader.get_latest_news_html()
    print(news_html)