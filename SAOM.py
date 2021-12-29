import asyncio
from gamer.Csgo import Csgo
from handler import *
from io import BytesIO
from handler import NeteaseHandler
from tinydb import TinyDB, where
import os

from argparser import DefaultParser
from handler.QqmusicHandler import QqmusicHandler
DB_PATH = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), 'content\songs.json')
CONTENT_PATH = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), 'content')
db = TinyDB(DB_PATH)


class SAOM:
    def __init__(self):
        self.parser = DefaultParser.DefaultParser(self)
        self.locale = 'en'
        self.game_name = 'csgo'
        self.music_impl = 'NeteaseImpl'
        self.hold_to_play = False
        self.play_key = 'N'
        self.status_key = 'L'
        self.game = None
        self.__set_status("还没有点歌捏")

    def set_status(self, message):
        self.__set_status(message)

    def __set_status(self, message):
        self.status = 'SAOM-在线点歌  github: xizeyoupan ' + message
        if self.game:
            self.game.write_status()

    def parse(self, line):
        self.parser.parse_line(line)

    def no_copyright(self, info):
        self.__set_status('找到了{}-{}，但是网易云没有版权（；´д｀）ゞ'.format(
            info['song_name'],
            info['artist_name']))

    def song_did_download(self, song_info):
        with open(os.path.join(CONTENT_PATH, song_info['file_name']), 'wb') as f:
            f.write(song_info['content'].read())
            print(os.path.join(CONTENT_PATH, song_info['file_name']))

        self.game.trans_wav(song_info)

        del song_info['content']
        db.insert(song_info)

    def song_do_download(self, song_info):
        self.__set_status('正在下载-{}-{} -- 进度： {:.2f}%'.format(
            song_info['song_name'],
            song_info['artist_name'],
            song_info['downloading'] * 100,
        ))

    def song_will_search(self, search_key):
        self.__set_status('接到指令！ 正在搜索： {}'.format(search_key))

    def song_did_search(self, song_info):
        self.__set_status('搜索完成！找到-{}-{} -- 准备下载！'.format(
            song_info['song_name'],
            song_info['artist_name']
        ))

    def order_song(self, namespace):
        asyncio.create_task(self._order_song(namespace))

    async def _order_song(self, namespace):
        async with QqmusicHandler() as musicImpl:
            await musicImpl.single_song(" ".join(namespace.s), self)

    async def _call_shell(self, args, extra):
        await asyncio.create_subprocess_shell(args)
        self.game.did_call_shell(extra)

    def call_shell(self, args, extra=None):
        asyncio.create_task(self._call_shell(args, extra))

    async def run(self):
        async with Csgo(self) as self.game:
            await self.game.start_watch()


async def main():
    await SAOM().run()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
