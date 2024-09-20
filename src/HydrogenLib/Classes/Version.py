from collections.abc import Iterable


class Version:
    def __init__(self, version):
        if isinstance(version, str):
            self.version = version.strip()
            self.version = tuple(map(int, self.version.split('.')))
        elif isinstance(version, tuple):
            self.version = version
        elif isinstance(version, Iterable):
            self.version = tuple(version)
        else:
            raise ValueError('Invalid version type')

    def add(self, version):
        if not isinstance(version, tuple):
            version = tuple(version)
        self.version = tuple(map(lambda x, y: x + y, self.version, version))

    def string(self):
        return str(self)

    def __str__(self):
        return '.'.join(map(str, self.version))

    @property
    def tuple(self):
        return self.version

    @classmethod
    def from_fd(cls, fd):
        fd.seek(0)
        return cls(fd.read())

    @classmethod
    def from_file(cls, file):
        with open(file, 'r') as fd:
            return cls.from_fd(fd)

    def __iter__(self):
        return iter(self.version)

