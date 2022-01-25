import asyncio
import json
import os
import sys
from io import StringIO
from SAOM import SAOM

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
CONTENT_PATH = os.path.join(PROJECT_PATH, 'content')

import game.utils as utils
from game.DefaultGamer import DefaultGamer


class CSGO(DefaultGamer):

    config_path = os.path.join(os.path.abspath(
        os.path.dirname(os.path.dirname(__file__))), 'config.json')

    def __init__(self, ctx: SAOM) -> None:
        self.cfg = StringIO()
        self.cfg.write('con_logfile saom_logfile.log \n')
        self.cfg.write('alias saom_playlist "exec saom_playlist.cfg" \n')
        self.cfg.write("alias saom_play saom_play_on \n")
        self.cfg.write(
            'alias saom_play_on "alias saom_play saom_play_off; voice_inputfromfile 1; voice_loopback 1; +voicerecord" \n')
        self.cfg.write(
            'alias saom_play_off "-voicerecord; voice_inputfromfile 0; voice_loopback 0; alias saom_play saom_play_on" \n')

        self.__running = False
        self.get_config()
        self.log_path = os.path.join(utils.get_steam_app_path(
            self.id), self.directory, self.libraryname, "saom_logfile.log")

        self.cfg_path = os.path.join(utils.get_steam_app_path(
            self.id), self.directory, self.ToCfg)
        self.wav_path = os.path.join(
            utils.get_steam_app_path(self.id),
            self.directory,
            'voice_input.wav')

        self.ctx = ctx

        self.cfg.write(
            'bind {} "exec saom_story" \n'.format(self.ctx.tell_key))
        self.cfg.write(
            'bind {} "exec saom_status" \n'.format(self.ctx.status_key))
        if self.ctx.hold_to_play:
            self.cfg.write("alias +saom_hold_play saom_play_on \n")
            self.cfg.write("alias -saom_hold_play saom_play_off \n")
            self.cfg.write(
                "bind {} +saom_hold_play \n".format(self.ctx.play_key))
        else:
            self.cfg.write("bind {} saom_play \n".format(self.ctx.play_key))

        if self.ctx.tell_by_wasd and self.ctx.teller_enable:
            self.cfg.write('bind w "+forward;exec saom_story;" \n')
            self.cfg.write('bind a "+moveleft;exec saom_story;" \n')
            self.cfg.write('bind s "+back;exec saom_story;" \n')
            self.cfg.write('bind d "+moveright;exec saom_story;" \n')
        else:
            self.cfg.write('bind w "+forward;" \n')
            self.cfg.write('bind a "+moveleft;" \n')
            self.cfg.write('bind s "+back;" \n')
            self.cfg.write('bind d "+moveright;" \n')

        with open(os.path.join(self.cfg_path, "saom.cfg"), 'w', encoding='utf8') as f:
            self.cfg.seek(0)
            f.write(self.cfg.read())
            self.cfg.close()

        self.write_status()

    def get_config(self) -> None:
        with open(self.config_path, 'r', encoding='utf8') as f:
            config: json = json.load(f)['games']['csgo']
            self.directory = config['directory']
            self.ToCfg = config['ToCfg']
            self.libraryname = config['libraryname']
            self.exename = config['exename']
            self.id = config['id']
            self.name = config['name']

    def stop_watch(self) -> None:
        self.__running = False
        self.log_file.close()

    async def start_watch(self) -> None:
        print('start watch')
        self.__running = True
        open(self.log_path, 'w', encoding='utf8').close()

        self.log_file = open(self.log_path, 'r', encoding='utf8')
        while self.__running:
            lines = self.log_file.readlines()
            for line in lines:
                if 'saom' in line.split():
                    line = line.strip('\n').split('saom')[-1].strip()
                    if line and '歌名' not in line:
                        self.ctx.parse(line)
                else:
                    self.ctx.parse(line)
            await asyncio.sleep(0.05)

        print('SAOM: CSGO watcher stopped.')

    def write_status(self):
        try:
            with open(os.path.join(self.cfg_path, "saom_status.cfg"), 'w', encoding='utf8') as f:
                f.write(f'say "{self.ctx.status}"')
        except PermissionError:
            pass

    def write_story(self, line):
        try:
            with open(os.path.join(self.cfg_path, "saom_story.cfg"), 'w', encoding='utf8') as f:
                f.write(f'say "{line}"')
        except PermissionError:
            pass

    def trans_wav(self, song_info):
        self.ctx.set_status(
            ' - {} 下载完成！正在转换为wav文件...'.format(song_info['song_name']))

        self.ctx.call_shell('{}/ffmpeg.exe -y -i "{}" -f wav -bitexact -map_metadata -1 -vn -acodec pcm_s16le -ar {} -ac {} "{}"'.format(
            PROJECT_PATH,
            os.path.join(CONTENT_PATH, song_info['file_name']),
            22050,
            1,
            self.wav_path
        ),
            song_info
        )

    def did_call_shell(self, extra):
        self.ctx.set_status('当前歌曲-{}-{}'.format(
            extra['song_name'],
            extra['artist_name']))
