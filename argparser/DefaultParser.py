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
            self.ctx.order_song(namespace)
        else:
            setattr(namespace, self.dest, values)


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
        args = line.split()
        end_args = []
        flag = False
        for i in args:
            if i.startswith('-'):
                if i in ('-s', '-点歌'):
                    end_args.append(i)
                    flag = True
                else:
                    flag = False
            else:
                if flag:
                    end_args.append(i)

        args = list(filter(lambda x: x not in end_args, args))
        args.extend(end_args)

        return self.parser.parse_args(args)


if __name__ == '__main__':
    import sys
    import os
    sys.path.append(os.path.dirname(
        os.path.dirname(os.path.realpath(__file__))))
    import SAOM
    dp = DefaultParser(SAOM.SAOM())
    r = dp.parse_line("-m tx -s 红色高跟鞋 珈乐")
    print(r)
