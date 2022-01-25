from abc import ABCMeta, abstractmethod


class AbstractTeller(metaclass=ABCMeta):

    @abstractmethod
    def __init__(self, ctx) -> None:
        """
        SAOM 实例会把自身作为ctx传入
        """
        self.ctx = ctx

    @abstractmethod
    def start_teller(self):
        pass

    @abstractmethod
    def stop_teller(self):
        pass

    @abstractmethod
    def compare(self, line: str):
        pass
