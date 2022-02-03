import argparse


class DefaultParser:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-s', nargs='*',)  # 单曲点歌
        self.parser.add_argument('-n', nargs='*',)  # 轻国小说展

    def parse_line(self, line: str) -> argparse.Namespace:
        try:
            namespace, _ = self.parser.parse_known_args(line.split())
        except SystemExit:
            namespace = None
        return namespace


if __name__ == '__main__':
    dp = DefaultParser()
    r = dp.parse_line(" -s 红色高跟鞋 珈乐 -g dd")
    print(r)
