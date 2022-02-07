import os
import shutil
import sys
import tempfile
import zipfile
from urllib.request import Request, urlopen

import PySimpleGUI as sg

sg.theme('BluePurple')

folder_path = os.path.dirname(os.path.realpath(__file__))
ffmpeg_path = os.path.join(folder_path, 'ffmpeg.exe')

if os.path.exists(ffmpeg_path):
    layout = [[sg.Text('已经找到了ffmpeg(≧∇≦)ﾉ) 重新下载？')],
              [sg.Submit("重下"), sg.Cancel("取消")]]

    window = sg.Window('哈哈', layout)
    event, values = window.read()
    if event == '取消':
        window.close()
        sys.exit()
    window.close()

url = sg.popup_get_text("下载加速由❤提供\n或在下方输入自定义下载地址", title="哈哈",
                        default_text="https://saom.saom.workers.dev/https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-n5.0-latest-win64-lgpl-5.0.zip")
if not url:
    sys.exit()

layout = [[sg.Text('下载进度：', key="-TEXT-"), sg.Text(key='-RATE-')],
          [sg.ProgressBar(1000, orientation='h', size=(20, 20), key='-PROG-')],
          [sg.Exit()]
          ]

window = sg.Window('下载中', layout, finalize=True, size=(250, 100))
tmp_file = tempfile.NamedTemporaryFile()


def download():
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"}
    req = Request(url=url, headers=headers)
    with urlopen(req) as response:
        CHUNK = 64 * 1024
        content_length = int(response.info().get('Content-Length'))
        print(content_length)
        now = 0.0

        while True:
            chunk = response.read(CHUNK)
            if not chunk:
                break
            tmp_file.write(chunk)
            now += len(chunk)
            progress = int(now / content_length * 1000)
            # print(progress)
            window['-PROG-'].update(progress)
            window['-RATE-'].update(
                f'{now / 1024 / 1024:.2f}MB/{content_length / 1024 / 1024:.2f}MB')


window.perform_long_operation(download, '-OPERATION DONE-')
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    elif event == '-OPERATION DONE-':
        window['-TEXT-'].update("正在解压")
        zip_file = zipfile.ZipFile(tmp_file)
        zip_file.extract(
            "ffmpeg-n5.0-latest-win64-lgpl-5.0/bin/ffmpeg.exe", folder_path)
        shutil.move(os.path.join(folder_path,
                    "ffmpeg-n5.0-latest-win64-lgpl-5.0/bin/ffmpeg.exe"), ffmpeg_path)
        shutil.rmtree(os.path.join(folder_path,
                                   "ffmpeg-n5.0-latest-win64-lgpl-5.0"))
        zip_file.close()
        tmp_file.close()
        sg.popup("Done!\n(●'◡'●)")
        break
window.close()
