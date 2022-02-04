import asyncio
import configparser
import logging
import os
from ast import literal_eval
from io import BytesIO
from os.path import dirname

import aiohttp
from pyquery import PyQuery as pq
from SAOM import SAOM
from tinydb import TinyDB
from utils import headers

from handler.AbstractHandler import AbstractHandler

DB_PATH = os.path.join(
    dirname(dirname(os.path.realpath(__file__))), 'content\songs.json')
CONTENT_PATH = os.path.join(
    dirname(dirname(os.path.realpath(__file__))), 'content')
db = TinyDB(DB_PATH)
logger = logging.getLogger(f'saom.{__name__}')


class BilibiliHandler(AbstractHandler):
    config_path = os.path.join(dirname(
        dirname(os.path.realpath(__file__))), 'config.ini')

    def __init__(self, ctx: SAOM) -> None:
        self.ctx = ctx
        self.session = aiohttp.ClientSession(
            headers={**headers, 'referer': 'https://www.bilibili.com'})
        self.get_config()
        if self.config['enable']['value']:
            self.start()

    def start(self):
        self.__running = True
        self.get_config()
        logger.debug('start.')

    def stop(self):
        self.__running = False
        logger.debug('stop.')

    @property
    def default_config(self):
        return {
            "className": {'value': self.__class__.__name__, "type": "str", "disabled": True},
            "name": {'value': "b站", "type": "str", "disabled": True},
            "shortcut": {'value': "b", "type": "str", "disabled": True},
            "holdtoplay": {'value': False, "alias": "按住来播放音乐", "type": "bool", "disabled": False},
            "enable": {'value': True, "alias": "开启音乐api", "type": "bool", "disabled": False},
        }

    def get_config(self) -> None:
        config = configparser.ConfigParser()
        config.read(self.config_path, encoding='utf-8')
        self.config = config[f'handler.{self.__class__.__name__}']
        self.config = dict(self.config)
        for k, v in self.config.items():
            self.config[k] = literal_eval(v)

    def save_config(self, config: dict) -> None:
        config_parser = configparser.ConfigParser()
        config_parser.read(self.config_path, encoding='utf-8')
        config_parser[f'handler.{self.__class__.__name__}'] = config
        with open(self.config_path, 'w', encoding='utf-8') as f:
            config_parser.write(f)

    def parse(self, line: str):
        if not self.__running or 'saom' not in line:
            return
        line = line.split('saom')[-1]
        namespace = self.ctx.parser.parse_line(line)
        if not namespace:
            return
        if namespace.pos0 == 's' and namespace.pos1:
            asyncio.create_task(self.single_song(' '.join(namespace.pos1)))

    def __del__(self):
        asyncio.create_task(self.session.close())

    async def single_song(self, search_key: str) -> None:
        logger.debug(f'Search {search_key}.')
        stream = BytesIO()
        self.ctx.game.write_status(
            f'接到指令！ 正在搜索： {search_key}，{self.config["name"]["value"]}')

        async with self.session.get('https://api.bilibili.com/x/web-interface/search/all/v2?keyword={}'.format(search_key)) as resp:
            video_json = (await resp.json())['data']['result'][10]['data']
            if not len(video_json):
                self.ctx.game.write_status(
                    f'没有找到 {search_key}-{self.config["name"]["value"]}.')
                logger.warning(
                    f'No result for {search_key}.')
                return
            chosen_video = video_json[0]
            bvid = chosen_video['bvid']
            author = chosen_video['author']
            d = pq(chosen_video['title'])
            title = d.text()

        async with self.session.get('https://api.bilibili.com/x/player/pagelist?bvid={}'.format(bvid)) as resp:
            p = (await resp.json())['data'][0]
            # duration = p['duration']
            cid = p['cid']
            song_info = {"song_name": title, "handler_name": self.config['name']['value'],
                         "artist_name": author, "song_id": bvid}

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
                stream.write(chunk)
                self.ctx.game.write_status(' - {} - 正在下载 - {} - {} -- 进度： {:.2f}%'.format(
                    self.config["name"]['value'],
                    song_info['song_name'],
                    song_info['artist_name'],
                    song_info['downloading'] * 100,
                ))

        logger.debug(f'Song downloaded {title}.')
        stream.seek(0)

        song_info["song_url"] = audio_url
        song_info["file_name"] = audio_url.split('?')[0].split('/')[-1]

        _path = os.path.join(CONTENT_PATH, song_info['file_name'])
        with open(_path, 'wb') as f:
            f.write(stream.read())
        logger.debug(f'Song saved to {_path}.')

        self.ctx.game.write_status(f" - {song_info['song_name']} - 正在转码...")
        c = await self.ctx.game.trans_wav(song_info)
        if c == 0:
            db.insert(song_info)
            self.ctx.game.write_status('当前歌曲-{}-{}-{}'.format(
                song_info['song_name'],
                song_info['artist_name'],
                song_info['handler_name']))
            return
        elif c == -1:
            self.ctx.game.write_status('哈哈，音频文件大小超过阈值了捏')
            return


if __name__ == "__main__":
    ...
