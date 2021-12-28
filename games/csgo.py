import asyncio
import json
import os
import sys
from io import StringIO

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import utils


cfg = StringIO()
cfg.write('con_logfile saom_logfile.log \n')
cfg.write('alias saom_playlist "exec saom_playlist.cfg" \n')
cfg.write("alias saom_play saom_play_on \n")
cfg.write('alias saom_play_on "alias saom_play saom_play_off; voice_inputfromfile 1; voice_loopback 1; +voicerecord" \n')
cfg.write('alias saom_play_off "-voicerecord; voice_inputfromfile 0; voice_loopback 0; alias saom_play saom_play_on" \n')


class Csgo:

    config_path = os.path.join(os.path.abspath(
        os.path.dirname(os.path.dirname(__file__))), 'config.json')

    def __init__(self, ctx) -> None:
        self.__running = False
        self.get_config()
        self.log_path = os.path.join(utils.get_steam_app_path(
            self.id), self.directory, self.libraryname, "saom_logfile.log")

        self.cfg_path = os.path.join(utils.get_steam_app_path(
            self.id), self.directory, self.ToCfg)

        self.ctx = ctx
        cfg.write('bind {} "exec saom_status" \n'.format(self.ctx.status_key))
        if self.ctx.hold_to_play:
            cfg.write("alias +slam_hold_play slam_play_on \n")
            cfg.write("alias -slam_hold_play slam_play_off \n")
            cfg.write("bind {} +slam_hold_play \n".format(self.ctx.play_key))
        else:
            cfg.write("bind {} slam_play \n".format(self.ctx.play_key))

        with open(os.path.join(self.cfg_path, "saom.cfg"), 'w', encoding='utf8') as f:
            cfg.seek(0)
            f.write(cfg.read())
            cfg.close()

        self.write_status()

    async def __aenter__(self):
        return self

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

    async def start_watch(self) -> None:
        self.__running = True
        open(self.log_path, 'w', encoding='utf8').close()
        log_file = open(self.log_path, 'r', encoding='utf8')
        while self.__running:
            lines = log_file.readlines()
            for line in lines:
                if 'saom' in line.split():
                    line = line.strip('\n').split('saom')[-1].strip()
                    if not line:
                        self.ctx.parse('-c')
                    else:
                        self.ctx.parse(line)

            await asyncio.sleep(0.5)

    async def __aexit__(self, exc_type, exc, tb) -> None:
        pass

    def write_status(self):
        try:
            with open(os.path.join(self.cfg_path, "saom_status.cfg"), 'w', encoding='utf8') as f:
                f.write('say ' + self.ctx.status)
        except PermissionError:
            pass


async def main():
    async with Csgo(None) as csgo:
        pass

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
