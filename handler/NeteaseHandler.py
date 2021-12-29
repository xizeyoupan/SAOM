import asyncio
import json
import os
from io import BytesIO
import aiohttp
import utils


class NeteaseImpl:
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
            config: json = json.load(f)['music']['netease']
            self.api = config['api']

    async def single_song(self, search_key: str, ctx) -> None:

        stream = BytesIO()
        ctx.song_will_search(search_key)

        async with self.session.get(self.api + "/search?keywords={}".format(
            search_key,
        )
        ) as resp:

            info: json = await resp.json()
            song_id: int = info['result']['songs'][0]['id']
            song_name: str = info['result']['songs'][0]['name']
            artist_name: str = info['result']['songs'][0]['artists'][0]['name']
            song_info = {"song_name": song_name, "artist_name": artist_name,
                         "song_id": song_id, }

            ctx.song_did_search(song_info)

        async with self.session.get(self.api + "/song/url?id={}&br=128000&realIP={}".format(
            song_id,
            utils.get_cn_ip())
        ) as song_detail:
            res = await song_detail.json()
            song_url: str = res['data'][0]['url']

        if not song_url:
            ctx.no_copyright(song_info)
            return

        now = 0.0
        size = 8192
        async with self.session.get(song_url) as resp:
            total = resp.content_length
            async for chunk in resp.content.iter_chunked(size):
                now += len(chunk)
                song_info['downloading'] = now / total
                ctx.song_do_download(song_info)
                stream.write(chunk)
        
        stream.seek(0)

        song_info["song_url"] = song_url
        song_info["file_name"] = song_url.split('/')[-1]
        song_info["content"] = stream
        ctx.song_did_download(song_info)

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.session.close()


async def main():
    async with NeteaseImpl() as netease:
        await netease.single_song("asoul 红色高跟鞋", print)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
