import asyncio
import json
import os
from io import BytesIO
import aiohttp
import utils


class QqmusicHandler:
    config_path = os.path.join(os.path.dirname(
        os.path.dirname(os.path.realpath(__file__))), 'config.json')

    async def __aenter__(self):
        conn = aiohttp.TCPConnector(ssl=False)
        self.session = aiohttp.ClientSession(connector=conn, trust_env=True)
        self.api = None
        self.get_config()
        return self

    def get_config(self) -> None:
        with open(self.config_path, 'r', encoding='utf8') as f:
            # config: json = json.load(f)['music']['netease']
            self.api = 'http://localhost:3300'

    async def single_song(self, search_key: str, ctx) -> None:
        stream = BytesIO()
        ctx.song_will_search(search_key)

        async with self.session.get(self.api + "/search?key={}".format(
            search_key,
        )
        ) as resp:

            info: json = (await resp.json())['data']['list']
            # media_mid = info[0]['media_mid']
            total = info[0]['size128']
            song_id: int = info[0]['songmid']
            song_name: str = info[0]['songname']
            artist_name: str = info[0]['singer'][0]['name']
            song_info = {"song_name": song_name, "artist_name": artist_name,
                         "song_id": song_id, }

            ctx.song_did_search(song_info)

        async with self.session.get(self.api + "/song/url?id={}".format(
            song_id,
        )
        ) as song_detail:

            res = await song_detail.json()

            if res['result'] != 100:
                ctx.no_copyright(song_info)
                return

            song_url: str = res['data']

        now = 0.0
        size = 8192
        async with self.session.get(song_url, headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"}) as resp:
            async for chunk in resp.content.iter_chunked(size):
                now += len(chunk)
                song_info['downloading'] = now / total
                ctx.song_do_download(song_info)
                stream.write(chunk)

        stream.seek(0)

        song_info["song_url"] = song_url
        song_info["file_name"] = song_url.split('?')[0].split('/')[-1]
        song_info["content"] = stream
        ctx.song_did_download(song_info)

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.session.close()
