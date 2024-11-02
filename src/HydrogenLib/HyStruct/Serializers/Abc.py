from abc import ABC, abstractmethod


class Serializer(ABC):
    @abstractmethod
    def dump(self, data):
        ...

    @abstractmethod
    def load(self, data):
        ...

    @abstractmethod
    def load_from_sock(self, sock):
        ...

