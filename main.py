import asyncio
import configparser
import json
import logging
import os
import sys
import time
from ast import literal_eval

import PySimpleGUI as sg

from SAOM import SAOM
from utils import get_steam_app_path

logger = logging.getLogger('saom')
logger.setLevel(logging.DEBUG)
ch = logging.FileHandler('saom.log', encoding='utf8')
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(name)s:%(levelname)s:%(asctime)s:%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
ch.setFormatter(formatter)
logger.addHandler(ch)

CONFIG_PATH = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), 'config.ini')
folder_path = os.path.dirname(os.path.realpath(__file__))
ffmpeg_path = os.path.join(folder_path, 'ffmpeg.exe')

sg.theme('Default1')


def open_config_window(config_str: str):
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH, encoding='utf-8')
    c = config[config_str]
    layout = []
    for k, v in c.items():
        v = literal_eval(v)
        alias = v.get('alias', k)
        if v['type'] == 'str':
            layout.append([sg.Text(alias)])
            layout.append([sg.Input(default_text=v['value'],
                                    key=f'-{k}-', disabled=v['disabled'])])
        if v['type'] == 'multiline':
            layout.append([sg.Text(alias)])
            layout.append([sg.Multiline(default_text=v['value'],
                                        key=f'-{k}-', disabled=v['disabled'])])
        elif v['type'] == 'bool':
            layout.append([sg.Checkbox(default=v['value'],
                                       text=alias, key=f'-{k}-', disabled=v['disabled'])])

    layout.append([sg.Button('保存', key='-SAVECONFIG-'),
                   sg.Button('取消', key='-CANCEL-', ), ])
    w = sg.Window(f"配置{config_str}", layout, modal=True)

    event, values = w.read()

    if event in (sg.WIN_CLOSED, '-CANCEL-'):
        pass
    elif event == '-SAVECONFIG-':
        logger.debug(f'{__file__}:{config_str} save config:{values}')
        for k, v in values.items():
            _ = literal_eval(config[config_str][k.strip('-')])
            _['value'] = v
            config[config_str][k.strip('-')] = str(_)
        with open(CONFIG_PATH, 'w', encoding='utf8') as f:
            config.write(f)

        sg.popup('载入成功，请在游戏内发送`exec saom`指令ヾ(≧▽≦*)',
                 title='', auto_close=True, auto_close_duration=2)

    w.close()


if not os.path.exists(ffmpeg_path):
    sg.popup('ffmpeg不存在，请执行第一次运行脚本', title='ffmpeg不存在')
    sys.exit()


config = configparser.ConfigParser()
config.read(CONFIG_PATH, encoding='utf-8')
_ = config.sections()
section_map = {}
games = []
handlers = []
storytellers = []
for i in _:
    name = literal_eval(config[i]['name'])['value']
    if i.startswith('game'):
        games.append(name)
    elif i.startswith('handler'):
        handlers.append(name)
    elif i.startswith('storyteller'):
        storytellers.append(name)
    section_map[name] = i


layout = [
    [sg.Text("请选择游戏：")],
    [sg.Combo(games, key='-GAME-', expand_x=True,
              readonly=True, default_value=games[0]),
     sg.Button('设置', key='-GAMECONFIG-')],

    [sg.HorizontalSeparator(color='#CCC')],

    [sg.Text("请选择默认音乐api：")],
    [sg.Combo(handlers, key='-HANDLER-', expand_x=True,
              readonly=True, default_value=handlers[0]),
     sg.Button('设置', key='-HANDLERCONFIG-')],

    [sg.HorizontalSeparator(color='#CCC')],

    [sg.Text("请选择默认独轮车：")],
    [sg.Combo(storytellers, key='-STORYTELLER-', expand_x=True,
              readonly=True, default_value=storytellers[0]),
     sg.Button('设置', key='-STORYTELLERCONFIG-')],

    [sg.HorizontalSeparator(color='#CCC')],

    [sg.Button('启动', key='-START-'),
     sg.Button('停止', key='-STOP-', disabled=True),
     sg.Button('重启', key='-RESTART-', disabled=True, visible=False),
     sg.Button('cfg目录', key='-OPENCFGFOLDER-'),
     sg.Button('gamelog', key='-OPENGAMELOG-'),
     ],

]

window = sg.Window('说唱脚本v1.0', layout, size=(400, 600))

saom = SAOM()


async def main():
    while True:
        event, values = window.read(timeout=0)
        await asyncio.sleep(0.01)

        if event == sg.WIN_CLOSED:
            break
        elif event == '-GAMECONFIG-':
            open_config_window(section_map[values['-GAME-']])
            layout[-1][2].click()
        elif event == '-HANDLERCONFIG-':
            open_config_window(section_map[values['-HANDLER-']])
            layout[-1][2].click()
        elif event == '-STORYTELLERCONFIG-':
            open_config_window(section_map[values['-STORYTELLER-']])
            layout[-1][2].click()
        elif event == '-OPENCFGFOLDER-':
            config = configparser.ConfigParser()
            config.read(CONFIG_PATH, encoding='utf-8')
            _game = config[section_map[values['-GAME-']]]
            _game = dict(_game)
            for k, v in _game.items():
                _game[k] = literal_eval(v)
            cfg_path = os.path.join(get_steam_app_path(_game['id']['value']),
                                    _game['directory']['value'], _game['tocfg']['value'], 'saom.cfg').replace('/', '\\')
            os.system(f'explorer /select,"{cfg_path}"')
        elif event == '-OPENGAMELOG-':
            config = configparser.ConfigParser()
            config.read(CONFIG_PATH, encoding='utf-8')
            _game = config[section_map[values['-GAME-']]]
            _game = dict(_game)
            for k, v in _game.items():
                _game[k] = literal_eval(v)
            game_log_path = os.path.join(get_steam_app_path(_game['id']['value']),
                                         _game['directory']['value'], _game['libraryname']['value'], "saom_logfile.log").replace('/', '\\')
            os.system(f'explorer /select,"{game_log_path}"')
        elif event == '-START-':
            saom.start(section_map[values['-GAME-']],
                       section_map[values['-HANDLER-']],
                       section_map[values['-STORYTELLER-']])

            window.set_title('说唱脚本v1.0 - 正在运行')
            window['-START-'].update(disabled=True)
            window['-RESTART-'].update(disabled=False)
            window['-STOP-'].update(disabled=False)
        elif event == '-STOP-':
            window.set_title('说唱脚本v1.0')
            window['-START-'].update(disabled=False)
            window['-RESTART-'].update(disabled=True)
            window['-STOP-'].update(disabled=True)
            saom.stop()
        elif event == '-RESTART-':
            saom.stop()
            saom.start(section_map[values['-GAME-']],
                       section_map[values['-HANDLER-']],
                       section_map[values['-STORYTELLER-']])

    window.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
