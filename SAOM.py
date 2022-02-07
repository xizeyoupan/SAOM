import asyncio
import configparser
import importlib
import os

from argparser.DefaultParser import DefaultParser

DB_PATH = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), 'content/songs.json')
CONTENT_PATH = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), 'content')
CONFIG_PATH = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), 'config.ini')


class SAOM:
    def __init__(self):
        self.parser = DefaultParser()
        self.config = configparser.ConfigParser()
        self.game = None
        self.handler = None
        self.storyteller = None

    @classmethod
    def init_config(cls):
        config_path = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), 'config.ini')
        if os.path.exists(config_path):
            return

        for i in ('game', 'handler', 'storyteller'):
            with os.scandir(os.path.join(os.path.dirname(os.path.realpath(__file__)), i)) as it:
                for entry in it:
                    if entry.is_file() and entry.name != '__init__.py' \
                            and entry.name.lower().endswith('.py') and 'Abstract' not in entry.name:
                        _name = entry.name.split(".")[0]
                        module = importlib.import_module(f'{i}.{_name}')
                        _class = getattr(module, _name)
                        _class.save_config(_class.default_config)

    def set_game(self, section_name: str):
        module = importlib.import_module(section_name)
        self.game = getattr(module, section_name.split('.')[-1])(self)

    def set_handler(self, section_name: str):
        module = importlib.import_module(section_name)
        self.handler = getattr(module, section_name.split('.')[-1])(self)

    def set_storyteller(self, section_name: str):
        module = importlib.import_module(section_name)
        self.storyteller = getattr(module, section_name.split('.')[-1])(self)

    def start(self, game: str, handler: str, storyteller: str):
        self.set_storyteller(storyteller)
        self.set_handler(handler)
        self.set_game(game)

    def stop(self):
        self.game.stop()
        self.handler.stop()
        self.storyteller.stop()


async def main():
    SAOM.init_config()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # loop.create_task()
    loop.run_until_complete(main())
