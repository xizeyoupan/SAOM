import asyncio
from collections import deque
from difflib import SequenceMatcher
import os

try:
    from storyteller.AbstractTeller import AbstractTeller
except ImportError:
    from AbstractTeller import AbstractTeller
_path = os.path.dirname(os.path.realpath(__file__))


class LocalTeller(AbstractTeller):
    def __init__(self, ctx):
        self.f = open(os.path.join(_path, 'Insult.txt'), 'r', encoding='utf-8')
        self.ctx = ctx
        self.current_line = ''
        self.contents = deque()
        self.__running = ctx.teller_enable

    async def start_teller(self):
        self.__running = True

        self.current_line = "开始说书"
        self.ctx.set_story(self.current_line)

    def stop_teller(self):
        self.__running = False

    async def compare(self, line):
        if not self.__running:
            return

        if line.count('：') == 1:
            line = line.split('：')[-1]
        elif line.count('：') > 1:
            line = line[line.index('：'):].strip('：')

        r = SequenceMatcher(lambda x: x in " ", line.strip('\n'),
                            self.current_line).ratio()

        if r > 0.6:
            self.current_line = self.f.readline().strip('\n')
            self.ctx.set_story(self.current_line)

    def __del__(self):
        self.f.close()


async def main():
    z = LocalTeller(None)
    await z.start_teller()
    while True:
        a = input(z.current_line)
        await z.compare(z.current_line)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
