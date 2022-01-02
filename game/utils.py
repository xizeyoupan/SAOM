import os
import winreg
import re


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


def get_steam_app_path(id: int) -> str:
    vdf_path = get_steam_path() + '\\steamapps\\libraryfolders.vdf'

    with open(vdf_path, 'r') as f:
        data = "".join(f.read().split('\n'))

    pattern = r'"path".*([a-zA-Z]:.*)"{}"'.format(id)
    data = re.findall(pattern, data)[-1]
    path: str = data.split('\t\t')[0]
    path = path.replace('\\\\', '/').strip('"')

    path = path + '/steamapps'
    return path


if __name__ == '__main__':
    print(get_steam_app_path(730))
