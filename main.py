from asyncore import loop
import json
import os
import sys

import PySimpleGUI as sg
from async_timeout import asyncio

from SAOM import SAOM

sg.theme('Default1')

CONFIG_PATH = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), 'config.json')

with open(CONFIG_PATH, encoding='utf8') as f:
    config = json.load(f)
    games = list(config['games'].keys())
    handlers = [i['name'] + " - " + i['shortcut']
                for i in config['handler'].values()]
    tellers = [i['name'] for i in config['teller'].values()]

layout = [
    [sg.Text("请选择游戏：")],
    [sg.Combo(games, key='-GAME-', expand_x=True,
              readonly=True, default_value=games[0])],

    [sg.Text("信息显示键(可自定义)："),
        sg.Combo(["N", "P", "L", "J"], key='-STATUSKEY-', size=(10, 10), default_value='L')],
    [sg.HorizontalSeparator(color='#CCC')],

    [sg.Text("请选择默认音乐api：")],
    [sg.Combo(handlers, key='-HANDLER-', expand_x=True,
              readonly=True, default_value=handlers[0])],

    [sg.Checkbox("按住键盘播放模式", key='-HOLD-', default=False),
     sg.Text("播放键(可自定义)："),
     sg.Combo(["N", "P", "L", "J"], key='-PLAYKEY-', expand_x=True, default_value='N')],

    [sg.HorizontalSeparator(color='#CCC')],

    [sg.Text("请选择默认独轮车：")],
    [sg.Combo(tellers, key='-STORYTELLER-', expand_x=True,
              readonly=True, default_value=tellers[0])],

    [sg.Text("独轮车默认状态："),
     sg.Combo(["关闭", "开启", ], key='-STORYTELLERENABLE-', size=(10, 10), default_value='关闭', readonly=True)],

    [sg.Text("独轮车绑定方向键："),
     sg.Combo(["关闭", "开启", ], key='-TELLBYWASD-',
              size=(10, 10), default_value='开启', readonly=True),
     sg.Text("说书键："),
     sg.Combo(["N", "P", "L", "J"], key='-TELLKEY-', expand_x=True, default_value='P')],

    [sg.HorizontalSeparator(color='#CCC')],

    [sg.Button('启动', key='-START-'),
     sg.Button('停止', key='-STOP-', disabled=True)],

]

window = sg.Window('说唱脚本', layout, size=(400, 600))

saom = SAOM()


async def main():
    while True:
        event, values = window.read(timeout=0)
        await asyncio.sleep(0.01)

        if event == sg.WIN_CLOSED:
            break
        elif event == '-START-':
            saom.handler_shortcut = values['-HANDLER-'].split(' ')[-1]
            saom.status_key = values['-STATUSKEY-']
            saom.play_key = values['-PLAYKEY-']
            saom.tell_key = values['-TELLKEY-']
            saom.hold_to_play = values['-HOLD-']
            saom.tell_by_wasd = True if values['-TELLBYWASD-'] == '开启' else False
            saom.teller_enable = True if values['-STORYTELLERENABLE-'] == '开启' else False

            saom.set_game(values['-GAME-'])
            saom.set_teller(values['-STORYTELLER-'])
            saom.run()
            window.set_title('说唱脚本 - 正在运行')
            window['-START-'].update(disabled=True)
            window['-STOP-'].update(disabled=False)
        elif event == '-STOP-':
            window.set_title('说唱脚本')
            window['-START-'].update(disabled=False)
            window['-STOP-'].update(disabled=True)
            saom.stop()

    window.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
