import argparse
import logging
import os
import sys

logger = logging.getLogger(f'saom.{__name__}')
log_path = os.path.join(os.path.abspath(
    os.path.dirname(os.path.dirname(__file__))), 'saom.log')


class DefaultParser:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('pos0')
        self.parser.add_argument('pos1', nargs='+')
        # self.parser.add_argument('-m')

    def parse_line(self, line: str) -> argparse.Namespace:
        _stderr = sys.stderr
        sys.stderr = open(log_path, 'a', encoding='utf-8')
        try:
            namespace, _ = self.parser.parse_known_args(line.split())
        except SystemExit:
            logger.error(f'Statement `{line}` cause an error.')
            namespace = None
        sys.stderr.close()
        sys.stderr = _stderr
        return namespace


if __name__ == '__main__':
    dp = DefaultParser()
    r = dp.parse_line("s 红色高跟鞋 珈乐")
    print(r)
