from abc import ABCMeta, abstractmethod

from SAOM import SAOM


class DefaultGame(metaclass=ABCMeta):

    @abstractmethod
    def __init__(self, ctx: SAOM) -> None:
        self.ctx = ctx
        self.config = ...
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    async def start(self) -> None:
        pass

    @abstractmethod
    def write_status(self, s, extra=True) -> None:
        pass

    @abstractmethod
    def write_story(self, s) -> None:
        pass

    @abstractmethod
    async def trans_wav(self, song_info):
        pass
