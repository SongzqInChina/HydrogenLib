from abc import ABC, abstractmethod
from typing import final


class Serializer(ABC):
    @abstractmethod
    def dumps(self, data):
        ...

    @abstractmethod
    def loads(self, data):
        ...

    def load_from_sock(self, sock):
        ...

    @final
    def socket_support(self) -> bool:
        return (
                Serializer.load_from_sock is not self.load_from_sock
        )
