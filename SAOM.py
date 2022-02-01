import asyncio
import importlib
import json
import configparser
import os
from io import BytesIO


from argparser.DefaultParser import DefaultParser

DB_PATH = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), 'content\songs.json')
CONTENT_PATH = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), 'content')
CONFIG_PATH = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), 'config.ini')


class SAOM:
    def __init__(self):
        self.parser = DefaultParser()
        self.config = configparser.ConfigParser()

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
    ...

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
