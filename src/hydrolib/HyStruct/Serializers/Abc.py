from abc import ABC, abstractmethod
from typing import final
from typing import Any


class Serializer(ABC):
    @abstractmethod
    def dumps(self, data) -> bytes:
        ...

    @abstractmethod
    def loads(self, data) -> Any:
        ...

    def load_from_sock(self, sock):
        ...

    @final
    def socket_support(self) -> bool:
        return (
                Serializer.load_from_sock is not self.load_from_sock
        )
