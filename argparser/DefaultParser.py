import argparse


class DefaultAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, 's', values)


class DefaultParser:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-点歌', nargs='*', action=DefaultAction)
        self.parser.add_argument('-s', nargs='*',)
        self.parser.add_argument('-m', default='ne')

    def parse_line(self, line: str) -> argparse.Namespace:
        namespace, _ = self.parser.parse_known_args(line.split())
        return namespace


if __name__ == '__main__':
    dp = DefaultParser()
    r = dp.parse_line("-m tx -点歌 红色高跟鞋 珈乐 -g dd")
    print(r)
