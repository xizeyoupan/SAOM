import asyncio
import configparser
import functools
import logging
import os
import uuid
from ast import literal_eval
from difflib import SequenceMatcher

from SAOM import SAOM
from utils import get_steam_app_path

from storyteller.AbstractTeller import AbstractTeller

logger = logging.getLogger(f'saom.{__name__}')


class LocalTeller(AbstractTeller):
    config_path = os.path.join(os.path.abspath(
        os.path.dirname(os.path.dirname(__file__))), 'config.ini')

    def __init__(self, ctx: SAOM):
        self.ctx = ctx
        self.get_config()
        if self.config['enable']['value']:
            asyncio.create_task(self.start())

    def init_customised(self):
        for i in range(1, 10):
            statement = self.config[f'piece{i}']['value']
            if not statement:
                continue
            statements = statement.split()

            if statements[0] == 'audio':
                say_words = statements[2] if len(
                    statements) > 2 else f'转码自定义音频{i}'
                cfg = f'echo "{self.uuid} piece{i}"\nsay "{say_words}"'
            elif statements[0] == 'say':
                cfg = f'say "{statements[-1][:80]}"'

            with open(os.path.join(self.cfg_path, f'saom_localteller_piece{i}.cfg'), 'w', encoding='utf-8') as f:
                f.write(cfg)

    @property
    def default_config(self):
        return {
            "name": {'value': "本地作文展", "type": "str", "disabled": True},
            "classname": {'value': self.__class__.__name__, "type": "str", "disabled": True},
            "enable": {'value': False, 'alias': '开启独轮车', "type": "bool", "disabled": False},
            "localtext": {'value': 'storyteller/Insult.txt', 'alias': '本地文本，支持相对路径和绝对路径', "type": "str", "disabled": False},
            "piece1": {'value': '', 'alias': '自定义动作1，用法请看文档', "type": "str", "disabled": False},
            "piece2": {'value': '', 'alias': '自定义动作2，用法请看文档', "type": "str", "disabled": False},
            "piece3": {'value': '', 'alias': '自定义动作3，用法请看文档', "type": "str", "disabled": False},
            "piece4": {'value': '', 'alias': '自定义动作4，用法请看文档', "type": "str", "disabled": False},
            "piece5": {'value': '', 'alias': '自定义动作5，用法请看文档', "type": "str", "disabled": False},
            "piece6": {'value': '', 'alias': '自定义动作6，用法请看文档', "type": "str", "disabled": False},
            "piece7": {'value': '', 'alias': '自定义动作7，用法请看文档', "type": "str", "disabled": False},
            "piece8": {'value': '', 'alias': '自定义动作8，用法请看文档', "type": "str", "disabled": False},
            "piece9": {'value': '', 'alias': '自定义动作9，用法请看文档', "type": "str", "disabled": False},
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

    async def start(self):
        self.__running = True
        self.get_config()
        self.cfg_path = os.path.join(get_steam_app_path(self.ctx.game.config['id']['value']),
                                     self.ctx.game.config['directory']['value'], self.ctx.game.config['tocfg']['value'])
        self.uuid = uuid.uuid4().hex
        self.init_customised()

        self.current_line = f"开始说书 - {self.config['name']['value']}"
        self.ctx.game.write_story(self.current_line)
        with open(self.config['localtext']['value'], 'r', encoding='utf-8') as f:
            self.contents = f.readlines()
            self.contents = [x.strip() for x in self.contents if x.strip()]
        self.contents.reverse()
        logger.debug(f'start.')

    def stop(self):
        self.__running = False
        for i in range(1, 10):
            open(os.path.join(self.cfg_path, f'saom_localteller_piece{i}.cfg'),
                 'w', encoding='utf-8').close()
        logger.debug('stop.')

    def parse(self, line: str):
        if not self.__running:
            return
        line = line.strip()
        if self.uuid in line:
            logger.debug(f'Found statement: {line}')
            piece = line.split()[-1]
            songinfo = {'file_name': self.config[piece]['value'].split()[1]}
            task = asyncio.create_task(
                self.ctx.game.trans_wav(songinfo, handler=False))
            task.add_done_callback(
                functools.partial(self.ctx.game.write_status, '本地说书自定义音频转码完成，可以开始播放了(≧∇≦)ﾉ'))
            task.add_done_callback(functools.partial(
                logger.debug, f"Switch to {songinfo['file_name']} successfully."))
        else:
            asyncio.create_task(self.compare(line))

    async def compare(self, line):
        if line.count('：') == 1:
            line = line.split('：')[-1]
        elif line.count('：') > 1:
            line = line[line.index('：'):].strip('：')

        r = SequenceMatcher(lambda x: x in " ", line.strip('\n'),
                            self.current_line).ratio()

        if r > 0.6:
            line = self.contents.pop()
            self.current_line = line.strip()[:80]
            self.current_line.replace('"', '\'')
            self.ctx.game.write_story(self.current_line)


if __name__ == '__main__':
    ...
