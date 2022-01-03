import asyncio
import json
import os
from io import BytesIO
from handler.utils import headers

import aiohttp

if __name__ == '__main__':
    import sys
    sys.path.append(os.path.dirname(
        os.path.dirname(os.path.realpath(__file__))))

    from SAOM import SAOM

from handler.AbstractHandler import AbstractHandler


class BilibiliHandler(AbstractHandler):
    config_path = os.path.join(os.path.dirname(
        os.path.dirname(os.path.realpath(__file__))), 'config.json')

    def __init__(self, ctx) -> None:
        self.ctx = ctx

    async def __aenter__(self):
        conn = aiohttp.TCPConnector(ssl=False)
        self.session = aiohttp.ClientSession(
            connector=conn, headers={**headers, 'referer': 'https://www.bilibili.com'}, trust_env=True)
        self.api = None
        self.get_config()
        return self

    def get_config(self) -> None:
        with open(self.config_path, 'r', encoding='utf8') as f:
            config: json = json.load(f)['handler']['bilibili']
            self.name = config['name']

    async def single_song(self, search_key: str) -> None:
        stream = BytesIO()
        self.ctx.song_will_search(search_key)

        async with self.session.get('https://api.bilibili.com/x/web-interface/search/all/v2?keyword={}'.format(search_key)) as resp:
            video_json = (await resp.json())['data']['result'][10]['data']
            chosen_video = video_json[0]
            bvid = chosen_video['bvid']
            author = chosen_video['author']

        async with self.session.get('https://api.bilibili.com/x/player/pagelist?bvid={}'.format(bvid)) as resp:
            p = (await resp.json())['data'][0]
            duration = p['duration']
            cid = p['cid']
            title = p['part']
            song_info = {"song_name": title, "artist_name": author,
                         "song_id": bvid, "handler_name": self.name}
        self.ctx.song_did_search(song_info)

        params = {'bvid': bvid, 'cid': cid,
                  'qn': '0', 'fnval': '16', 'fnver': '0', }

        async with self.session.get("https://api.bilibili.com/x/player/playurl", params=params) as video_detail:

            res = await video_detail.json()
            audios = res['data']['dash']['audio']
            for audio in audios:
                if audio['id'] == 30216:
                    audio_url = audio['baseUrl']
                    break

        size = 8192
        now = 0.0
        async with self.session.get(audio_url) as resp:
            total = resp.content_length
            async for chunk in resp.content.iter_chunked(size):
                now += len(chunk)
                song_info['downloading'] = now / total
                self.ctx.song_do_download(song_info)
                stream.write(chunk)

        stream.seek(0)

        song_info["song_url"] = audio_url
        song_info["file_name"] = audio_url.split('?')[0].split('/')[-1]
        song_info["content"] = stream
        self.ctx.song_did_download(song_info)

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.session.close()


async def _test():
    async with BilibiliHandler(SAOM()) as bili:
        await bili.single_song("珈乐 红色高跟鞋")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_test())
