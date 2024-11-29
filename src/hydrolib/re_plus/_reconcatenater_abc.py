from abc import ABC, abstractmethod


class REConcater(ABC):
    @classmethod
    @abstractmethod
    def concat(cls) -> str: ...
    @abstractmethod
    def pattern(self) -> str: ...

    @abstractmethod
    def __add__(self, other): ...

    @abstractmethod
    def __mul__(self, other): ...

    @abstractmethod
    def __or__(self, other): ...


class BaseREConcateratable(ABC):
    name = None
    ignore = False
    origin_pattern = None

    @abstractmethod
    def pattern(self) -> str: ...
    @abstractmethod
    def origin(self) -> str: ...

    def findall(self, string): ...

    def finditer(self, string): ...

    def match(self, string): ...
