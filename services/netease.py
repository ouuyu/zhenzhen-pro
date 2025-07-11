import httpx
import json
import re

class NeteaseMusicPlayer:
    def __init__(self):
        self.search_api_url = "https://163api.qijieya.cn/search"
        self.music_api_url = "https://api.bugpk.com/api/163_music"
        self.lyric_api_url = "https://163api.qijieya.cn/lyric"  # 歌词API地址
        self.client = httpx.Client()

    def get_music_player_html(self, search_keywords: str) -> str:
        """
        根据搜索关键词获取网易云音乐播放器HTML和歌词。
        """
        try:
            # 搜索歌曲
            search_params = {"keywords": search_keywords, "limit": 1}
            search_response = self.client.get(self.search_api_url, params=search_params)
            search_response.raise_for_status()
            search_data = search_response.json()

            if not search_data.get("result", {}).get("songs"):
                return "未找到相关歌曲。"

            song_id = search_data["result"]["songs"][0]["id"]
            song_name = search_data["result"]["songs"][0]["name"]
            artist_name = search_data["result"]["songs"][0]["artists"][0]["name"]

            # 获取音乐播放链接
            music_params = {
                "ids": song_id,
                "level": "exhigh",
                "type": "json"
            }
            music_response = self.client.get(self.music_api_url, params=music_params)
            
            try:
                music_data = music_response.json()
            except json.JSONDecodeError:
                music_response.raise_for_status()
                return "解析音乐数据失败，响应不是有效的 JSON。"

            if music_response.status_code != 200 and not (music_data.get("url") and music_data.get("status") == 200):
                music_response.raise_for_status()
            
            if not music_data.get("url"): # 检查URL是否存在
                return "未能获取歌曲播放链接。"

            music_url = music_data["url"]

            # 获取歌词
            lyric_params = {"id": song_id}
            lyric_response = self.client.get(self.lyric_api_url, params=lyric_params)
            lyric_response.raise_for_status()
            lyric_data = lyric_response.json()

            lyric_html = ""
            if lyric_data.get("lrc", {}).get("lyric"):
                raw_lyric = lyric_data["lrc"]["lyric"]
                # 移除时间戳和作者/作曲信息，并用 <br> 分隔
                cleaned_lyric = re.sub(r"\[\d{2}:\d{2}\.\d{3}\]", "", raw_lyric) # 移除时间戳
                # 移除作词/作曲等小字信息
                cleaned_lyric = re.sub(r"\[\d{2}:\d{2}\.\d{3}\]\s*.*?:.*?\n", "", cleaned_lyric)
                cleaned_lyric = "<br>".join([line.strip() for line in cleaned_lyric.split('\n') if line.strip()]) # 每行用<br>分隔
                lyric_html = f'<div style="font-size: smaller;"><p>{cleaned_lyric}</p></div>' # 用小字显示

            # 构建HTML输出
            html_output = f'<p>歌曲: {song_name}</p>\n<p>歌手: {artist_name}</p>\n'
            html_output += f'<audio controls src="{music_url}"></audio>\n'
            html_output += lyric_html # 添加歌词HTML

            return html_output

        except httpx.HTTPStatusError as e:
            return f"API请求失败, 状态码: {e.response.status_code}. 详细信息: {e.response.text}"
        except httpx.RequestError as e:
            return f"请求发送失败: {e}"
        except json.JSONDecodeError:
            return "解析响应数据失败, 可能不是有效的 JSON。"
        except KeyError:
            return "API响应数据结构不符合预期, 缺少关键字段。"
        except Exception as e:
            return f"发生未知错误: {e}"

if __name__ == "__main__":
    player = NeteaseMusicPlayer()
    search_term = "情非得已"
    html_player = player.get_music_player_html(search_term)
    print(html_player)