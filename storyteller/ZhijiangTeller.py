import asyncio
import configparser
import json
import logging
import os
import random
from ast import literal_eval
from collections import deque
from difflib import SequenceMatcher

import aiohttp
from SAOM import SAOM

from storyteller.AbstractTeller import AbstractTeller

logger = logging.getLogger(f'saom.{__name__}')


class ZhijiangTeller(AbstractTeller):
    config_path = os.path.join(os.path.abspath(
        os.path.dirname(os.path.dirname(__file__))), 'config.ini')

    def __init__(self, ctx: SAOM):
        self.session = aiohttp.ClientSession()
        self.ctx = ctx
        self.current_line = ''
        self.page_order = list(range(1, 1035))
        random.shuffle(self.page_order)
        self.page_order.pop()
        self.contents = deque()
        self.get_config()
        if self.config['enable']['value']:
            asyncio.create_task(self.start())

    @property
    def default_config(self):
        return {
            "name": {'value': "枝江作文展", "type": "str", "disabled": True},
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

    async def get_content(self):
        page = self.page_order.pop()
        async with self.session.get(f'https://asoulcnki.asia/v1/api/ranking/?pageNum={page}&timeRangeMode=0&sortMode=0&pageSize=10') as resp:
            res = json.loads(await resp.text())

            for i in res['data']['replies']:
                content = i['content'].split('\n')

                content = filter(lambda x: x, content)
                content = deque(content)
                piece = {'author': i['m_name'], 'content': content}
                self.contents.append(piece)
        logger.debug(f'Loaded page {page}.')

    async def check(self):
        if len(self.contents) < 2:
            await self.get_content()

    async def start(self):
        self.get_config()
        self.__running = True
        await self.check()
        self.current_line = f"开始说书 - {self.config['name']['value']}"
        self.ctx.game.write_story(self.current_line)
        logger.debug(f'start.')

    def stop(self):
        self.__running = False
        logger.debug('stop.')

    def parse(self, line: str):
        if self.__running:
            asyncio.create_task(self.compare(line))

    async def compare(self, line):
        if line.count('：') == 1:
            line = line.split('：')[-1]
        elif line.count('：') > 1:
            line = line[line.index('：'):].strip('：')

        r = SequenceMatcher(lambda x: x in " ", line.strip('\n'),
                            self.current_line).ratio()

        if r > 0.6:
            if not len(self.contents[0]['content']):
                self.contents.popleft()

            line = self.contents[0]['content'].popleft()
            self.current_line = line.strip()[:80]
            while not self.current_line:
                line = self.contents[0]['content'].popleft()
                self.current_line = line.strip()[:80]
            self.current_line.replace('"', '\'')
            self.ctx.game.write_story(self.current_line)
            await self.check()

    def __del__(self):
        asyncio.create_task(self.session.close())


if __name__ == '__main__':
    ...
