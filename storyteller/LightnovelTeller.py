import asyncio
import configparser
import json
import logging
import os
from ast import literal_eval
from difflib import SequenceMatcher

import aiohttp
from pyquery import PyQuery as pq
from SAOM import SAOM
from utils import headers

from storyteller.AbstractTeller import AbstractTeller

logger = logging.getLogger(f'saom.{__name__}')


class LightnovelTeller(AbstractTeller):
    config_path = os.path.join(os.path.abspath(
        os.path.dirname(os.path.dirname(__file__))), 'config.ini')

    def __init__(self, ctx: SAOM):
        self.session = aiohttp.ClientSession()
        self.ctx = ctx
        self.current_line = '轻之国度-还没有轻小说捏'
        self.contents = []
        self.get_config()
        if self.config['enable']['value']:
            asyncio.create_task(self.start())

    @property
    def default_config(self):
        return {
            "name": {'value': "轻国小说展", "type": "str", "disabled": True},
            "classname": {'value': self.__class__.__name__, "type": "str", "disabled": True},
            "enable": {'value': False, 'alias': '开启独轮车', "type": "bool", "disabled": False},
        }

    def get_config(self) -> None:
        config = configparser.ConfigParser()
        config.read(self.config_path, encoding='utf-8')
        self.config = config[f'storyteller.{self.__class__.__name__}']
        self.config = dict(self.config)
        for k, v in self.config.items():
            self.config[k] = literal_eval(v)

    def save_config(self, config: dict) -> None:
        config_parser = configparser.ConfigParser()
        config_parser.read(self.config_path, encoding='utf-8')
        config_parser[f'storyteller.{self.__class__.__name__}'] = config
        with open(self.config_path, 'w', encoding='utf-8') as f:
            config_parser.write(f)

    async def get_content(self, s: str):
        payload = {
            "is_encrypted": 0,
            "platform": "pc",
            "client": "web",
            "sign": "",
            "gz": 0,
            "d": {
                "q": f"{s}",
                "type": 6,
                "page": 1
            }
        }

        logger.debug(f'Search: {s}.')
        self.ctx.game.write_status(f"{self.config['name']['value']} - 正在查找{s}")
        async with self.session.post('https://www.lightnovel.us/proxy/api/search/search-result', json=payload, headers=headers) as resp:
            res = json.loads(await resp.text())
            data = res['data']
            if len(data['list']) == 0:
                self.ctx.game.write_status(
                    f"{self.config['name']['value']} - 没有找到{s}捏。")
                logger.warning(f'No result for {s}.')
                return
            first_piece = data['list'][0]
            novel_title = first_piece['title']
            aid = first_piece['aid']

        self.ctx.game.write_status(
            f"{self.config['name']['value']} - 找到了，正在载入小说..")
        async with self.session.get(f'https://www.lightnovel.us/cn/detail/{aid}', headers=headers) as resp:
            html = await resp.text()
            d = pq(html)
            p = d("#article-main-contents")
            text = p.text()
            text_list = text.split('\n')
            text_list = [i.strip() for i in text_list if i.strip()]
            text_list.reverse()
            self.contents = text_list
            self.current_line = f"开始说书 - {self.config['name']['value']} - {novel_title}"
            self.ctx.game.write_story(self.current_line)

        self.ctx.game.write_status(
            f"{self.config['name']['value']} - 载入完毕！可以说书！")
        logger.debug(f'Loaded : {novel_title}.')

    async def start(self):
        self.__running = True
        self.ctx.game.write_story(self.current_line)
        logger.debug(f'start.')

    def stop(self):
        self.__running = False
        logger.debug('stop.')

    def parse(self, line: str):
        if not self.__running:
            return
        if 'saom' in line:
            line = line.split('saom')[-1]
            namespace = self.ctx.parser.parse_line(line)
            if namespace.pos0 == 'n':
                asyncio.create_task(self.get_content(' '.join(namespace.pos1)))
                return
        asyncio.create_task(self.compare(line))

    async def compare(self, line):
        if line.count('：') == 1:
            line = line.split('：')[-1]
        elif line.count('：') > 1:
            line = line[line.index('：'):].strip('：')

        r = SequenceMatcher(lambda x: x in " ", line.strip('\n'),
                            self.current_line).ratio()

        if r > 0.6:
            line = self.contents.pop() if self.contents else self.current_line
            self.current_line = line.strip()[:80]
            self.current_line.replace('"', '\'')
            self.ctx.game.write_story(self.current_line)

    def __del__(self):
        asyncio.create_task(self.session.close())


if __name__ == '__main__':
    ...
