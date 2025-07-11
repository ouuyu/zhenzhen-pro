import httpx
import json
import re

class NeteaseMusicPlayer:
    def __init__(self):
        self.search_api_url = "https://163api.qijieya.cn/search"
        self.music_api_url = "https://api.bugpk.com/api/163_music"
        self.lyric_api_url = "https://163api.qijieya.cn/lyric"
        self.client = httpx.Client()

    def get_music_player_html(self, search_keywords: str) -> str:
        try:
            search_params = {"keywords": search_keywords, "limit": 1}
            search_response = self.client.get(self.search_api_url, params=search_params)
            search_response.raise_for_status()
            search_data = search_response.json()

            if not search_data.get("result", {}).get("songs"):
                return "未找到相关歌曲。"

            song_id = search_data["result"]["songs"][0]["id"]
            song_name = search_data["result"]["songs"][0]["name"]
            artist_name = search_data["result"]["songs"][0]["artists"][0]["name"]

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
            
            html_output = f"""
            <link rel="stylesheet" href="https://lf6-cdn-tos.bytecdntp.com/cdn/expire-1-M/aplayer/1.10.1/APlayer.min.css">
            <script src="https://lf26-cdn-tos.bytecdntp.com/cdn/expire-1-M/aplayer/1.10.1/APlayer.min.js"></script>
            <script src="https://npm.elemecdn.com/hexo-anzhiyu-music@1.0.1/assets/js/Meting2.min.js"></script>

            <div class="aplayer"
                data-id="{song_id}"
                data-server="netease"
                data-type="song"
                data-fixed="false"
                data-autoplay="false"
                data-theme="#FADFA3"
                data-loop="all"
                data-order="random"
                data-volume="0.7"
                data-lrc-type="1">
            </div>
            <p>歌曲: {song_name}</p>
            <p>歌手: {artist_name}</p>
            """
            
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
    search_term = "天后"
    html_player = player.get_music_player_html(search_term)
    print(html_player)