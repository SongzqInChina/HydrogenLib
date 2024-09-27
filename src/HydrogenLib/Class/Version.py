import re
from typing import Iterable, Union

from ..Class.Base import Char


class Version:
    _version_checker = re.compile(r"^(\d+\.)+\d$")
    _number_checker = re.compile(r"^[0-9]+$")

    def _check_suffix(self, suffix):
        if suffix.lower() not in ("dev", "alpha", "beta", "rc", "post", "final", "release", None):
            raise ValueError("Invalid suffix")

    def _check_version(self, version):
        if isinstance(version, str):
            if not self._version_checker.match(version):
                raise ValueError("Invalid version")
        elif isinstance(version, Iterable):
            version = tuple(version)
            for i in version:
                if not self._number_checker.match(i):
                    raise ValueError("Invalid version")

    def _to_char_tuple(self, version):
        version = version.split('.')
        return list(map(lambda x: Char(int(x)), version))

    def __init__(self, version, suffix=None):
        self._check_version(version)
        self._check_suffix(suffix)

        self.version = self._to_char_tuple(version)
        self.suffix = suffix

    def add(self, version: Union[str, list[Char], object]):
        if isinstance(version, self.__class__):
            version = version.version  # type: list[Char]
        elif isinstance(version, list):
            version = version
        self._check_version(version)
        for i, (v1, v2) in enumerate(zip(self.version, version)):
            self.version[i] = Char(v1 + v2)
        return self

    def sub(self, version: Union[str, list[Char], object]):
        if isinstance(version, self.__class__):
            version = version.version  # type: list[Char]
        elif isinstance(version, list):
            version = version
        self._check_version(version)
        for i, (v1, v2) in enumerate(zip(self.version, version)):
            self.version[i] = Char(v1 - v2)
            if self.version[i] < 0:
                self.version[i] = Char(0)
        return self

    def __str__(self):
        return "{}.{}".format(
            '.'.join(map(lambda x: str(x), self.version)),
            self.suffix
        )
