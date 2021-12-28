import asyncio
from games.csgo import Csgo
from musicImpl import *
from io import BytesIO
from musicImpl import NeteaseImpl
from parse import defaultparse
from tinydb import TinyDB, where
import os
DB_PATH = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), 'content\songs.json')
db = TinyDB(DB_PATH)


class SAOM:
    def __init__(self):
        self.parser = defaultparse.DefaultParser(self)
        self.locale = 'en'
        self.game_name = 'csgo'
        self.music_impl = 'NeteaseImpl'
        self.hold_to_play = False
        self.play_key = 'N'
        self.status_key = 'L'
        self.game = None
        self.__set_status("还没有点歌捏")

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
        self.__set_status('当前歌曲-{}-{}'.format(
            song_info['song_name'],
            song_info['artist_name']))

        del song_info['content']

        db.insert(song_info)

    def song_do_download(self, song_info):
        self.__set_status('正在下载-{}-{} -- 进度： {:.2f}%'.format(
            song_info['song_name'],
            song_info['artist_name'],
            song_info['downloading'] * 100,
        ))

    def song_will_search(self, search_key):
        self.__set_status('接到指令！ 正在搜索-{}'.format(search_key))

    def song_did_search(self, song_info):
        self.__set_status('搜索完成！找到-{}-{} -- 正在下载！'.format(
            song_info['song_name'],
            song_info['artist_name']
        ))

    async def ordersong(self, namespace):
        async with NeteaseImpl.NeteaseImpl() as musicImpl:
            await musicImpl.single_song(" ".join(namespace.s), self)

    async def run(self):
        async with Csgo(self) as self.game:
            await self.game.start_watch()


async def main():
    await SAOM().run()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
