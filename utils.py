import os
import random
import re
import winreg
from ast import literal_eval
from typing import Any

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"}


def get_steam_path():
    steam_path = None

    try:
        if('PROGRAMFILES(X86)' in os.environ):
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 r'SOFTWARE\WOW6432Node\Valve\Steam')
        else:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 r'SOFTWARE\Valve\Steam')
        steam_path = winreg.QueryValueEx(key, 'InstallPath')[0]
    except FileNotFoundError:
        print('Steam not installed.')
    finally:
        key.Close()

    return steam_path


def get_steam_app_path(id) -> str:
    vdf_path = get_steam_path() + '\\steamapps\\libraryfolders.vdf'

    with open(vdf_path, 'r', encoding='utf8') as f:
        data = "".join(f.read().split('\n'))

    pattern = r'"path".*([a-zA-Z]:.*)"{}"'.format(id)
    data = re.findall(pattern, data)[-1]
    path: str = data.split('\t\t')[0]
    path = path.replace('\\\\', '/').strip('"')

    path = path + '/steamapps'
    return path


def get_cn_ip():
    ips = ['58.14.0.0', '58.16.0.0', '58.24.0.0', '58.30.0.0', '58.32.0.0', '58.66.0.0', '58.68.128.0', '58.82.0.0',
           '58.87.64.0', '58.99.128.0', '58.100.0.0', '58.116.0.0', '58.128.0.0', '58.144.0.0', '58.154.0.0', '58.192.0.0',
           ]
    rnd = random.randint(0, len(ips) - 1)
    ip = ips[rnd]
    _ip = ip.split('.')
    for i, v in enumerate(_ip):
        if int(v) == 0:
            _ip[i] = str(random.randint(0, 255))
    ip = '.'.join(_ip)
    return ip


def get_value(s: str) -> Any:
    return literal_eval(s)['value']


if __name__ == '__main__':
    print(get_steam_app_path(730))
