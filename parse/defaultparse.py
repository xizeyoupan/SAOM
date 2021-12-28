import argparse
import asyncio


class DefaultAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if 'ctx' in kwargs:
            self.ctx = kwargs['ctx']
            del kwargs['ctx']
        super().__init__(option_strings, dest, nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        if self.dest in ['点歌', 's']:
            setattr(namespace, 's', values)
            asyncio.create_task(self.ctx.ordersong(namespace))
        else:
            setattr(namespace, self.dest, values)

        print(self.dest)

class DefaultParser:
    def __init__(self, ctx) -> None:
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument(
            '-点歌', nargs='*', action=DefaultAction, ctx=ctx)
        self.parser.add_argument(
            '-s', nargs='*', action=DefaultAction, ctx=ctx)
        self.parser.add_argument(
            '-m', default='ne', action=DefaultAction, ctx=ctx)

    def parse_line(self, line: str) -> argparse.Namespace:
        return self.parser.parse_args(line.split(' '))


if __name__ == '__main__':
    import sys
    import os
    sys.path.append(os.path.dirname(
        os.path.dirname(os.path.realpath(__file__))))
    import SAOM
    dp = DefaultParser(SAOM.SAOM())
    r = dp.parse_line("-m tx -s 红色高跟鞋 珈乐")
    print(r)
