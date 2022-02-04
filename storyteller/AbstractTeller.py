from abc import ABCMeta, abstractmethod

from SAOM import SAOM


class AbstractTeller(metaclass=ABCMeta):

    @abstractmethod
    def __init__(self, ctx: SAOM) -> None:
        """
        SAOM 实例会把自身作为ctx传入
        """
        self.ctx = ctx

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
    async def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def compare(self, line: str):
        pass

    @abstractmethod
    def parse(self, line: str):
        pass
