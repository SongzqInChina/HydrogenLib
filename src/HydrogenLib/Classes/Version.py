import re
from typing import Iterable
from ..Classes.Base import Char


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
        return tuple(map(lambda x: Char(int(x)), version))

    def __init__(self, version, suffix=None):
        self._check_version(version)
        self._check_suffix(suffix)

        self.version = self._to_char_tuple(version)
        self.suffix = suffix

    def add(self, version):
        if isinstance(version, self.__class__):
            version = version.version  # type: tuple[Char, ...]
        self._check_version(version)


