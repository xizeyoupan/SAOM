from abc import ABCMeta, abstractmethod

from SAOM import SAOM


class AbstractHandler(metaclass=ABCMeta):
    """
    这个类名需要与文件名保持一致
    音乐处理所必须实现的接口
    """

    @abstractmethod
    def __init__(self, ctx: SAOM) -> None:
        """
        SAOM 实例会把自身作为ctx传入
        """
        self.ctx = ctx

    @abstractmethod
    async def single_song(self, search_key: str):
        pass

    @property
    @abstractmethod
    def default_config(self):
        pass

    @abstractmethod
    def get_config(self):
        pass

    def save_config(self, config: dict):
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def parse(self, line: str):
        pass
