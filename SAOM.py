import asyncio
import json
from io import BytesIO
from tinydb import TinyDB, where
import os
import importlib

from argparser.DefaultParser import DefaultParser

DB_PATH = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), 'content\songs.json')
CONTENT_PATH = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), 'content')
CONFIG_PATH = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), 'config.json')


db = TinyDB(DB_PATH)


class SAOM:
    def __init__(self):
        self.parser = DefaultParser()
        self.chosen_game = 'csgo'
        self.hold_to_play = False
        self.play_key = 'N'
        self.status_key = 'L'
        self.game = None
        self.__set_status("还没有点歌捏 点歌方式: 聊天框内输入 saom -s 歌名")

    def set_game(self):
        with open(CONFIG_PATH, 'r', encoding='utf8') as f:
            games: json = json.load(f)['games']

        for (k, v) in games.items():
            if k == self.chosen_game:
                module = importlib.import_module(
                    'game.{0}'.format(v['className']))
                self.game = getattr(module, v['className'])(self)
                break

    def set_status(self, message):
        self.__set_status(message)

    def __set_status(self, message):
        self.status = 'SAOM-在线点歌 -已开源- ' + message
        if self.game:
            self.game.write_status()

    def parse(self, line):
        namespace = self.parser.parse_line(line)
        self.order_song(namespace)

    def no_copyright(self, info):
        self.__set_status('找到了{}-{}，但是{}没有版权（；´д｀）ゞ'.format(
            info['song_name'],
            info['artist_name'],
            info['handler_name']
        ))

    def song_did_download(self, song_info):
        with open(os.path.join(CONTENT_PATH, song_info['file_name']), 'wb') as f:
            f.write(song_info['content'].read())
            print(os.path.join(CONTENT_PATH, song_info['file_name']))

        self.game.trans_wav(song_info)

        del song_info['content']
        db.insert(song_info)

    def song_do_download(self, song_info):
        self.__set_status(' - {} - 正在下载-{}-{} -- 进度： {:.2f}%'.format(
            song_info['handler_name'],
            song_info['song_name'],
            song_info['artist_name'],
            song_info['downloading'] * 100,
        ))

    def song_will_search(self, search_key):
        self.__set_status('接到指令！ 正在搜索： {}'.format(search_key))

    def song_did_search(self, song_info):
        self.__set_status(' - {} - 搜索完成！找到-{}-{} -- 准备下载！'.format(
            song_info['handler_name'],
            song_info['song_name'],
            song_info['artist_name']
        ))

    def order_song(self, namespace):
        asyncio.create_task(self._order_song(namespace))

    async def _order_song(self, namespace):
        handler_shortcut: str = namespace.m
        with open(CONFIG_PATH, 'r', encoding='utf8') as f:
            handlers: json = json.load(f)['handler']

        for (k, v) in handlers.items():
            if handler_shortcut == v['shortcut']:
                module = importlib.import_module(
                    'handler.{0}'.format(v['handlerName']))
                handler = getattr(module, v['handlerName'])
                break

        async with handler(self) as handler:
            await handler.single_song(" ".join(namespace.s))

    async def _call_shell(self, args, extra):
        await asyncio.create_subprocess_shell(args)
        self.game.did_call_shell(extra)

    def call_shell(self, args, extra=None):
        asyncio.create_task(self._call_shell(args, extra))

    async def run(self):
        self.set_game()
        await self.game.start_watch()


async def main():
    s = SAOM()
    await s.run()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
