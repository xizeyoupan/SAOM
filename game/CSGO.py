from ast import literal_eval
import asyncio
import json
import logging
import os
import sys
import configparser
from io import StringIO
from SAOM import SAOM
from game.DefaultGame import DefaultGame
from utils import get_value, get_steam_app_path

logger = logging.getLogger(f"saom.{__name__}")
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
CONTENT_PATH = os.path.join(PROJECT_PATH, 'content')


class CSGO(DefaultGame):

    config_path = os.path.join(os.path.abspath(
        os.path.dirname(os.path.dirname(__file__))), 'config.ini')

    def __init__(self, ctx: SAOM) -> None:
        self.get_config()
        self.cfg = StringIO()
        self.cfg.write('con_logfile saom_logfile.log\n')
        self.cfg.write('alias saom_playlist "exec saom_playlist.cfg"\n')
        self.cfg.write("alias saom_play saom_play_on\n")
        self.cfg.write(
            'alias saom_play_on "alias saom_play saom_play_off; voice_inputfromfile 1; voice_loopback 1; +voicerecord"\n')
        self.cfg.write(
            'alias saom_play_off "-voicerecord; voice_inputfromfile 0; voice_loopback 0; alias saom_play saom_play_on"\n')

        self.__running = False
        self.log_path = os.path.join(get_steam_app_path(self.config['id']['value']),
                                     self.config['directory']['value'], self.config['libraryname']['value'], "saom_logfile.log")

        self.cfg_path = os.path.join(get_steam_app_path(self.config['id']['value']),
                                     self.config['directory']['value'], self.config['tocfg']['value'])
        self.wav_path = os.path.join(
            get_steam_app_path(self.config['id']['value']),
            self.config['directory']['value'],
            'voice_input.wav')

        self.ctx = ctx
        self.binds: str = self.config['binds']['value']

        if self.ctx.handler.config['holdtoplay']['value']:
            self.cfg.write("alias +saom_hold_play saom_play_on\n")
            self.cfg.write("alias -saom_hold_play saom_play_off\n")
            self.binds = self.binds.replace('播放音乐', '+saom_hold_play')
        else:
            self.binds = self.binds.replace('播放音乐', '+saom_play')

        self.cfg.write(self.binds)

        with open(os.path.join(self.cfg_path, "saom.cfg"), 'w', encoding='utf8') as f:
            self.cfg.seek(0)
            f.write(self.cfg.read())
            self.cfg.close()

        asyncio.create_task(self.start())
        self.write_status('启动成功！')

    @ property
    def default_config(self):
        return {
            "name": {'value': "csgo", "type": "str", "disabled": True},
            "classname": {'value': self.__class__.__name__, "type": "str", "disabled": True},
            "id": {'value': "730", "type": "str", "disabled": True},
            "directory": {'value': "common\\Counter-Strike Global Offensive\\", "type": "str", "disabled": True},
            "tocfg": {'value': "csgo\\cfg\\", "type": "str", "disabled": True},
            "libraryname": {'value': "csgo\\", "type": "str", "disabled": True},
            "statuskey": {'value': "exec saom_status", "alias": "信息显示绑定指令", "type": "str", "disabled": True},
            "tellkey": {'value': "exec saom_story", "alias": "说书绑定指令", "type": "str", "disabled": True},
            "playkey": {'value': "播放音乐", "alias": "音乐播放绑定指令\nsaom_play/saom_hold_play (不按住播放/按住播放)\n下面绑定时输入`播放音乐`即可", "type": "str", "disabled": True},
            "binds": {'value': 'bind "p" "exec saom_story"\nbind "l" "exec saom_status"\nbind "n" "播放音乐"\n', "alias": "绑定指令", "type": "multiline", "disabled": False},
        }

    def get_config(self) -> None:
        config = configparser.ConfigParser()
        config.read(self.config_path, encoding='utf-8')
        self.config = config[f'game.{self.__class__.__name__}']
        self.config = dict(self.config)
        for k, v in self.config.items():
            self.config[k] = literal_eval(v)

    def save_config(self, config: dict) -> None:
        config_parser = configparser.ConfigParser()
        config_parser.read(self.config_path, encoding='utf-8')
        config_parser[f'game.{self.__class__.__name__}'] = config
        with open(self.config_path, 'w', encoding='utf-8') as f:
            config_parser.write(f)

    def stop(self) -> None:
        self.__running = False
        self.log_file.close()
        open(os.path.join(self.cfg_path, "saom_story.cfg"), 'w').close()
        open(os.path.join(self.cfg_path, "saom_status.cfg"), 'w').close()
        logger.debug('stop.')

    async def start(self) -> None:
        logger.debug('start.')
        self.__running = True
        open(self.log_path, 'w', encoding='utf8').close()

        self.log_file = open(self.log_path, 'r', encoding='utf8')
        while self.__running:
            lines = self.log_file.readlines()
            for line in lines:
                if 'SAOM - 说唱脚本- ddl.ink/saom' in line:
                    continue
                self.ctx.handler.prase(line)
                self.ctx.storyteller.parse(line)
            await asyncio.sleep(0.1)

    def write_status(self, mesage: str, extra: bool = True):
        try:
            with open(os.path.join(self.cfg_path, "saom_status.cfg"), 'w', encoding='utf8') as f:
                if extra:
                    f.write(f'say "SAOM - 说唱脚本- ddl.ink/saom  {mesage}"')
                else:
                    f.write(f'say "{mesage}"')
        except PermissionError:
            pass

    def write_story(self, line: str):
        try:
            with open(os.path.join(self.cfg_path, "saom_story.cfg"), 'w', encoding='utf8') as f:
                f.write(f'say "{line}"')
        except PermissionError:
            pass

    async def trans_wav(self, song_info):
        args = '{}/ffmpeg.exe -y -i "{}" -f wav -bitexact -map_metadata -1 -vn -acodec pcm_s16le -ar {} -ac {} "{}"'.format(
            PROJECT_PATH,
            os.path.join(CONTENT_PATH, song_info['file_name']),
            22050,
            1,
            self.wav_path
        )

        await asyncio.create_subprocess_shell(args)
        logger.debug(f'{song_info["file_name"]} to wav.')


if __name__ == '__main__':
    CSGO(SAOM())
