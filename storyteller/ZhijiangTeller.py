import asyncio
from collections import deque
from difflib import SequenceMatcher
import json
import aiohttp

try:
    from storyteller.AbstractTeller import AbstractTeller
except ImportError:
    from AbstractTeller import AbstractTeller


class ZhijiangTeller(AbstractTeller):
    def __init__(self, ctx):
        self.session = aiohttp.ClientSession()
        self.ctx = ctx
        self.current_line = ''
        self.page_num = 0
        self.contents = deque()
        self.__running = ctx.teller_enable

    async def get_content(self):
        async with self.session.get(f'https://asoulcnki.asia/v1/api/ranking/?pageNum={self.page_num}&timeRangeMode=0&sortMode=0&pageSize=10') as resp:
            res = json.loads(await resp.text())

            for i in res['data']['replies']:
                content = i['content'].split('\n')

                content = filter(lambda x: x, content)
                content = deque(content)
                piece = {'author': i['m_name'], 'content': content}
                self.contents.append(piece)

    async def check(self):
        if len(self.contents) < 2:
            self.page_num += 1
            await self.get_content()

    async def start_teller(self):
        self.__running = True
        await self.check()

        self.current_line = "开始说书"
        self.ctx.set_story(self.current_line)

    def stop_teller(self):
        self.__running = False
        # asyncio.create_task(self.session.close())

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
            if not len(self.contents[0]['content']):
                self.contents.popleft()

            line = self.contents[0]['content'].popleft()
            # while len(line) < 2 or emoji.emoji_count(line) / len(line) > 0.3:
            #     if not len(self.contents[0]['content']):
            #         self.contents.popleft()
            #     await self.check()
            #     line = self.contents[0]['content'].popleft()
            self.current_line = line.strip()[:80]
            self.ctx.set_story(self.current_line)
            await self.check()

    def __del__(self):
        asyncio.create_task(self.session.close())


async def main():
    z = ZhijiangTeller(None)
    await z.start_teller()
    while True:
        a = input(z.current_line)
        await z.compare(z.current_line)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
