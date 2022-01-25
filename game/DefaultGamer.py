from abc import ABCMeta, abstractmethod


class DefaultGamer(metaclass=ABCMeta):

    @abstractmethod
    def __init__(self, ctx) -> None:
        self.ctx = ctx
        pass

    @abstractmethod
    def stop_watch(self) -> None:
        pass

    @abstractmethod
    async def start_watch(self) -> None:
        pass

    @abstractmethod
    def write_status(self):
        pass

    @abstractmethod
    def write_story(self):
        pass

    @abstractmethod
    def trans_wav(self, song_info):
        pass

    @abstractmethod
    def did_call_shell(self, extra):
        pass
