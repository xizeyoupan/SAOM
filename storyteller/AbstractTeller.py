from abc import ABCMeta, abstractmethod


class AbstractTeller(metaclass=ABCMeta):

    @abstractmethod
    def __init__(self, ctx) -> None:
        """
        SAOM 实例会把自身作为ctx传入
        """
        self.ctx = ctx

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
