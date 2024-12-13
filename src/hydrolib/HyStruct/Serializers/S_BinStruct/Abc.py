from typing import Protocol, Self, Union, runtime_checkable


@runtime_checkable
class Packable_CLS_NO_ARG(Protocol):
    def pack(self, ins) -> bytes:
        ...


@runtime_checkable
class Packable_INS_NO_ARG(Protocol):
    def pack(self) -> bytes:
        ...


@runtime_checkable
class Packable_CLS_WITH_ARG(Protocol):
    @classmethod
    def pack(cls, ins, *args, **kwargs) -> bytes:
        ...


@runtime_checkable
class Packable_INS_WITH_ARG(Protocol):
    def pack(self, *args, **kwargs) -> bytes:
        ...


@runtime_checkable
class Unpackable_CLS_NO_ARG(Protocol):
    @classmethod
    def unpack(cls, data: bytes) -> 'Self':
        ...


@runtime_checkable
class Unpackable_CLS_WITH_ARG(Protocol):
    @classmethod
    def unpack(cls, data: bytes, *args, **kwargs) -> 'Self':
        ...


@runtime_checkable
class Unpackable_INS_NO_ARG(Protocol):
    def unpack(self, data: bytes) -> 'Self':
        ...


@runtime_checkable
class Unpackable_INS_WITH_ARG(Protocol):
    def unpack(self, data: bytes, *args, **kwargs) -> 'Self':
        ...


PackableNoArg = Union[Packable_CLS_NO_ARG, Packable_INS_NO_ARG]
PackableWithArg = Union[Packable_CLS_WITH_ARG, Packable_INS_WITH_ARG]
Packable = Union[PackableNoArg, PackableWithArg]

UnpackableNoArg = Union[Unpackable_CLS_NO_ARG, Unpackable_INS_NO_ARG]
UnpackableWithArg = Union[Unpackable_CLS_WITH_ARG, Unpackable_INS_WITH_ARG]
Unpackable = Union[UnpackableNoArg, UnpackableWithArg]
